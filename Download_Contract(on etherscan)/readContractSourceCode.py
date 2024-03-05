# -*- coding: UTF-8 -*-

import pandas as pd
import requests
import time
import os
from utils.regulate_source_code import find_single_solname_in_phrase, multi_sol_div, multi_sol_concat, multi_sol_fix, regulate_code_import, main_regulate_source_code

Net = ""
while Net == "":
    val = input("请输入/重新输入 Network，选择如下： Mainnet / Goerli / Sepolia:\n")
    if val == "Mainnet" or val == "Goerli" or val == "Sepolia":
        Net = str(val)
    else:
        continue



df = pd.read_csv('./data/export-verified-contractaddress-opensource-license({}).csv'.format(Net))   # 需要手动删除csv第一行
# df = pd.read_csv('./data/export-verified-contractaddress-opensource-license({}).csv'.format(Net), header=None)
# df.columns = ['Txhash','ContractAddress','ContractName']
# 对应网络所有合约地址 ， 共5k条

N = len(df)
# N = 1000

last_N = df[-N:].copy()
# 后1000条

YourApiKeyToken="FQXNEMBZ59ZG95A6KKXNUIWESBUWTBT82F"
# 查看my API key：https://etherscan.io/myapikey，输入

'''
    1. getSourceCode , regulate source code
'''

module = "contract"
action = "getsourcecode"
contract_address_list = last_N["ContractAddress"]
contract_names = last_N["ContractName"]
# param

crtid=0
timecost = []
costsum = 0

for (contract_address,name) in zip(contract_address_list, contract_names):
    t0=time.time()
    if Net == "Mainnet":
        url = ('https://api.etherscan.io/api'+
           '?module={}'+
           '&action={}'+
           '&address={}'+
           '&apikey={}').format(module, action, contract_address, YourApiKeyToken)
    elif Net == "Goerli":
        url = ('https://api-goerli.etherscan.io/api' +
               '?module={}' +
               '&action={}' +
               '&address={}' +
               '&apikey={}').format(module, action, contract_address, YourApiKeyToken)
    else:
        url = ('https://api-sepolia.etherscan.io/api'+
               '?module={}' +
               '&action={}' +
               '&address={}' +
               '&apikey={}').format(module, action, contract_address, YourApiKeyToken)

    response = requests.get(url=url)
    # 通过params传参

    t1=time.time()
    print("读取以及输出本contract Source Code(时间s)：{}".format(t1-t0))
    timecost.append(t1-t0)
    costsum = costsum + t1-t0
    # 记录时间
    crtid =crtid + 1

    '''
    print(type(response)) <class 'requests.models.Response'>
    print(response.status_code)		# 打印状态码 200
    print(response.text)		# 获取响应内容
    '''

    content = response.text.encode(response.encoding).decode('utf-8')  #去除unicode乱码
    try:
        text_dict=eval(content)
        # 响应内容-字符串转换为字典
        source_code_list=text_dict["result"]

        ###
        ### 1、输出rawcode
        ###
        path = "./sourcecode_{}/rawcode".format(Net)
        if not os.path.exists(path):
            os.makedirs(path)
        rawcodewritter = open("./sourcecode_{}/rawcode/{}({}).txt".format(Net, name, contract_address), "w", encoding="utf-8")
        print(source_code_list, file=rawcodewritter)
        rawcodewritter.close()

        purecode = ""
        print("\n\n【contract NO.{}】".format(crtid))
        for ele in source_code_list:
            print("contract name: {}({})".format(name,contract_address))
            piece_of_code=ele["SourceCode"]
            purecode = purecode + piece_of_code
        ###
        ### 2、输出出去以后的.sol代码合集
        ###
        path = "./sourcecode_{}/purecode".format(Net)
        if not os.path.exists(path):
            os.makedirs(path)
        writter2 = open("./sourcecode_{}/purecode/{}({}).txt".format(Net, name,contract_address),"w", encoding="utf-8")
        print(purecode, file=writter2)
        writter2.close()

        ###
        ### 3、整合并且输出本地目录可以编译的code，没有内部引用。同时生成multisol_div文件夹存放子文件
        ###
        source_code = main_regulate_source_code(purecode, name, contract_address, Net)
        path = "./sourcecode_{}/finalcode".format(Net)
        if not os.path.exists(path):
            os.makedirs(path)
        writter3 = open("./sourcecode_{}/finalcode/{}({}).txt".format(Net, name,contract_address),"w", encoding="utf-8")
        print(source_code, file=writter3)
        writter3.close()
    except Exception as e:
        print("Reason: ",e)
    print("【累计用时 {}/{}】：{}s".format(crtid, N, costsum))

print("【总用时】：{}".format(costsum))

pd.DataFrame(columns=["timecost"],data=timecost).to_csv("./sourcecode({})_readingtime.csv".format(Net),encoding="utf-8")

halt = input("HALT")

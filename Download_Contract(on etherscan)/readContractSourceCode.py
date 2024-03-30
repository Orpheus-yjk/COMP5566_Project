# -*- coding: UTF-8 -*-

import pandas as pd
import requests
import time
import os
from utils.regulate_source_code import main_regulate_source_code
from utils.plus import reorganize

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

delta = 0
last_N = df[-N+delta:].copy()
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

    content = response.text.encode(response.encoding).decode('utf-8')  # 格式化unicode，去除unicode乱码


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

        ###
        ### 2、输出出去以后的.sol代码合集
        ###
        path = "./sourcecode_{}/purecode".format(Net)
        if not os.path.exists(path):
            os.makedirs(path)
        purecode = ""
        print("\n\n【contract NO.{}】".format(crtid+delta))
        for ele in source_code_list:
            print("contract name: {}({})".format(name,contract_address))
            piece_of_code=ele["SourceCode"]

            # remove \n & \r & \"
            while piece_of_code.find("\\n") != -1:
                piece_of_code = piece_of_code.replace("\\n", "\n")
            while piece_of_code.find("\\r") != -1:
                piece_of_code = piece_of_code.replace("\\r", "\r")
            while piece_of_code.find("\\\"") != -1:
                piece_of_code = piece_of_code.replace("\\\"", "\"")
            # remove unicode & 非ascii乱码
            piece_of_code = piece_of_code.replace("unicode", " ")

            tmp = piece_of_code
            piece_of_code = ""
            import random
            for j in range(0,len(tmp)):
                if ord(tmp[j])<0 or ord(tmp[j])>127:
                    coin = random.randint(1, 2)
                    if coin==1: #大写
                        piece_of_code= piece_of_code + chr(random.randint(65, 90))
                    else: # 小写
                        piece_of_code= piece_of_code + chr(random.randint(97, 122))
                else:
                    piece_of_code = piece_of_code + tmp[j]

            # while piece_of_code.find("unicode\"") != -1:
            #     idx = piece_of_code.find("unicode\"")
            #     idx2 = idx + len("unicode\"")
            #     while piece_of_code[idx2] != '\"':
            #         idx2 = idx2 + 1
            #     str0 = piece_of_code[idx:idx2 + 1]
            #     import random
            #     import string
            #     value = ''.join(random.sample(string.ascii_letters + string.digits, idx2 + 1 - idx))  # 随机字符串
            #     piece_of_code = piece_of_code.replace(str0, value)

            purecode = purecode + piece_of_code
        purecodewritter = open("./sourcecode_{}/purecode/{}({}).txt".format(Net, name,contract_address),"w", encoding="utf-8")
        print(purecode, file=purecodewritter)
        purecodewritter.close()

        ###
        ### 3、整合并且输出本地目录可以编译的code，没有内部引用。同时生成multisol_div文件夹存放子文件
        ###
        path = "./sourcecode_{}/finalcode".format(Net)
        if not os.path.exists(path):
            os.makedirs(path)

        source_code_header, source_code= main_regulate_source_code(purecode, name, contract_address, Net)
        # 1. remove ^ in pragma solidity ^
        # 2. comcat all.sol files
        # 3.find compile version
        # 4.find SPDX version
        # final regulation. reorganize code --> content_dict.
        # add SPDX, compile version, and import; adding contract addr !

        ##################################################################

        # Fix bug
        # 还是存在contract/library乱序的问题，所以写一个re-organize: 抓取内容，重组代码

        ##################################################################

        newcode, content_dict, dependency, typology, codewithdoc, withdoc_content_dict = reorganize(source_code)
        while newcode.find("\n\n\n") != -1:
            newcode = newcode.replace("\n\n\n", "\n\n")
        while codewithdoc.find("\n\n\n") != -1:
            codewithdoc = codewithdoc.replace("\n\n\n", "\n\n")
        # leave out blank line

        source_code = source_code_header + newcode
        sourcecodewritter = open("./sourcecode_{}/finalcode/{}({}).txt".format(Net, name,contract_address),"w", encoding="utf-8")
        print(source_code, file=sourcecodewritter)
        sourcecodewritter.close()

        path = "./sourcecode_{}/CodewithDocs".format(Net)   ## 记录被省略的文档信息
        if not os.path.exists(path):
            os.makedirs(path)
        source_code = source_code_header + codewithdoc
        sourcecodewritter = open("./sourcecode_{}/CodewithDocs/{}({}).txt".format(Net, name,contract_address),"w", encoding="utf-8")
        print(source_code, file=sourcecodewritter)
        sourcecodewritter.close()

        # if name=="ChainFactory_ERC20":
        #     print(dependency)
        #     print(typology)
        #     exit(0)
    except Exception as e:
        print("Reason: ",e)
    print("【累计用时 {}/{}】：{}s".format(crtid, N, costsum))

print("【总用时】：{}".format(costsum))

pd.DataFrame(columns=["timecost"],data=timecost).to_csv("./sourcecode({})_readingtime.csv".format(Net),encoding="utf-8")

halt = input("HALT")

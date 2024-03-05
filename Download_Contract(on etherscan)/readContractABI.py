# -*- coding: UTF-8 -*-

import pandas as pd
import requests
import time
import os
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
    2. getABI
'''

module = "contract"
action = "getabi"
contract_address_list = last_N["ContractAddress"]
contract_names = last_N["ContractName"]
# param

crtid=0
timecost = []
costsum = 0

for (contract_address,name) in zip(contract_address_list, contract_names):
    t0 = time.time()
    if Net == "Mainnet":
        url = ('https://api.etherscan.io/api' +
               '?module={}' +
               '&action={}' +
               '&address={}' +
               '&apikey={}').format(module, action, contract_address, YourApiKeyToken)
    elif Net == "Goerli":
        url = ('https://api-goerli.etherscan.io/api' +
               '?module={}' +
               '&action={}' +
               '&address={}' +
               '&apikey={}').format(module, action, contract_address, YourApiKeyToken)
    else:
        url = ('https://api-sepolia.etherscan.io/api' +
               '?module={}' +
               '&action={}' +
               '&address={}' +
               '&apikey={}').format(module, action, contract_address, YourApiKeyToken)

    response = requests.get(url=url)
    # 通过params传参

    '''
    print(type(response)) <class 'requests.models.Response'>
    print(response.status_code)		# 打印状态码 200
    print(response.text)		# 获取响应内容
    '''

    content = response.text.encode(response.encoding).decode('utf-8')  # 去除unicode乱码
    try:
        text_dict=eval(content)
        # 响应内容-字符串转换为字典
        ABI_list=text_dict["result"]
        print("\n\n【contract NO.{}】{}".format(crtid,name))
        path = "./ABI_{}/".format(Net)
        if not os.path.exists(path):
            os.makedirs(path)
        data = open("./ABI_{}/{}({}).txt".format(Net,name,contract_address), 'w', encoding='utf-8')
        print(str(text_dict["result"]), file=data)
        data.close()

        t1=time.time()
        print("读取以及输出本contract ABI花费了：{}s".format(t1-t0))
        timecost.append(t1-t0)
        costsum = costsum + t1-t0
        # 记录时间
        crtid =crtid + 1
    except Exception as e:
        print(e)
    print("【累计用时 {}/{}】：{}s".format(crtid, N, costsum))

print("【总用时】：{}".format(costsum))

pd.DataFrame(columns=["timecost"],data=timecost).to_csv("./ABI({})_readingtime.csv".format(Net),encoding="utf-8")

halt = input("HALT")

# -*- coding: UTF-8 -*-

import pandas as pd
import requests
import time
# 通过url直接加上请求参数，与通过params传参效果是一样的

df = pd.read_csv('export-verified-contractaddress-opensource-license.csv')
# 所有合约地址

N = 1000

last_N = df[-N:].copy()
# 前1000条

YourApiKeyToken="FQXNEMBZ59ZG95A6KKXNUIWESBUWTBT82F"
# my API key

'''
    2. getSourceCode
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
    t0=time.time()
    response = requests.get(url=('https://api.etherscan.io/api'+\
       '?module={}'+\
       '&action={}'+\
       '&address={}'+\
       '&apikey={}').format(module, action, contract_address, YourApiKeyToken))
    # 通过params传参

    '''
    print(type(response)) <class 'requests.models.Response'>
    print(response.status_code)		# 打印状态码 200
    print(response.text)		# 获取响应内容
    '''

    text_dict=eval(response.text)
    # 响应内容-字符串转换为字典
    ABI_list=text_dict["result"]
    print("\n\n【contract NO.】：{} ".format(crtid))
    print(str(text_dict["result"]))
    data = open("./ABI/{}.txt".format(name), 'w', encoding='utf-8')
    print(str(text_dict["result"]), file=data)
    data.close()

    t1=time.time()
    print("读取以及输出本条约花费了(时间s)：{}".format(t1-t0))
    timecost.append(t1-t0)
    costsum = costsum + t1-t0
    # 记录时间
    crtid =crtid + 1
    if crtid % 50 ==0 :
        print("【总用时】：{}".format(costsum))

print("【总用时】：{}".format(costsum))

pd.DataFrame(columns=["timecost"],data=timecost).to_csv("./ABI_readingtime.csv",encoding="utf-8")



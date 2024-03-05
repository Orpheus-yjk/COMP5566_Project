# -*- coding: UTF-8 -*-

import pandas as pd
import requests
import time
from solcx import compile_standard, install_solc



df = pd.read_csv('export-verified-contractaddress-opensource-license.csv')
# 所有合约地址

start = 0

N = 1000 - start

last_N = df[-N:].copy()
# 前1000条

YourApiKeyToken="FQXNEMBZ59ZG95A6KKXNUIWESBUWTBT82F"
# my API key

'''
    getSourceCode --> bytecode / abi
'''

module = "contract"
action = "getsourcecode"
contract_address_list = last_N["ContractAddress"]
contract_names = last_N["ContractName"]
# param

crtid = start
# add=0
timecost = []
costsum = 0
difficult_sol = []
for (contract_address,name) in zip(contract_address_list, contract_names):
    t0=time.time()
    response = requests.get(url=('https://api.etherscan.io/api'+\
       '?module={}'+\
       '&action={}'+\
       '&address={}'+\
       '&apikey={}').format(module, action, contract_address, YourApiKeyToken))
    # 通过params传参

    text_dict=eval(response.text)
    # 响应内容-字符串转换为字典
    source_code_list=text_dict["result"]
    print("\n\n【contract NO.】：{} ".format(crtid))
    for ele in source_code_list:
        print("contract name: {}".format(name))
        # print("source code:{}".format(ele))
        source_code=ele["SourceCode"].replace("\\n","\n")
        source_code=source_code.replace("\\r","\r")

        '''
        Compile
        '''
        from web3 import Web3
        w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))

        beg = source_code.find("pragma solidity ")
        compile_version = source_code[beg + 16 :
                                       source_code.find(";", beg, len(source_code))]
        while compile_version[0]<'0' or compile_version[0]>'9': compile_version = compile_version[1:]
        while compile_version[-1]<'0' or compile_version[-1]>'9': compile_version = compile_version[:-1]
        print("compile version == {}".format(compile_version))
        # pragma solidity 0.x.y; find compile version

        # compile code to bytecode
        try:
            install_solc(compile_version)
            compiled_sol = compile_standard(
                {
                    "language": "Solidity",
                    "sources": {"{}.sol".format(name): {"content": source_code}},
                    "settings": {
                        "outputSelection": {
                            "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
                        }
                    },
                },
                solc_version=compile_version,
            )
            # print("bytecode: "+compiled_sol["contracts"]["{}.sol".format(name)][name]["evm"][
            #         "bytecode"
            #     ]["object"])
            # output bytecode
            bytecode = compiled_sol["contracts"]["{}.sol".format(name)][name]["evm"][
                    "bytecode"
                ]["object"]
            data = open("./bytecode/{}.txt".format(name), 'w', encoding='utf-8')
            print(str(bytecode), file=data)
            data.close()
        except Exception as e:
            print("\033[31mFAIL!!\033[0m")
            # 这是红色字体
            difficult_sol.append(name)
            data = open("./difficult/{}.txt".format(name), 'w', encoding='utf-8')
            print(source_code, file=data)
            data.close()
            # print('Reason:', e)
        # get abi
        # abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

    t1=time.time()
    print("\033[34m读取以及输出本条约花费了(时间s)：{}\033[0m".format(t1-t0))
    # 这是蓝色字体
    timecost.append(t1-t0)
    costsum = costsum + t1-t0
    # 记录时间
    crtid =crtid + 1
    if crtid % 50 ==0 :
        print("【总用时】：{}".format(costsum))

print("【总用时】：{}".format(costsum))

data = open("./difficulty_backups.txt", 'w', encoding='utf-8')
print(str(difficult_sol), file=data)
data.close()

pd.DataFrame(columns=["difficult .sol"],data=difficult_sol).to_csv("./difficult_sol.csv",encoding="utf-8")



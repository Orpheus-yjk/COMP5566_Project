# -*- coding: UTF-8 -*-

import pandas as pd
import time
import os
from solcx import compile_standard, install_solc

def getfiles(dir):
    filenames=os.listdir(dir)
    return filenames


crtid = 0
timecost = []
costsum = 0
failed_sol = []

if not os.path.exists("./compiled_bytecode"):
    os.makedirs("./compiled_bytecode")

if not os.path.exists("./successfully_compile"):
    os.makedirs("./successfully_compile")

if not os.path.exists("./fail_to_compile"):
    os.makedirs("./fail_to_compile")

if not os.path.exists("./fail_to_compile/compile_error_log"):
    os.makedirs("./fail_to_compile/compile_error_log")

oldlist = getfiles('./fail_to_compile/') + getfiles('./successfully_compile/')

tmp = getfiles("./")
CodePath = ""
for ele in tmp:
    if len(tmp)>len("sourcecode_"):
        if ele[:len("sourcecode")] == "sourcecode":
            CodePath = "./"+ele #+"/finalcode/"

while True:
    print(CodePath)
    sourcecodelist = getfiles(CodePath+"/finalcode/")
    if len(sourcecodelist) - len(oldlist) == 0: break # over
    print("New Generation: LEN= ", len(sourcecodelist) - len(oldlist))
    for Name in sourcecodelist:
        if Name in oldlist: continue
        else: oldlist.append(Name)
        if Name.find(".") == -1: continue
        # not a file, either .txt or .sol; it is a folder
        name = Name[:-4]
        t0 = time.time()
        print("\n\n【contract NO.】：{} ".format(crtid))
        print("Contract Name: {}".format(name))

        print("Name = ", Name)

        with open(CodePath+"/finalcode/"+Name, "r",encoding='utf-8') as f:  # 打开文件
            data = f.read()  # 读取文件
            source_code = str(data)
            try:
                source_code = source_code.encode('utf-8').decode('unicode_escape')
                # source_code = source_code.replace("\\u003c", "<")
                # source_code = source_code.replace("\\u003e", ">")
                # source_code = source_code.replace("\\u0026", "&")
                # source_code = source_code.replace("\\u0027", "\'")
            # remove \u00X
            except Exception as e:
                print(e)

            source_code = source_code.replace("\\n", "\n")
            source_code = source_code.replace("\\r", "\r")
            source_code = source_code.replace("\\\"", "\"")
            # remove \n & \r & \"

        '''
        Compile
        '''
        from web3 import Web3
        w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:8545"))

        beg = source_code.find("pragma solidity ")
        if beg == -1:   # 没有compile version
            print("FAIL!!")
            failed_sol.append(name)
            data = open("./fail_to_compile/{}".format(Name), 'w', encoding='utf-8')
            print(source_code, file=data)
            data.close()
            data = open("./fail_to_compile/compile_error_log/{}".format(Name), 'w', encoding='utf-8')
            print("No Content", file=data)
            data.close()
            continue
        
        compile_version = source_code[beg + 16 : source_code.find(";", beg, len(source_code))]
        while compile_version[0]<'0' or compile_version[0]>'9': compile_version = compile_version[1:]
        while compile_version[-1]<'0' or compile_version[-1]>'9': compile_version = compile_version[:-1]
        print("compile version == {}".format(compile_version))
        # pragma solidity 0.x.y; find compile version

        # compile code to bytecode
        if os.path.exists(CodePath+"/multisol_div/{}".format(name)):
            paths = ["./utils/node_modules",CodePath+"/multisol_div/{}".format(name)]
            # 有本地文件
        else:
            paths = ["./utils/node_modules"]
        shortname = name[:name.find("(")]   # shortname is used instead of name " xxxx(0x...)" to prevent compile error
        try:
            install_solc(compile_version)
            compiled_sol = compile_standard(
                {
                    "language": "Solidity",
                    "sources": {"{}.sol".format(shortname): {"content": source_code}},
                    "settings": {
                        "outputSelection": {
                            "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
                        }
                    },
                },
                solc_version=compile_version,
                allow_paths = paths
            )
            bytecode = compiled_sol["contracts"]["{}.sol".format(shortname)][shortname]["evm"][
                    "bytecode"
                ]["object"]
            data = open("./compiled_bytecode/{}".format(Name), 'w', encoding='utf-8')
            print(str(bytecode), file=data)
            data.close()
            data2 = open("./successfully_compile/{}".format(Name), 'w', encoding='utf-8')
            print(source_code, file=data2)
            data2.close()
        except Exception as e:
            print("FAIL!!")
            failed_sol.append(name)
            data = open("./fail_to_compile/{}".format(Name), 'w', encoding='utf-8')
            print(source_code, file=data)
            data.close()
            data = open("./fail_to_compile/compile_error_log/{}".format(Name), 'w', encoding='utf-8')
            print(e, file=data)
            data.close()

        # get abi
        # abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

        t1=time.time()
        print("编译以及输出本Contract Bytecode花费了(时间s)：{}".format(t1-t0))
        timecost.append(t1-t0)
        costsum = costsum + t1-t0
        # 记录时间
        crtid =crtid + 1
        if crtid % 50 ==0 :
            print("【1 - {} 累计用时】：{}".format(crtid,costsum))

    print("【总用时】：{}".format(costsum))

    data = open("./fail_backups.txt", 'w', encoding='utf-8')
    print(str(failed_sol), file=data)
    data.close()

    pd.DataFrame(columns=["Compiled failed sol"],data=failed_sol).to_csv("./failed_sol.csv",encoding="utf-8")

    print("\n【WAITING 100s】............\n\n")
    time.sleep(100)

halt = input("HALT")

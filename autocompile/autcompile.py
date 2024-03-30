# -*- coding: UTF-8 -*-

import pandas as pd
import time
import os
from solcx import compile_standard, install_solc
from util import reorganize


def getfiles(dir):
    filenames = os.listdir(dir)
    return filenames

if not os.path.exists("./compile_result/compiled_bytecode"):
    os.makedirs("./compile_result/compiled_bytecode")

if not os.path.exists("./compile_result/compiled_bytecode_abi"):
    os.makedirs("./compile_result/compiled_bytecode_abi")

if not os.path.exists("./compile_result/successfully_compile"):
    os.makedirs("./compile_result/successfully_compile")

if not os.path.exists("./compile_result/fail_to_compile"):
    os.makedirs("./compile_result/fail_to_compile")

if not os.path.exists("./compile_result/fail_to_compile/compile_error_log"):
    os.makedirs("./compile_result/fail_to_compile/compile_error_log")

# 到2022.01.27为止，solidity最新的版本为0.8.11
# 获取solidity v0.4.0之后所有的版本号

all_compile_version=[]
for ver in open("./allcompileversion.txt"):
    all_compile_version.append(ver[:-1]) #去掉换行符

crtid = 0
timecost = []
costsum = 0
failed_sol = []

tmp = getfiles("./")
CodePath = "./sourcecode"
print(CodePath)
sourcecodelist = getfiles(CodePath)
print("Number of the .sol files: ", len(sourcecodelist))


for Name in sourcecodelist:
    if Name.find(".") == -1: continue
    # not a file, either .txt or .sol; it is a folder
    name = Name[:Name.find(".")]
    t0 = time.time()

    print("\n\n【contract NO.】：{} ".format(crtid))
    print("Contract Name: {}".format(name))

    with open(CodePath + "/" + Name, "r", encoding='utf-8') as f:  # 打开文件
        data = f.read()  # 读取文件
        source_code = str(data)
        try:
            source_code = source_code.encode('utf-8').decode('unicode_escape')
        except Exception as e:
            print(e)

        source_code = source_code.replace("\\n", "\n")
        source_code = source_code.replace("\\r", "\r")
        source_code = source_code.replace("\\\"", "\"")
        # remove \n & \r & \"

    source_code, filename = reorganize(source_code)
    print("Sub Name: {}".format(filename))
    '''
    Compile
    '''
    from web3 import Web3

    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:8545"))

    beg = source_code.find("pragma solidity ")
    if beg == -1:  # 没有compile version
        compile_version = "0.4.22" # default
        source_code = "pragma solidity ^" + compile_version + ";\n\n" + source_code
    else:
        compile_version = source_code[beg + 16: source_code.find(";", beg, len(source_code))]
        while compile_version[0] < '0' or compile_version[0] > '9': compile_version = compile_version[1:]
        while compile_version[-1] < '0' or compile_version[-1] > '9': compile_version = compile_version[:-1]

        if compile_version.find("=")!=-1:   # >= > <
            idx = compile_version.find("=")+1
            sub = ""
            while (compile_version[idx]>="0" and compile_version[idx]<="9") or compile_version[idx]==".":
                sub = sub+compile_version[idx]
                idx = idx + 1
            source_code = source_code.replace("pragma solidity ^" + compile_version, "pragma solidity ^" + sub)
            compile_version = sub

        elif compile_version.find(">")!=-1:
            idx = compile_version.find(">") + 1
            sub = ""
            while (compile_version[idx] >= "0" and compile_version[idx] <= "9") or compile_version[idx] == ".":
                sub = sub + compile_version[idx]
                idx = idx + 1
            for j in range(0,len(all_compile_version)):
                if sub == all_compile_version[j]:
                    compile_version = all_compile_version[j+1]
                    break
            source_code = source_code.replace("pragma solidity ^" + compile_version, "pragma solidity ^" + sub)
            compile_version = sub
        elif compile_version.find(">")!=-1:
            idx = compile_version.find("<") + 1
            sub = ""
            while (compile_version[idx] >= "0" and compile_version[idx] <= "9") or compile_version[idx] == ".":
                sub = sub + compile_version[idx]
                idx = idx + 1
            for j in range(0,len(all_compile_version)):
                if sub == all_compile_version[j]:
                    compile_version = all_compile_version[j-1]
                    break
            source_code = source_code.replace("pragma solidity ^" + compile_version, "pragma solidity ^" + sub)
            compile_version = sub

        for j in range(0,len(all_compile_version)):
            if all_compile_version[j]=="0.4.20": # 硬性条件不能低于0.4.11，这里规定0.4.20，修改compile version
                ource_code = source_code.replace("pragma solidity ^" + compile_version, "pragma solidity ^" + "0.4.20")
                compile_version = "0.4.20"
                break
            elif all_compile_version[j]==compile_version:
                break

        print("compile version == {}".format(compile_version))
        # pragma solidity 0.x.y; find compile version


    # compile code to bytecode
    shortname = ""  # shortname is used instead of name " xxxx(0x...)" to prevent compile error
    for j in range(0,len(name)):
        if (name[j]>="0" and name[j]<="9") or (name[j]>="A"and name[j]<="Z") or (name[j]>="a"and name[j]<="z"):
            shortname = shortname + name[j]
        else:break

    # if filename=="ETHVault":
    #     print(source_code)
    #     exit(0)
    # if source_code.find("contract "+ shortname)==-1:
    #     source_code = source_code + "\n\n" + "contract "+ format(shortname) + "{}"
        ## 类似主函数，缺了要加上
        ### 但是还不够，除了不能带有下划线的文件名，必须没有带下划线的contract名才行，并且文件名必须出现在contract中，这需要手动改
        ### 否则我只能抽取contarct名，改带下划线的contract名，重新取文件名，编译之后移花接木
    shortname = filename

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
            allow_paths=[]
        )
        bytecode = compiled_sol["contracts"]["{}.sol".format(shortname)][shortname]["evm"][
            "bytecode"
        ]["object"]
        data = open("./compile_result/compiled_bytecode/{}".format(Name), 'w', encoding='utf-8')
        print(str(bytecode), file=data)
        data.close()
        data2 = open("./compile_result/successfully_compile/{}".format(Name), 'w', encoding='utf-8')
        print(source_code, file=data2)
        data2.close()

        # get abi
        # abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]
        abi = compiled_sol["contracts"]["{}.sol".format(shortname)][shortname]["abi"]
        data3 = open("./compile_result/compiled_bytecode_abi/{}".format(Name), 'w', encoding='utf-8')
        print(str(abi), file=data3)
        data3.close()

    except Exception as e:

        print("FAIL!!")
        failed_sol.append(name)
        data = open("./compile_result/fail_to_compile/{}".format(Name), 'w', encoding='utf-8')
        print(source_code, file=data)
        data.close()
        data = open("./compile_result/fail_to_compile/compile_error_log/{}".format(name+".txt"), 'w', encoding='utf-8')
        print(e, file=data)
        data.close()

    t1 = time.time()
    print("编译以及输出本Contract Bytecode花费了(时间s)：{}".format(t1 - t0))
    timecost.append(t1 - t0)
    costsum = costsum + t1 - t0
    # 记录时间
    crtid = crtid + 1
    if crtid % 50 == 0:
        print("【1 ~ {} 累计用时】：{}".format(crtid, costsum))

print("【总用时】：{}".format(costsum))

data = open("./compile_result/fail_backups.txt", 'w', encoding='utf-8')
print(str(failed_sol), file=data)
data.close()

pd.DataFrame(columns=["Compiled failed sol"], data=failed_sol).to_csv("./failed_sol.csv", encoding="utf-8")

halt = input("HALT")

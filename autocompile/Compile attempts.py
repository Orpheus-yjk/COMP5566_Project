# -*- coding: UTF-8 -*-

import pandas as pd
import os
import shutil
import autocompile

if __name__ == '__main__':
    all_compile_version=[]
    for ver in open("./allcompileversion.txt"):
        all_compile_version.append(ver[:-1]) #去掉换行符
    LOWER_VERSION = ""
    UPPER_VERSION = ""
    while True:
        LOWER_VERSION = input("请输入最低编译器版本 0.x.y：")
        if LOWER_VERSION in all_compile_version:
            break
        else:
            print("invalid version.")

    while True:
        UPPER_VERSION = input("请输入最高编译器版本 0.x.y：")
        if UPPER_VERSION in all_compile_version:
            break
        else:
            print("invalid version.")

    lower_idx = 0
    upper_idx = 0
    for i in range(0,len(all_compile_version)):
        if all_compile_version[i]==LOWER_VERSION:
            lower_idx = i
            break
    for i in range(0,len(all_compile_version)):
        if all_compile_version[i]==UPPER_VERSION:
            upper_idx = i
            break
    # lower_idx > upper_idx
    # lower version -> upper version
    data = {"version":[],"suc_num":[],"fail_num":[]}
    for i in range(lower_idx,upper_idx-1,-1):
        autocompile.main(all_compile_version[i])
        path_suc = "./compile_result/successfully_compile"
        path_fail = "./compile_result/fail_to_compile"
        suc_list = autocompile.getfiles(path_suc)
        fail_list = autocompile.getfiles(path_fail)
        number_suc = len(suc_list)
        number_fail = len(fail_list) - 1
        data["version"].append(all_compile_version[i])
        data["suc_num"].append(number_suc)
        data["fail_num"].append(number_fail)
        if os.path.exists("./compile_result"):
            shutil.rmtree('./compile_result', ignore_errors=True)

    data= pd.DataFrame(data)
    PATH = "./Compile attempts record/"
    if not os.path.exists(PATH):
        os.makedirs(PATH)
    data.to_csv(PATH+"suc_and_fail.csv", sep=',', index=False, header=True)
    writter = open(PATH+"version", 'w', encoding='utf-8')
    print(LOWER_VERSION,file=writter)
    print(UPPER_VERSION,file=writter)
    writter.close()
    halt = input("HALT")
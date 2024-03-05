# -*- coding: UTF-8 -*-

import os

def multi_sol_div(code):
    '''
    划分 .sol files，返回sol file's name+对应内容。同时不对import进行处理，保留原来
    '''
    sols_content = {}
    beg = 0
    while code.find(".sol\":", beg, len(code)) != -1:
        # 1. 找到sol file's name
        # 查找最接近短语“content”的最后一个.sol名称
        beg = code.find(".sol\":", beg, len(code))
        idx = code.find("content", beg, len(code)) # 'content''s position
        if idx == -1: break
        while code.find(".sol\":", beg+1, idx) !=-1 : beg = code.find(".sol\":", beg+1, idx)
        # find the last .sol name nearest to the phrase 'content' in the 'content list'
        tmp = beg - 1
        sol_name = ""
        while code[tmp] != "\"" and code[tmp]!="/":  # 提取sol 文件名，并且去掉前面的路径 /../../
            sol_name = code[tmp] + sol_name
            tmp = tmp - 1
        sol_name = sol_name + ".sol"    # sol 文件名

        beg = code.find("content", beg + 8, len(code)) + 9
        while code[beg] == '}' or code[beg] == ' ' or code[beg] == ':': beg = beg + 1

        # 2. 截取 X.sol 的代码
        count = 0 # 括号管理：'{' > '}'
        tmp2 = beg
        subcode = ""
        while tmp2 < len(code) - 1:
            tmp2 = tmp2 + 1
            subcode = subcode + code[tmp2]
            if code[tmp2] == '\n' or code[tmp2] == '\r' or code[tmp2] == ' ':
                continue
            else:
                if code[tmp2] == '{': count = count + 1
                if code[tmp2] == '}': count = count - 1
                if count < 0:
                    subcode = subcode[:-1]
                    while subcode[-1]=='\n' or subcode[-1]=='\r' or subcode[-1] == ' ' or subcode[-1] == "\"":subcode = subcode[:-1]
                    sols_content[sol_name] = subcode +"\n\n"   # 截取代码完毕，文件名'XXX.sol'对应代码内容
                    break
        beg = tmp2

    return sols_content
    # 返回sol files内容，以字典形式

def find_single_solname_in_phrase(a, Enforce_Complete=False):
    '''
    从import完整或者声明中抽取 ~~.sol 文本，可忽略前面的路径
    '''
    # if a.find("@openzeppelin")!=-1:
    #     Isopenzeppelin = True  # 检查（可能是）外部引用
        # 保留完整路径 "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol"
    # else:
    #     Isopenzeppelin = False
    idx2 = idx = a.find(".sol")
    if Enforce_Complete:
        while a[idx - 1] != ' ' and a[idx - 1] != "\"" and a[idx - 1] != '/':
            idx = idx - 1
            if idx < 0: break
    else:
        while a[idx - 1] != ' ' and a[idx - 1] != "\"":
            idx = idx - 1
            if idx < 0: break
    while a[idx2] != ';' and a[idx2] != "\"" and a[idx2] != "\n":
        idx2 = idx2 + 1
        if idx2 == len(a):break
    return a[idx:idx2]
    # 比如 import "../utils/introspection/ERC165.sol"; 变成 "ERC165.sol";


def multi_sol_concat(sols_content):
    '''
    找import，拓扑排序，搜索，添加
    返回 newcode值
    '''
    import_flag = {}
    unique_flag = {}
    sol_file_adj = {}
    external_import = []
    '''
    1. 区分内部import和外部import， 根据内部import找到继承关系
    '''
    for file_name in sols_content.keys():
        code = sols_content[file_name]
        import_flag[file_name] = []  #储存完整的import声明
        sol_file_adj[file_name] = []
        beg = 0
        while code.find("import", beg) != -1:
            beg = code.find("import", beg)
            end = beg
            while code[end] != ';':
                end = end + 1
                if end - beg > 200:  # maxlength for valid 'import ....' sentence
                    break
                # error, there is no import XXX or from XXX import ...
            if end - beg <= 200:
                import_flag[file_name].append(
                    code[beg:end + 1]  # 储存完整的import声明
                    # 比如import "../../../utils/Context.sol";  or import { CollateralOpts } from "./CollateralOpts.sol";
                )
                unique_flag[code[beg:end + 1]] = True
            beg = end + 1
        # 获取import 声明

    for file_name in sols_content.keys():
        for ele in import_flag[file_name]:
            import_sol = find_single_solname_in_phrase(ele, Enforce_Complete = False)
            if import_sol in sols_content.keys():
                sol_file_adj[file_name].append(import_sol)
                # 记录内部调用
            else:
                external_import.append(ele) # 储存完整的外部import声明

    '''
    2. 进行顺序继承，合并代码
    '''
    record = {}
    for file_name in sols_content.keys():
        record[file_name] = False
        # 所有内部的sol file名称载入字典

    def dfs(file_name):
        mycode = ""
        record[file_name] = True
        for name in sol_file_adj[file_name]:
            if name in record.keys():
                if record[name] == False:
                    mycode = dfs(name) + mycode
        # print("\033[34m这是{}\033[0m".format(file_name))
        return mycode + sols_content[file_name]  #带绝对路径的import

    newcode = ""
    for file_name in sols_content.keys():
        if record[file_name] == False:
            newcode = newcode + dfs(file_name)

    # for file_name in sol_file_adj.keys():
    #     print("\033[31m{} 引用的头文件是\033[0m: ".format(file_name))
    #     print(sol_file_adj[file_name])
    return newcode, unique_flag, external_import
    # 还需要修改整个代码里的import 和 SPDX 的重复声明


def multi_sol_fix(code):
    '''
    deal with multi .sol files, divide them and concat them into one
    '''

    '''
    1. devide code into sol files
    '''
    sols_content = multi_sol_div(code)
    '''
    2. concat sol files into one; return import list
    '''
    newcode, unique_flag, external_import = multi_sol_concat(sols_content)

    return newcode, sols_content, unique_flag, external_import


def regulate_code_import(code, unique_flag, external_import, remain_ex_path=False, remain_in_path=False):
    for ele in unique_flag.keys():
        code = code.replace(ele, '')
    for ele in unique_flag.keys():
        if code.find(ele)!=-1: # 如果是对于单个sol，整体的import声明可能不存在
            import_sol = find_single_solname_in_phrase(ele, Enforce_Complete=False)
            if (import_sol in external_import) and (not remain_ex_path):  # 外部调用(openzeppelin 或者 http: import声明等)截取
                code = code.replace(ele, "import ./"+import_sol+";\n")
                # wripped out
            elif (import_sol in external_import) and remain_ex_path:  # 外部调用(openzeppelin 或者 http: import声明等)保留完整
                code = code
            else:
                if remain_in_path:
                    code = code.replace(ele, "import ./"+import_sol+";\n")    # 内部声明截取
                else:
                    code = code.replace(ele, "\n")    # 内部声明消除
    return code

def main_regulate_source_code(code, name, contract_address, Net):
    '''
    1. remove ^ in  pragma solidity ^
    '''
    code=code.replace("pragma solidity ^", "pragma solidity ")
    try:
        code = code.encode('utf-8').decode('unicode_escape')
        # code = code.replace("\\u003c", "<")
        # code = code.replace("\\u003e", ">")
        # code = code.replace("\\u0026", "&")
        # code = code.replace("\\u0027", "\'")
        # remove \u00X
    except Exception as e:
        print("\033[33m{}\n{}\n\033[0m".format("Source code Encode ERROR:",e))
        # 这是黄色字体
    code=code.replace("\\n","\n")
    code=code.replace("\\r","\r")
    code=code.replace("\\\"","\"")
    # remove \n & \r & \"

    '''
    2. comcat all .sol files
    deal with multi sol files
    '''
    # 基础的定义必须先于派生合同的定义(钻石继承)

    newcode = ""
    sols_content = {}
    unique_flag = {}
    external_import = []
    IsMultiSol = False
    if code.find("\"content\":") != -1:
        newcode, sols_content, unique_flag, external_import = multi_sol_fix(code)
        IsMultiSol = True
    else:
        # 单个文件不用钻石继承 和 import管理
        newcode = code
        sols_content = {name+".sol": code}
        unique_flag = {}
        external_import = []
        IsMultiSol = False

    if len(newcode) < 250 :
        print("\033[31mFetch Code in .sol FAIL!!\033[0m" + " Contract Name: {}".format(name))
        # 这是红色字体 + 黑色name.sol
        return ""

    '''
    3. find compile version
    '''
    examstr = ""
    compile_version_list = []
    for i in range(0,len(newcode)-1):
        examstr = examstr + newcode[i]
        if len(examstr)>len("pragma solidity "): examstr = examstr[1:]
        compile_version = ""
        if examstr == "pragma solidity ":
            idx = i + 1
            while idx < len(newcode):
                if newcode[idx] == ';':break
                compile_version = compile_version + newcode[idx]
                idx = idx + 1
            compile_version_list.append(compile_version)
        i = i + len(compile_version) - 1

    if len(compile_version_list) > 0:
        compile_version = compile_version_list[0]
        print("compile version == {}".format(compile_version))
    else:
        compile_version = "0.8.0"
        compile_version_list.append(compile_version)
        print("\033[31mcompile version:  TBD\033[0m")

    '''4. find SPDX version'''
    examstr = ""
    SPDX_version_list = []
    for i in range(0, len(newcode) - 1):
        examstr = examstr + newcode[i]
        if len(examstr) > len("SPDX-License-Identifier: "): examstr = examstr[1:]
        SPDX_version = ""
        if examstr == "SPDX-License-Identifier: ":
            idx = i + 1
            while idx < len(newcode):
                if newcode[idx] == '\n': break
                SPDX_version = SPDX_version + newcode[idx]
                idx = idx + 1
            SPDX_version_list.append(SPDX_version)
        i = i + len(SPDX_version) - 1

    if len(SPDX_version_list) > 0:
        SPDX_version = SPDX_version_list[0] #抽取一个SPDX License
    else:
        SPDX_version = "MIT"
        SPDX_version_list.append(SPDX_version)

    '''
    5. final regulation : add SPDX, compile version, import;
    '''
    for version in SPDX_version_list:
        if newcode.find("SPDX-License-Identifier: ".format(version)) != -1:
            newcode = newcode.replace("SPDX-License-Identifier: {}".format(version), '')
    # 1. delete multi SPDX annoucement

    for version in compile_version_list:
        if newcode.find("pragma solidity {};".format(version)) != -1:
            newcode = newcode.replace("pragma solidity {};".format(version), '')
    # 2. delete multi annoucement of compile version in .sol files

    newcode = regulate_code_import(newcode, unique_flag, external_import, remain_ex_path=False, remain_in_path=False)
    # 3. delete multi annoucement of import in .sol files AND do Diamond Inheritance

    newcode = "pragma solidity {};".format(compile_version) + '\n\n' + newcode
    # add compile version in front
    newcode = "// SPDX-License-Identifier: {}\n\n".format(SPDX_version) + newcode
    # add SPDX license in front
    while newcode.find("\n\n\n")!=-1:
        newcode = newcode.replace("\n\n\n", "\n\n")
    # leave out blank line

    if IsMultiSol:
        path = "./sourcecode_{}/multisol_div/{}({})".format(Net,name,contract_address)
        if not os.path.exists(path):
            os.makedirs(path)
        for file_name in sols_content.keys():
            try:
                data = open("./sourcecode_{}/multisol_div/{}({})/{}".format(Net,name,contract_address,file_name), 'w', encoding='utf-8')
                printcode = regulate_code_import(sols_content[file_name], unique_flag, external_import, remain_ex_path=True, remain_in_path=True)
                # 进而规范子文件的import声明
                while printcode.find("\n\n\n") != -1:
                    printcode = printcode.replace("\n\n\n", "\n\n")
                # leave out blank line
                print(printcode, file= data)
                data.close()
            except Exception as e:
                print(e)
        data = open("./sourcecode_{}/multisol_div/{}({})/external-list.txt".format(Net,name,contract_address),"a",encoding="utf-8")
        print(external_import, file=data)  #输出外部调用
        data.close()
    return newcode


# -*- coding: UTF-8 -*-

import os

def getfiles(dir):
    filenames=os.listdir(dir)
    return filenames

sourcecodelist = getfiles('./difficult/')
print(sourcecodelist)

sol_file_list={}

def multi_sol_fix(code,name):
    beg = 0
    newcode = ""
    while code.find(".sol\":", beg, len(code))!= -1:
        beg = code.find(".sol\":", beg, len(code))
        idx = code.find("content", beg+8, len(code)) # 'content''s index
        if idx == -1: break

        while code.find(".sol\":", beg+1, idx) !=-1 : beg = code.find(".sol\":", beg+1, idx)
        # find the last .sol name nearest to 'content'
        i = beg - 1
        sol_name = ""
        while code[i]!="\"":
            sol_name = code[i] + sol_name
            i = i - 1
        sol_name = sol_name + ".sol"
        sol_file_list[sol_name] = True
        beg = code.find("content", beg+8, len(code)) + 9

        while code[beg] == '}' or code[beg] == ' ' or code[beg] == ':' : beg = beg + 1

        end = beg

        subcode = ""
        testcode = ""

        while end<len(code)-1:
            end = end + 1
            subcode = subcode + code[end]
            if code[end]=='\n' or code[end]=='\r' or code[end]==' ':
                continue
            else:
                testcode = testcode + code[end]
                if len(testcode) >= 4:
                    if testcode[-4:] == "}\"}," or testcode[-4:] == "}\"}}":
                        cnt = 4
                        while cnt>0 :
                            if subcode[-1] == '\n' or subcode[-1] == '\r' or subcode[-1] == ' ':
                                subcode = subcode[:-1]
                            else:
                                subcode = subcode[:-1]
                                cnt = cnt - 1
                        subcode = subcode + "}\n\n"
                        newcode = newcode + '\n' + subcode
                        break
        beg = end
    return newcode

import_list = []
def regulate_code_import(code):
    beg = 0
    import_list = []
    while code.find("import", beg)!=-1:
        beg = code.find("import", beg)
        end = beg
        while code[end] != ';':
            end = end + 1
            if end - beg > 200: #maxlength
                break
            # error
        if end - beg <= 200: import_list.append(code[beg:end+1])
        beg = end + 1
    for ele in import_list:
        code = code.replace(ele, '')
    for ele in import_list:
        if ele.find("utils") != -1:
            code = ele +'\n' + code
        # remain openzepplin files
    return code

totfail = 0
totgood = 0

for name in sourcecodelist:
    if name[-4:] != ".txt":
        continue

    code = ""
    with open("./difficult/"+name, "r",encoding='utf-8') as f:  # 打开文件
        data = f.read()  # 读取文件
        code = str(data)

    '''1. remove ^ in  pragma solidity ^'''
    code=code.replace("pragma solidity ^", "pragma solidity ")
    code=code.replace("\\n","\n")
    code=code.replace("\\r","\r")
    code=code.replace("\\\"","\"")
    # remove \n & \r & \"

    # if code.find("pragma solidity ") != -1:
    #     beg = code.find("pragma solidity ")
    #     compile_version = code[beg : code.find(";", beg, len(code))]
    #     while compile_version[0] < '0' or compile_version[0] > '9': compile_version = compile_version[1:]
    #     while compile_version[-1] < '0' or compile_version[-1] > '9': compile_version = compile_version[:-1]
    #     print("【{}】".format(name))
    #     print("compile version == {}".format(compile_version))
    #     # pragma solidity 0.x.y; find compile version
    # else:
    #     compile_version = "0.8.19"
    #     # assign one
    '''
    2. comcat all .sol files
    '''
    if code.find("\"content\":") != -1:
        sol_file_list = {}
        newcode= multi_sol_fix(code,name)
    else:
        sol_file_list = {}
        sol_file_list[name[:-4]+".sol"] = True

    if len(newcode) < 250 :
        print("\033[31mTrans FAIL!!\033[0m")
        totfail = totfail + 1
    else :
        totgood = totgood + 1

    '''3. find compile version'''
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

    print("【{}】".format(name))
    if len(compile_version_list) > 0:
        compile_version = compile_version_list[0]
        print("compile version == {}".format(compile_version))
    else:
        compile_version = "0.8.0"
        compile_version_list.append(compile_version)
        print("\033[31mTBD\033[0m")

    '''4. find SPDX version'''
    examstr = ""
    SPDX_version_list = []
    for i in range(0, len(newcode) - 1):
        examstr = examstr + newcode[i]
        if len(examstr) > len("// SPDX-License-Identifier: "): examstr = examstr[1:]
        SPDX_version = ""
        if examstr == "// SPDX-License-Identifier: ":
            idx = i + 1
            while idx < len(newcode):
                if newcode[idx] == '\n': break
                SPDX_version = SPDX_version + newcode[idx]
                idx = idx + 1
            SPDX_version_list.append(SPDX_version)
        i = i + len(SPDX_version) - 1

    if len(SPDX_version_list) > 0:
        SPDX_version = SPDX_version_list[0]
    else:
        SPDX_version = "MIT"
        SPDX_version_list.append(SPDX_version)

    '''
    5. final regulation
    '''
    for version in SPDX_version_list:
        if newcode.find("// SPDX-License-Identifier: ".format(version)) != -1:
            newcode = newcode.replace("// SPDX-License-Identifier: {}".format(version), '')
    # 1. delete multi SPDX annoucement
    for version in compile_version_list:
        if newcode.find("pragma solidity {};".format(version)) != -1:
            newcode = newcode.replace("pragma solidity {};".format(version), '')
    # 2. delete multi annoucement of version in .sol files
    newcode = regulate_code_import(newcode)
    # 3. delete multi annoucement of import in .sol files
    while newcode.find("\n\n\n")!=-1:
        newcode = newcode.replace("\n\n\n", "\n\n")
    # leave out blank line
    newcode = "pragma solidity {};".format(compile_version) + '\n\n' + newcode
    # add compile version in front
    newcode = "// SPDX-License-Identifier: MIT" + '\n\n' + newcode
    # add SPDX license in front

    # newcode = newcode + "\n}\n"

    print("CODE LEN:", len(code), len(newcode))
    data = open("./difficult/newforge/{}".format(name), 'w', encoding='utf-8')
    print(newcode, file=data)
    data.close()

print("\033[31mFAIL number:{}\033[0m ".format(totfail))

print("\033[32mGOOD: {}\033[0m".format(totgood))


###################### deprecated

#
# def DFS(String):
#     ret = ""
#     print(eval(String))
#     exit(0)
#     try:
#         tmp = eval(String)
#         print(1)
#         if type(tmp) == "dict":
#             for key, value in dict.items():
#                 if key[-4:] == ".sol":
#                     # find a .sol file
#                     print("\033sol fine name: {}\033[0m".format(key))
#                     try:
#                         tmp2 = eval(value)
#                         if "content" in tmp2:
#                             sourcecode = tmp2["content"]
#                             ret = ret + "\n" + sourcecode + '\n'
#                             # add new .sol file source code
#
#                             beg = 0
#                             while sourcecode.find("import ", beg, len(sourcecode))!=-1:
#                                 beg = sourcecode.find("import ", beg, len(sourcecode))
#                                 end = sourcecode.find(";", beg, len(sourcecode))
#                                 substr = sourcecode[beg:end+1]
#                                 import_list["substr"] = True
#                                 beg = beg + 1
#                             # remain import instance
#
#                     except Exception as e:
#                         continue
#                         # key is not .sol
#             return ret
#             # Done sereaching
#         else:
#             return ret
#             # not a dict
#     except Exception as e:
#         return ret
#         # not a dict

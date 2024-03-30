def do(code):
    t0 = ""
    d0 = []
    name = ""
    checkpoint=False
    for i in range(0,len(code)):
        def isheadofline(idx):  # contract关键字必须行首
            while True:
                idx = idx-1
                if idx <0 :return True
                if idx>=len("abstract"):
                    if code[idx-len("abstract"):idx]=="abstract": #跳过关键字
                        idx = idx - len("abstract")
                        continue
                if code[idx]=='\n' or code[idx]=='\r':return True
                if code[idx]!=' ':return False

        if t0 == "":    #找类型
            if i >= len("library"):
                if code[i-len("library"):i] == "library":
                    if isheadofline(i-len("library")):
                        t0 = "library"
                        checkpoint = True
            if i >= len("interface"):
                if code[i-len("interface"):i] == "interface":
                    if isheadofline(i-len("interface")):
                        t0 = "interface"
                        checkpoint = True
            if i >= len("contract"):
                if code[i-len("contract"):i] == "contract":
                    if isheadofline(i-len("contract")):
                        t0 = "contract"
                        checkpoint = True

        if checkpoint:
            checkpoint = False
            j=i+1
            word=""
            isname = True
            while True:
                if code[j]==' ' or code[j]==',' or code[j]=='{':
                    if word!="" and word!="is":
                        if isname:
                            isname=False
                            name=word
                        else:
                            d0.append(word)
                        word=""
                    if word=="is":word=""
                else:
                    word = word + code[j]
                if code[j]=='{':break
                j=j+1
            break
    return name, t0, d0



def reorganize(code):
    # contract code
    content_dict={}
    dependency = {}
    typology = {}   # contract / abstract contract /  interface / library
    counter = 0
    start = False
    subcode = ""
    comment = False
    string_comment = False
    subcodewithdoc = ""
    withdoc_content_dict={}
    for i in range(0,len(code)):
        subcodewithdoc = subcodewithdoc + code[i]
        if i>1:
            if code[i-1:i+1]=="/*":
                string_comment=True
                subcode = subcode[:-1]
        if string_comment:
            if code[i - 1:i + 1] == "*/":
                string_comment = False
            continue
        if i>1:
            if code[i-1:i+1]=="//":
                comment=True
                subcode = subcode[:-1]
        if comment:
            if code[i]=="\n":
                comment=False
            continue

        subcode = subcode + code[i]
        if code[i]=='{':
            if not start:
                start = True
            counter = counter + 1

        elif code[i]=='}':
            counter = counter - 1
            if counter==0:
                name, type0, dependency0 = do(subcode)
                # name, type0, dependency0 = do(subcodewithdoc)
                content_dict[name] = subcode
                typology[name] = type0
                dependency[name] = dependency0
                start = False
                subcode = ""
                withdoc_content_dict[name] = subcodewithdoc
                subcodewithdoc = ""

    # 尽量按照 先library，再interface，然后(abstract)contract的顺序，看的人舒服很多
    def dfs(name):
        if not bucket[name]: return ""  ##防止重复
        bucket[name] = False
        for n0 in dependency[name]:
            if n0 in bucket.keys():
                if bucket[n0]: dfs(n0)
        queue0.append(name)
        return subcode

    ###################################################### 1. 生成没有注释的代码
    newcode = ""
    bucket = {}
    for name in content_dict.keys():
        bucket[name] = True

    queue0 = []
    libcode = ""
    # 先library
    for name in content_dict.keys():
        if typology[name] == "library":
            # libcode =  dfs(name) + libcode
            dfs(name)

    # 再interface
    for name in content_dict.keys():
        if typology[name] == "interface":
            # intecode = dfs(name) + intecode
            dfs(name)

    # 最后是contract
    for name in content_dict.keys():
        if typology[name] == "contract":
            # contcode =  dfs(name) + contcode
            # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>TOT:",name,len(contcode))
            dfs(name)

    # newcode= libcode + intecode + contcode
    for name in queue0:
        newcode = newcode + content_dict[name]



    ###################################################### 2. 生成有注释的代码
    tmp_dict = content_dict
    content_dict = withdoc_content_dict

    codewithdoc = ""
    bucket = {}
    for name in content_dict.keys():
        bucket[name] = True

    queue0 = []

    # 先library
    for name in content_dict.keys():
        if typology[name] == "library":
            # libcode = dfs(name) + libcode
            dfs(name)

    # 再interface
    for name in content_dict.keys():
        if typology[name] == "interface":
            # intecode = dfs(name) + intecode
            dfs(name)

    # 最后是contract
    for name in content_dict.keys():
        if typology[name] == "contract":
            # contcode =  contcode + dfs(name)
            dfs(name)

    # codewithdoc = libcode + intecode + contcode
    for name in queue0:
        codewithdoc = codewithdoc + content_dict[name]

    content_dict = tmp_dict

    return newcode, content_dict, dependency, typology, codewithdoc, withdoc_content_dict

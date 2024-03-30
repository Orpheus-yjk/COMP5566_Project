def do(code):   # 分离出contract name和 dependency
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

    for i in range(0,len(code)):    # 划分contract
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

        subcode = subcode + code[i]     # 生成没有注释的代码
        if code[i]=='{':
            if not start:
                start = True
            counter = counter + 1

        elif code[i]=='}':
            counter = counter - 1
            if counter==0:
                name, type0, dependency0 = do(subcode)
                content_dict[name] = subcode
                typology[name] = type0
                dependency[name] = dependency0
                start = False
                subcode = ""

    #######################################################################
    # 替换掉含非法字符的contract name
    #######################################################################
    rename = {}
    for name in content_dict.keys():
        sub = ""
        for j in range(0,len(name)):
            if (name[j] >= "0" and name[j] <= "9") or (name[j] >= "A" and name[j] <= "Z") or (name[j] >= "a" and name[j] <= "z") or name[j]=="$":   # $是一个奇怪的符号
                sub = sub + name[j]
            else:
                if sub=="":continue
                break
        if len(sub)<=3:
            import random
            import string
            sub = sub + 'oTo'.join(random.sample(string.ascii_letters + string.digits, 3))
        rename[name] = sub


    # 尽量按照 先library，再interface，然后(abstract)contract的顺序，看的人舒服很多
    def dfs(name):
        if not bucket[name]: return ""  ##防止重复
        bucket[name] = False
        for n0 in dependency[name]:
            if n0 in bucket.keys():
                if bucket[n0]: dfs(n0)
        queue0.append(name)
        return subcode

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

    # 替代rename

    mx = 0
    proper_name = ""
    def dfs_cnt(name):
        if not bucket[name]: return 0
        bucket[name]=False
        cnt = 0
        for n0 in dependency[name]:
            if n0 in bucket.keys():
                if bucket[n0]:
                    cnt = cnt + 1
                    dfs_cnt(n0)
        return cnt + 1
    for name in queue0:
        for ele in rename.keys():
            content_dict[name] = content_dict[name].replace(ele,rename[ele])
        newcode = newcode + content_dict[name]

        for j in bucket.keys():
            bucket[j]=True
        tmp = dfs_cnt(name)
        if tmp > mx:
            mx = tmp
            proper_name = rename[name]

    return newcode, proper_name

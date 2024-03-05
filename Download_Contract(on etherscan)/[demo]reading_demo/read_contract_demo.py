import requests
import time
# 通过url直接加上请求参数，与通过params传参效果是一样的

YourApiKeyToken="FQXNEMBZ59ZG95A6KKXNUIWESBUWTBT82F"
# '''
#     1. getSourceCode
# '''
#
# module = "contract"
# action = "getsourcecode"
# address_list = ["0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413"]
# # param
#
# for address in address_list:
#     t0=time.time()
#     response = requests.get(url=('https://api.etherscan.io/api'+\
#        '?module={}'+\
#        '&action={}'+\
#        '&address={}'+\
#        '&apikey={}').format(module, action, address_list[0], YourApiKeyToken))
#     # 通过params传参
#
#     '''
#     print(type(response)) <class 'requests.models.Response'>
#     print(response.status_code)		# 打印状态码 200
#     print(response.text)		# 获取响应内容
#     '''
#
#     text_dict=eval(response.text)
#     # 响应内容-字符串转换为字典
#     source_code_list=text_dict["result"]
#     print(source_code_list)
#     for ele in source_code_list:
#         print(ele)
#         source_code=ele["SourceCode"]
#         print(source_code)
#
#
#     t1=time.time()
#     print("读取以及输出本条约花费了(时间s)：{}".format(t1-t0))



'''
    2. getContractABI
'''

module = "contract"
action = "getabi"
address_list = ["0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413"]
# param

for address in address_list:
    t0=time.time()
    response = requests.get(url=('https://api.etherscan.io/api'+\
       '?module={}'+\
       '&action={}'+\
       '&address={}'+\
       '&apikey={}').format(module, action, address_list[0], YourApiKeyToken))
    # 通过params传参

    print(response.text)  # 获取响应内容
    text_dict = eval(response.text)
    print(str(text_dict["result"]))
    # JSON格式
# 目录
> 1. `readContractSourceCode.py` 选择从Mainnet/Georli/Sepolia浏览器下载5000，5000，3500条Contracts的rawcode，并且拼接成可运行的源代码(少数本地编译有问题但remix上可以编译通过)。调用获取api见：[https://docs.etherscan.io/api-endpoints/contracts](https://docs.etherscan.io/api-endpoints/contracts)。
> 2. `readContractABI.py`  选择从Mainnet/Georli/Sepolia浏览器下载5000，5000，3500条Contracts的ABI。
> 3. `[fintech]getBytecode.py` 本地下载的合约源代码进行编译得到bytecode。
> 4. 其他文件：`data`内是合约地址，`utils`内是库。`[demo]reading_demo`是读取样例。
> 这是[**_github项目地址 : https://github.com/Orpheus-yjk/COMP5566_Project/tree/main/Download_Contract(on%20etherscan)_**](https://github.com/Orpheus-yjk/COMP5566_Project/tree/main/Download_Contract(on%20etherscan) "从etherscan上读取代码")。
> 

# 运行方法
> 1. 运行`read-ContractSourceCode.py`，选择`Mainnet/Georli/Sepolia`，目录下会出现sourcecode\_*net文件夹，打开下有rawcode，purecode，finalcode和multisol_div。finalcode是最终编译来源，multisol_div是将rawcode中若干个完整的.sol文件切分成多个.sol文件。 multisol_div下每个sol file下的external_list.txt存放不属于内部调用的import声明。
> 2. 运行`readContractABI.py`，选择Mainnet/Georli/Sepolia，目录下会出现ABI\_*net文件夹。
> 3. 运行`[fintech]getBytecode.py`，会对下载的源代码编译online每隔一段时间收取新下载的文件进行编译。产生successfully_compile，fail_to_compile，和compiled_bytecode。successfully_compile和fail_to_compile存放成功或者失败的源代码，compiled_bytecode存放字节码。fail_to_compile下compile_error_log存放编译错误信息。
> 3.29上传以后，finalcode文件夹改成存放去除所有注释的代码，此外另一个目录CodewithDocs存放含有注释的代码。

python 3.x

**_requirements.txt_**   

pip install -r requirements.txt 安装所有依赖库，也可以一个个安装。

[**_可以用清华源_** ](https://pypi.tuna.tsinghua.edu.cn/simple "https://pypi.tuna.tsinghua.edu.cn/simple") pip install 包名 -i [**_网址_** ] 。
```
numpy
pandas
requests
web3
py-solc-x
```
本地使用anaconda部署python的话，打开anaconda power shell，下列是查看、添加、删除环境命令：

- 输入conda env list 可查看当前存在哪些虚拟环境
- 输入conda create -n your _env_name python=X.X(版本号) anaconda 命令创建python版本为X.X,名字为your_env_name的虚拟环境
- 删除环境
  - 第一步：首先退出环境
  - conda deactivate
  - 第二步：删除环境
  - conda remove -n  需要删除的环境名 --all


# 编写过程
## 版本0
下载了etherscan主网上已经验证过的合约。共5k条。
下载SourceCode、ABI：使用etherscan api，用requests获取
调用python solcx. compile_standard，编译sol代码。raw code编译时报错很多。
source code放在./sourcecode/中，ABI放在./ABI/中。编译过的字节码放在./bytecode/中。

## 改进 1
1. 对raw code进行修缮，对 转义字符，compile version, SPDX version进行合并。
2. 对包含多sol文件的raw code，进行代码提取，合并，import只保留外部import，内部import消失。没有根据继承顺序合并，造成了一些编译错误


## 改进 2

1. 把包含多sol文件内容的raw code按文件名分开，并且按文件名分开存储。
2. 根据内部import，决定内容顺序进行代码合并。经过检查大部分代码可以通过remix的编译。
3. 检测、合并、编译的步骤模块化。
4. 无法编译的代码放在./difficult/中。编译通过的代码放在./success/中，其字节码放在./bytecode/中。difficult文件夹中包含compile_error_log文件夹，放置编译错误信息。

## 本地运行python进行实时下载和编译  2.24
大部分本地solc编译能通过。约有850/5000条合约不能在本地编译通过，人工在remix也能编译通过。

## 改动 2.25

规范输出目录结构，如开头所示。
rawcode：网页请求源代码
purecode：合并完成，输出到本地目录可以编译的单个`code`文件，没有内部引用。
multisol_div：子代码存放处
finalcode：最终编译的代码

## 改动 3.29
增添了对合约的抽取和重组function。
finalcode存储去掉注释以后的代码，方便编译通过。
CodewithDocs存放原来代码。


# 工具已经上传
对于少数程序下载以后编译不了的合约，请查看fail_to_compile文件夹手动在Remix上修改成功并采集bytecode。
然后将正确的代码复制回本地。







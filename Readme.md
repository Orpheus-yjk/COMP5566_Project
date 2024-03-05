# [COMP]5566 Project
### 任务：在以太坊上检测蜜罐合约
> 
> (1)通过收集研究论文、报告和相关的博客，建立一个蜜罐合同的分类法。
> 
> (2)收集以太坊上的智能合约的源代码、ABI和字节码。
> 
> (3)创建一个工具或利用现有的现有工具来检测分类法中的每种契约。
> 
> (4)分析被发现的合同和对手的利润



### Download_Contract目录下代码文件说明：

Download_Contract(on Etherscan)包含从`Mainnet/Goerli/Sepolia`上下载源代码、ABI、编译源代码的py文件：

`readContractSourceCode.py`，`readContractABI.py`，`[fintech]getBytecode.py`

具体运行方式见其目录下说明。



调用获取api见：[https://docs.etherscan.io/api-endpoints/contracts](https://docs.etherscan.io/api-endpoints/contracts)。



~~~python
# 分割线
~~~



项目原始论文：

[**_usenix.org_**] The Art of The Scam: Demystifying Honeypots in Ethereum Smart Contracts(2019)



对合约下手的论文可观看：

> 用字节码检测 || bytecode detection：
> 
> [**_ieeexplore_**] Machine-learning Approach using Solidity Bytecode for Smart-contract Honeypot Detection in the Ethereum(2021)
> 
> [**_ieeexplore_**] SCSGuard: Deep Scam Detection for Ethereum Smart Contracts(2022)

> 深度学习方法 || deep learning method：
> 
> [**_ieeexplore_**] A Data Science Approach for Detecting Honeypots in Ethereum(2019)
> 
> [**_ieeexplore_**] Honeypot Contract Risk Warning on Ethereum Smart Contracts(2020)




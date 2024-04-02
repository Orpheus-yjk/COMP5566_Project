HoneyBadger ubuntu安装使用步骤
===========
**选用Ubuntu Linux的原因**

如果用Docker镜像代码，想批量检测sol文件，输入输出文件，修改代码不方便。所以如果硬盘容量允许建议让HoneyBadger本地运行，可以图形化操作，文件导入和拖拽，收集数据。

**安装ubuntu(18/20/22.x)虚拟机**

windows(1)下载VMWare：[Download VMware Workstation Player](https://www.vmware.com/products/workstation-player/workstation-player-evaluation.html "https://www.vmware.com/products/workstation-player/workstation-player-evaluation.html")(2)下载ubuntu镜像：[ubuntu镜像文件下载（最新和历史版本）](https://blog.csdn.net/weixin_48557496/article/details/116329462 "ubuntu镜像文件下载（最新和历史版本）")(3)在VM Ware中导入ubuntu镜像。



## Full installation

### Install the following dependencies
#### solc
```
$ sudo add-apt-repository ppa:ethereum/ethereum
$ sudo apt-get update
$ sudo apt-get install solc
```
注意这里的solc版本是1.13。一个查询并且安装特定版本包的例子：
```
$ sudo apt-cache madison  openssh-client

$ sudo apt-get install  openssh-client=1:6.6p1-2ubuntu1
// 上面安装的是  1:6.6p1-2ubuntu1    openssh-client
```

#### evm from go-ethereum
要手动安装。ubuntu库里的ethereum版本太新(1.13.x)，honeybadger运行不了（ethereum<1.8.6）
#### 先安装go
要在Ubuntu上将Go版本更改为Go 1.8，可以按照以下步骤执行命令：

```
打开终端（Terminal）。

下载Go 1.8版本的二进制安装包（根据你的系统架构选择合适的版本）。你可以从官方网站获取Go 1.8的下载链接：https://golang.org/dl/
wget https://dl.google.com/go/go1.8.linux-amd64.tar.gz

解压安装包：
tar -xvf go1.8.linux-amd64.tar.gz

将Go 1.8安装到/usr/local目录下：
sudo mv go /usr/local

更新环境变量，打开你的终端配置文件（如 ~/.bashrc 或 ~/.zshrc）：
nano ~/.bashrc

在最后一行加上
export PATH=$PATH:/usr/local/go1.8/bin

保存并关闭文件（^X）。然后运行以下命令使配置生效：
source ~/.bashrc

验证Go版本是否已更改为Go 1.8：
go version
```
结果是 go version == 1.8.0




#### 再安装ethereum/evm
请给出ubuntu安装ethereum=1.8.0的命令

在Ubuntu上安装Ethereum 1.8.0，可以按照以下步骤执行命令：
```
打开终端（Terminal）。

更新系统软件包列表，确保使用最新的软件包版本：
sudo apt update

安装Ethereum的依赖项：
sudo apt install build-essential libssl-dev libffi-dev python3-dev

下载Ethereum 1.8.0的源代码包：
wget https://github.com/ethereum/go-ethereum/archive/v1.8.0.tar.gz

解压源代码包：
tar -zxvf v1.8.0.tar.gz

进入解压后的目录：
cd go-ethereum-1.8.0

编译和安装Ethereum：
make geth
sudo cp build/bin/geth /usr/local/bin/

安装完成后，可以通过以下命令验证安装：
geth version
```
结果geth == 1.8。


#### [z3](https://github.com/Z3Prover/z3/releases) Theorem Prover version 4.7.1.

Download the [source code of version z3-4.7.1](https://github.com/Z3Prover/z3/releases/tag/z3-4.7.1)

```
$ python scripts/mk_make.py --python
$ cd build
$ make
$ sudo make install
```

#### [Requests](https://github.com/kennethreitz/requests/) library

```
pip install requests
```

#### [web3](https://github.com/pipermerriam/web3.py) library

```
pip install web3
```

## Evaluate Ethereum smart contract honeypot

```
python honeybadger.py -s <contract filename>
```

Run ```python honeybadger.py --help``` for a complete list of options.

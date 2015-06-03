# 前后端分离开发
由于前端开发时，总是受制与后端的各种分支，导致前端维护代码非常困难，所以现在写了一个代理脚本（如附件），我们前端人员只需要在本地运行该脚本，然后配置一些相应url关联即可

实现原理是创建一个完整的代理服务器，如果遇到有本地模版配置的便将数据放入到本地模板渲染。所以后台需要在套用模板的时候判断一下头部，如果有If-Appflood-Api的便吐出json数据

##使用方法：
1、本地环境需要安装python 2.7, tornado, mako

2、下载附件中的脚本放到任何路径

3、打开server.py配置相关的信息
port:本地服务器端口
api_host：需要代理的服务器地址
api_port：需要代理的服务器地址的端口
template_path：前端templates目录的所在路径
static_path：前端static目录的所在路径

4、在server.py目录下增加urls.txt，配置如下（key值是url的path部分，value值是对应本地的模板）：

{
	"/dsp/signin":"rtb/signin.mako",
	"/dsp/overview":"rtb/campaign.mako"
}

5、运行server.py脚本，便开启了一个完整的代理服务器。
http://localhost:8888/dsp/signin  访问一下，你会发现，这个url把本地的mako模关联起来了
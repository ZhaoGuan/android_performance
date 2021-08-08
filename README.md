# Android_performance
使用虚拟环境的时候  
PYTHON_CONFIGURE_OPTS="--enable-framework" pyenv install 3.9.6  
main.py 为主入口可以直接运行  
使用pyinstaller进行打包  
运行build.sh，生成的结果在dist文件夹中。  
数据存放在info文件夹中  
报告放在report文件中 python3.9

#

打包运行时候容易出现的问题:

1. 运行位置问题 主运行的地址为系统地址 如果想要存放内容就要使用相对地址(最好从引入模块中获取地址)  

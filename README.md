# LF_AutoBalePython
Python 自动构建打包上传SVN脚本
#使用说明
#本脚本基于Python语言，学习优化的自动化构建打包脚本，目前仅支持企业发布SVN上传，注释完全，使用便捷，如有其它需要，可自行修改或联系笔者 173090505@qq.com

#条件准备
#1. cd 到需要打包的项目路径下
#2. 四个配置文件放入该目录下
#配置文件 1）用于打包 ios_distribution.cer 发布证书，证书名称随意
#配置文件 2）cer对应的配置文件 ios_Distribution.mobileprovision  文件名字随意
#配置文件 3）本文自带exportOptionsPlist.plist 文件，用于生成xcarchive 的打包配置，(分为app-store、ad-hoc、enterprise、development) 这里默认选择第三中enterprise打包方式
#配置文件 4）本文自带pythonText.py 执行脚本文件
#3. 执行，放入四个配置文件到项目目录下，将cer及mobileprovision双击导入后，执行python pythonText.py即可

#注意事项
#1.本文支持.xcodeproj  .xcworkspace两种项目管理方式打包，读者可自行解注释 (#步骤二 构建企业版)
#2.本文默认打包，上传替换SVN文件方式，默认项目名+.ipa为文件名上传，读者自行添加SVN更新地址
#3.本文自动查询配置文件信息，不需要读者查询添加，代码里面的打包准备请自行配置
#4.检查xcodebuild是否可用，执行xcodebuild -list
#5.检查配置证书是否匹配可用，ios_Distribution.mobileprovision文件目录下执行security cms -D -i  ios_Distribution.mobileprovision

修复iOS11不能构建问题，主要原因是在原来的基础上多了几条plist配置，iOS11根据配置更精确的打包ipa，本脚本默认常规模式打包，如有特殊需要，可以在脚本里面修改配置参数，或者直接联系读者技术指导

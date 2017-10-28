本脚本优势：

1.本脚本采用手动打包，证书信息自动读取,无需读者任何手动查询配置

2.配置文件exportOptionsPlist.plist，根据.mobileprovision文件自动生存配置
3.本脚本支持-xcworkspace  -xcodeproj两种项目管理构建
4.本脚本支持多渠道上传，支持相关密码验证输入（fir，svn，邮件发送）

本脚本准备须知：

1.本脚本文件pythonPerform.py、.mobileprovision、.cer能构建已经自动添加，这里无需添加会自动读取
2.将pythonPerform.py  .mobileprovision放入一个A文件夹，在A放入目标项目即可
3.执行，cd到A文件夹下，执行python pythonPerform.py会自动构建

上传fir渠道须知：

1.上传fir的用户请检测fir命令是否可用，如果没有安装，请先执行sudo gem install -n /usr/local/bin fir-cli安装
2.fir用户准备自己要上传的apitoken即可
上传SVN渠道须知：

1.请准备svn上传地址即可，密码账号会在第一次验证，以后无需验证

2.svn上传会自动替换目标文件

发布邮件须知：

1.发布邮件请先配置发送方邮箱

2.如果有效是阿里企业邮箱配置mtp.mxhichina.com，端口号465，阿里的smtp发送服务自动开启，接收方邮箱随意
3.如果是QQ邮箱作为发送方，请先开启第三方登录邮箱smtp服务，然后用生存的安全码作为本邮件的发送密码

注意事项

1.archive过程不能修改代码，否则正在构建的包会有修改中的问题

2.查看~/Library/MobileDevice/Provisioning\ Profiles/  查看电脑mobileprovision文件集，security cms -D -I  filename.mobileprovision
3.gem environment  查看gem环境
4.本脚本需要xcodebuild安装，使用前先测试xcodebuild命令是否可用
一切尽在不言中，自己看脚本吧，注释完全，使用便捷。
github.com/xjkf123/LF_AutoBalePython

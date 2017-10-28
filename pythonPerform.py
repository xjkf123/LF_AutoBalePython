# -*- coding: utf-8 -*-
import os
import sys
import time
import getpass
import smtplib
import subprocess
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from xml.dom.minidom import Document
from xml.etree.ElementTree import ElementTree,Element

#注意事项
#本脚本简化所有必要信息，改成自动获取
#1.archive过程不能修改代码，否则正在构建的包会有修改中的问题
#~/Library/MobileDevice/Provisioning\ Profiles/   查看电脑mobileprovision文件集，security cms -D -i
#gem environment  查看gem环境
#☟☟☟☟☟☟☟☟☟☟☟☟☟☟☟☟☟☟说明配置如下☟☟☟☟☟☟☟☟☟☟☟☟☟☟☟☟☟☟
#使用者配置项目配置（准备目标发布cer及mobileprovision配置文件及本py即可）
SCHEME               = ""#指定构建版本，如果不指定，默认第一个taget作为构建版本

#上传svn
SVN_ADDRESS
#上传fir，需要配置用户fir_token,如果没有安装fir，执行先 sudo gem install -n /usr/local/bin fir-cli
FIR_APITOKEN         = ""#Fir配置apitoken

#发送邮件配置QQ：smtp.qq.com 端口号465   阿里企业：smtp.mxhichina.com 端口号465
SEND_MAIL            = ""
SMTP_SERVER          = "smtp.mxhichina.com"#smtp邮箱域名链接
SMTP_SERVER_PORT     = "465"#smtp邮箱域名链接端口号
ACCEPT_MAILS         = ['xxx@xx.com','xxx@xx.com']
UPDATE_CONTENT = "更新上传内容配置"#更新上传内容配置
#☝☝☝☝☝☝☝☝☝☝☝☝☝☝☝☝☝☝说明配置如上☝☝☝☝☝☝☝☝☝☝☝☝☝☝☝☝☝☝

#☟☟☟☟☟☟☟☟☟☟☟☟☟☟☟☟☟☟方法配置☟☟☟☟☟☟☟☟☟☟☟☟☟☟☟☟☟☟
#输入邮箱密码
def input_mail_password():
    global smtp_auth_password
    smtp_auth_password = getpass.getpass('password: ')
    server  = smtplib.SMTP_SSL(SMTP_SERVER,SMTP_SERVER_PORT)
    server.login(SEND_MAIL, smtp_auth_password)

#获取当前项目路径及配置文件路径
def current_path_method():
    #默认utf-8 编码
    if sys.getdefaultencoding() != 'utf-8':
        reload(sys)
        sys.setdefaultencoding('utf-8')
    global current_path,execution_path
    execution_path = string_subprocessPopen("pwd",None,True)
    current_path = string_subprocessPopen("cd .. && pwd",None,True)
    print "\ncurrent_path_method方法完成\n当前项目路径\n%s\n当前配置文件路径\n" % (current_path)

#获取mobileprovision配置文件相关信息
def current_mobileprovision_method():
    print "☟☟☟☟☟☟☟☟☟mobileprovision配置文件如下☟☟☟☟☟☟☟☟☟☟☟"
    print value_mobileprovision("输出mobileprovision","")
    print "☝☝☝☝☝☝☝☝☝mobileprovision配置文件如上☝☝☝☝☝☝☝☝☝☝☝"
    global uuid_mobileprovision,teamName_mobileprovision,fileName_mobileprovision
    global bundleId_mobileprovision,cerId_mobileprovision
    
    uuid_mobileprovision         = value_mobileprovision("<key>UUID</key>","</string>")
    fileName_mobileprovision     = value_mobileprovision("<key>Name</key>","</string>")
    cerId_mobileprovision        = value_mobileprovision("<key>com.apple.developer.team-identifier</key>","</string>")
    teamName_mobileprovision     = "iPhone Distribution: " + value_mobileprovision("<key>TeamName</key>","</string>")
    bundleIdTemp_mobileprovision = value_mobileprovision("<key>application-identifier</key>","</string>")
    bundleId_mobileprovision     = bundleIdTemp_mobileprovision[len('%s'%(cerId_mobileprovision))+1:len('%s'%(bundleIdTemp_mobileprovision))]

#获取当前项目scheme
def current_scheme_method():
    scheme_string = string_subprocessPopen("xcodebuild -list",current_path,False)
    global scheme
    #判断版本是否指定，并且存在于版本列表中
    if SCHEME.strip():
        if SCHEME in scheme_string:
            scheme = SCHEME
            return
    #没有指定版本，默认获取第一个作为版本构建
    string_location = scheme_string.find("\n",scheme_string.find("Targets:\n        ") + len("Targets:\n        "))
    scheme = scheme_string[scheme_string.find("Targets:\n        ") + len("Targets:\n        "):string_location]

#创建build配置exportOptionsPlist.plist文件
def create_exportOptionsPlist_method():
    os.system("rm -r exportOptionsPlist.plist")
    # 创建dom文档
    doc = Document()
    plist = doc.createElement('plist')
    doc.appendChild(plist)
    dict = doc.createElement('dict')
    plist.appendChild(dict)
    create_node(doc,dict,"key","compileBitcode")
    compileBitcode = doc.createElement("false")
    dict.appendChild(compileBitcode)
    create_node(doc,dict,"key","method")
    create_node(doc,dict,"string","enterprise")
    create_node(doc,dict,"key","provisioningProfiles")
    key1 = doc.createElement("dict")
    dict.appendChild(key1)
    create_node(doc,key1,"key",bundleId_mobileprovision)
    create_node(doc,key1,"string",fileName_mobileprovision)
    create_node(doc,dict,"key","signingCertificate")
    create_node(doc,dict,"string","iPhone Distribution")
    create_node(doc,dict,"key","signingStyle")
    create_node(doc,dict,"string","manual")
    create_node(doc,dict,"key","stripSwiftSymbols")
    compileBitcode = doc.createElement("true")
    dict.appendChild(compileBitcode)
    create_node(doc,dict,"key","teamID")
    create_node(doc,dict,"string",cerId_mobileprovision)
    #xml转plist
    f = open("exportOptionsPlist.xml", "w")
    f.write(doc.toprettyxml(indent = "\t", newl = "\n", encoding = "utf-8"))
    f.close()
    os.system("plutil -convert xml1 exportOptionsPlist.xml -o exportOptionsPlist.plist")
    os.system("rm -r exportOptionsPlist.xml")
    if os.path.exists('%s/exportOptionsPlist.plist' % (execution_path)):
        print "\n exportOptionsPlist配置文件生成成功\n"

#设置xml子节点
def create_node(doc,father,note_key,note_value):
    key = doc.createElement(note_key)
    key_text = doc.createTextNode(note_value)
    key.appendChild(key_text)
    father.appendChild(key)

# 遍历指定目录，显示目录下的所有文件名，如果有目标文件，返回True
def traverse_file(path,compare_file):
    pathDir =  os.listdir(path)
    for allDir in pathDir:
        child = os.path.join('%s' % (allDir))
        if cmp(child,compare_file) == 0:
            return True

#查询mobileprovision key信息
def value_mobileprovision(findKey,valueLabel):
    file_mobileprovision = "";
    valueLabel_ = valueLabel.replace("/", '')
    file_mobileprovision = access_filename(execution_path,".mobileprovision")
    if not file_mobileprovision.strip():
        print "获取配置文件.mobileprovision文件失败，请检查文件是否存在Python_AutoBuild中"
        sys.exit(1)

    string_mobileprovision = string_subprocessPopen('security cms -D -i %s' % (file_mobileprovision),None,False)
    if findKey == "输出mobileprovision":
        return string_mobileprovision

    findKey_location = string_mobileprovision.find('%s' % (findKey))
    string_mobileprovision = string_mobileprovision[findKey_location:]
    findKey_location = string_mobileprovision.find('%s' % valueLabel_)
    value = string_mobileprovision[findKey_location + len('%s' % valueLabel_) :string_mobileprovision.find('%s' % valueLabel)]
    return  value

#获取目标目录文件名
def access_filename(cwd_patch,file_suffix):
    for file_name in os.listdir(cwd_patch):
        if os.path.splitext(file_name)[1] == file_suffix:
            return file_name
    return ""

#执行终端系统命名，获取打印数据
def string_subprocessPopen(command,cwd_patch,cancel_newline):
    command_file = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=cwd_patch)
    command_file.wait()
    command_string = command_file.stdout.read().decode()
    if cancel_newline == True:
        command_string = command_string.replace("\n", '')
    return command_string

#将builde文件移动到文档目录
def move_documents():
    os.system('mv %s %s' % (build_xcarchive,ipa_filePath))
    documents_patch = '%s/Documents' % (string_subprocessPopen("cd && pwd",None,True));
    if not traverse_file(documents_patch,SCHEME) == True :
        os.system("mkdir -p %s/%s" % (documents_patch,SCHEME))
    os.system('mv %s %s/%s' % (ipa_filePath,documents_patch,SCHEME))
    os.system('rm -r %s' % (build_path))
    os.system('rm -r %s/exportOptionsPlist.plist' % (execution_path))

#☟☟☟☟☟☟☟☟☟☟☟☟☟☟☟☟☟☟执行步骤☟☟☟☟☟☟☟☟☟☟☟☟☟☟☟☟☟☟
#步骤一  清理build缓存
def clean_build_cache_method():
    reload(sys)
    sys.setdefaultencoding('utf-8')
    global build_path
    build_path          = '%s/build' % (execution_path)
    build_current_path  = '%s/build' % (current_path)
    os.system("cd .. && xcodebuild clean")
    if os.path.exists(build_path):
        os.system("rm -r %s" % (build_path))
    if os.path.exists(build_current_path):
        os.system("cd .. && rm -r %s" % (build_current_path))
    os.system('mkdir build')

#步骤二  archive项目
def archive_build_method():
    global build_xcarchive,name_projects
    name_xcodeproj      = access_filename(current_path,".xcodeproj")
    name_xcworkspace    = access_filename(current_path,".xcworkspace")
    execution_filename  = name_xcworkspace
    execution_command   = "-workspace"
    if not name_xcworkspace.strip():
        execution_filename  = name_xcodeproj
        execution_command   = "-project"
    #修改xcode签名方式
    name_projects = name_xcodeproj[:-10]
    os.system("sed -i '' 's/CODE_SIGN_STYLE = Automatic;/CODE_SIGN_STYLE = Manual;/g' %s/%s.xcodeproj/project.pbxproj" % (current_path,name_projects))
    build_xcarchive = '%s/%s.xcarchive' % (build_path,scheme)
    archive_cmd     = 'cd .. && xcodebuild archive %s %s -scheme %s -sdk iphoneos -configuration Release -archivePath %s  CODE_SIGN_IDENTITY="%s" PROVISIONING_PROFILE="%s" || exit' % (execution_command,execution_filename,scheme,build_xcarchive,teamName_mobileprovision,uuid_mobileprovision)
    print "archive构建版本配置 %s" % (archive_cmd)
    os.system(archive_cmd)

#步骤三  生成ipa包
def exportArchive_ipa_method():
    os.system("sed -i '' 's/CODE_SIGN_STYLE = Manual;/CODE_SIGN_STYLE = Automatic;/g' %s/%s.xcodeproj/project.pbxproj" % (current_path,name_projects))
    global ipa_filePath,ipa_filename
    ipa_filePath             = time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))
    ipa_filePath             = '%s/%s_%s' % (build_path,scheme,ipa_filePath)
    name_exportOptionsPlist  = access_filename(execution_path,".plist")
    exportArchive_cmd = 'xcodebuild -exportArchive -archivePath %s -exportOptionsPlist %s -exportPath %s' % (build_xcarchive,name_exportOptionsPlist,ipa_filePath)
    print "exportArchive_Ipa配置 %s" % (exportArchive_cmd);
    os.system(exportArchive_cmd)
    ipa_filename             = access_filename(ipa_filePath,".ipa")

#☟☟☟☟☟☟☟☟☟☟☟☟☟☟☟☟☟☟上传渠道☟☟☟☟☟☟☟☟☟☟☟☟☟☟☟☟☟☟
#上传SVN，自动替换目标目录里面的ipa,需要配置svn地址，账号密码如果第一次登录会自动验证登录
def upload_channel_svn_method():
    if os.path.exists(ipa_filePath):
        os.system('svn delete  %s%s -m "%s"' % (SVN_ADDRESS,ipa_filename,"delete updata"))
        os.system('svn import -m %s  %s %s/%s' % (UPDATE_CONTENT,ipa_filePath,SVN_ADDRESS,ipa_filename))
    else:
        print("ipa文件生成失败，请检查原因，或手动生成")

#上传fir，需要配置用户fir_token,如果没有安装fir，执行先 sudo gem install -n /usr/local/bin fir-cli
def upload_channel_fir_method():
    if os.path.exists(ipa_filePath):
        fir_cmd = "fir publish '%s/%s' --token='%s' -c %s -Q --open" % (ipa_filePath,ipa_filename,FIR_APITOKEN,UPDATE_CONTENT)
        os.system(fir_cmd)
    else:
        print("没有找到ipa文件")

#发邮件,附带png安装二维码，这里是fir生成的，SVN渠道暂不支持图片
def send_mail_method():
    msg = MIMEMultipart()
    #版本更新内容
    msgaaa=MIMEText(UPDATE_CONTENT,'plain','utf-8')
    msg.attach(msgaaa)
    #设置二维码安装附件
    qr_code_name = access_filename(ipa_filePath,".png")
    qr_code_path = '%s/%s' % (ipa_filePath,qr_code_name)
    attach_png = MIMEApplication(open(qr_code_path,'rb').read())
    attach_png.add_header('Content-Disposition', 'attachment', filename=qr_code_name)
    msg.attach(attach_png)
    msg['From'] = SEND_MAIL
    msg['To'] = ",".join(ACCEPT_MAILS)
    msg['Subject'] = Header(  "Vlon无垠为你打包打包完成，附件二维码扫描更新,更新时间：" + time.strftime('%Y年%m月%d日%H:%M:%S',time.localtime(time.time())), 'utf-8').encode()
    print "%s msg配置信息" % (msg)
    server  = smtplib.SMTP_SSL(SMTP_SERVER,SMTP_SERVER_PORT)
    server.login(SEND_MAIL, smtp_auth_password)
    server.sendmail(SEND_MAIL,ACCEPT_MAILS, msg.as_string())
    server.quit()

def main():
    #输入邮箱密码
    input_mail_password()

    #获取当前项目路径及配置文件路径
    current_path_method()

    #获取mobileprovision配置文件相关信息
    current_mobileprovision_method()

    #获取当前项目scheme
    current_scheme_method()

    #创建build配置exportOptionsPlist.plist文件
    create_exportOptionsPlist_method()

    #步骤一  清理build缓存
    clean_build_cache_method()

    #步骤二  archive项目
    archive_build_method()

    #步骤三  生成ipa包
    exportArchive_ipa_method()
    
    #上传svn
    upload_channel_svn_method()
    
    #上传fir，需要配置用户fir_token,如果没有安装fir，执行先 sudo gem install -n /usr/local/bin fir-cli
    upload_channel_fir_method()

    #发邮件,附带png安装二维码，这里是fir生成的，SVN渠道暂不支持图片
    send_mail_method()

    #将builde文件移动到文档目录
    move_documents()


# 执行
main()

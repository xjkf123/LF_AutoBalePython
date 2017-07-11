# -*- coding: utf-8 -*-
import os
import subprocess

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



#SVN地址
SVN_ADDRESS = "svn://XXXXXXXXXXXXXXXXXXXXXXXXXXX"

# 获取当前scheme
def get_scheme():
    scheme_file = os.popen("xcodebuild -list")
    scheme_string = scheme_file.read()
    scheme_file.close()
    
    string_location1 = scheme_string.find("\n",scheme_string.find("Schemes:\n        ") + len("Schemes:\n        "))
    scheme = scheme_string[scheme_string.find("Schemes:\n        ") + len("Schemes:\n        "):string_location1]
    return scheme

# 获取当前路径下证书配置信息
def get_certificate_informationh(project_path,key_characters):
    
    file_name = get_file_name(project_path)#获取.mobileprovision文件名
    certificate_file = os.popen('security cms -D -i %s' % (file_name))
    certificate_string = certificate_file.read()
    certificate_file.close()
    
    string_location1 = certificate_string.find('%s' % (key_characters))
    string_location2 = certificate_string.find("</string>",string_location1)
    certificate_value = certificate_string[string_location1 + len('%s' % (key_characters)) + 16:string_location2]
    return   certificate_value

#获取指定目录下的所有指定后缀的文件名
def get_file_name(project_path):
    file_list = os.listdir(project_path)
    for name in file_list:
        if os.path.splitext(name)[1] == '.mobileprovision':
            return name

#步骤一  清理项目缓存及ipa   创建新build目录
def clean_project_build(project_path):
    print "开始清理build缓存"
    os.system('cd %s;xcodebuild clean' % project_path)  # cd到路径，执行缓存清理 clean命令
    build_path = '%s/build' % (project_path) #配置build路径

    if os.path.exists(build_path): #如果build路径不为nil，移除build路径文件
        cleanCmd = "rm -r %s" % (build_path)
        os.system(cleanCmd)
    os.system('cd %s;mkdir build' % project_path) #在当前路径下，新建build文件目录

#步骤二 构建企业版
def build_inhouse_workspace(project_path,project_scheme,project_teamName,project_uuid):
    
    #修改xcode签名方式
    modify_sign_string = "sed -i '' 's/ProvisioningStyle = Automatic;/ProvisioningStyle = Manual;/g' ./%s.xcodeproj/project.pbxproj" % (project_scheme)
    os.system(modify_sign_string)
    
    build_xcarchive = '%s/build/%s.xcarchive' % (project_path, project_scheme)
    #方式一 没有.xcworkspace执行
    #buildCmd = 'xcodebuild -project %s.xcodeproj -scheme %s -sdk iphoneos -configuration Release clean archive -archivePath %s  CODE_SIGN_IDENTITY="%s" PROVISIONING_PROFILE="%s"' % (project_scheme, project_scheme,build_xcarchive,project_teamName, project_uuid)
    #方式一 有.xcworkspace执行
    buildCmd = 'xcodebuild -workspace %s.xcworkspace -scheme %s -sdk iphoneos -configuration Release clean archive -archivePath %s  CODE_SIGN_IDENTITY="%s" PROVISIONING_PROFILE="%s"' % (project_scheme, project_scheme,build_xcarchive,project_teamName, project_uuid)
    print "构建版本配置： %s" % (buildCmd);
    os.system(buildCmd)

#步骤三 生成配置ipa包
def build_ipa(project_path,project_scheme,filename_ipa):
    
    build_path = '%s/build' % (project_path)
    if os.path.exists(build_path):
        signCmd = 'xcodebuild -exportArchive -archivePath %s/%s.xcarchive -exportOptionsPlist %s/exportOptionsPlist.plist -exportPath %s' % (build_path,project_scheme, project_path, build_path)
        print signCmd
        os.system(signCmd)
        return filename_ipa
    else:
        print("没有找到app文件")
        return ''

#步骤四 更新上传svn
def upload_svn(project_path,ipa_filename):
    
    ipa_path = '%s/build/%s' %(project_path,ipa_filename)
    print ipa_path
    if os.path.exists(ipa_path):
        os.system('svn delete  %s%s -m "%s"' % (SVN_ADDRESS,ipa_filename,"delete updata")) #删除svn里面存在的文件
        os.system('svn import -m "New Import"  %s/build/%s %s%s' % (project_path,ipa_filename,SVN_ADDRESS,ipa_filename))
    else:
        print("ipa文件生成失败，请检查原因，或手动生成")


def main():
    
    # 获取当前目录路径
    process = subprocess.Popen("pwd", stdout=subprocess.PIPE)
    (stdoutdata, stderrdata) = process.communicate()
    project_path = stdoutdata.strip()
    
    # 获取当前scheme
    project_scheme = get_scheme()

    # 获取当前证书配置信息
    project_uuid = get_certificate_informationh(project_path,"UUID")
    project_teamName = "iPhone Distribution: " + get_certificate_informationh(project_path,"TeamName")

    filename_ipa  = '%s.ipa' % (project_scheme)
    #步骤一  清理项目缓存及ipa   创建新build目录
    clean_project_build(project_path)

    #步骤二 构建企业版
    build_inhouse_workspace(project_path,project_scheme,project_teamName,project_uuid)

    #步骤三 生成配置ipa包
    build_ipa(project_path,project_scheme,filename_ipa)

    #步骤四 更新上传svn
    upload_svn(project_path,filename_ipa)

# 执行
main()
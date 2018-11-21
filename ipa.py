import zipfile
import re
import plistlib
import subprocess
import os
import shutil


# 解压ipa获取并信息
def unzip_ipa(path):
    ipa_file = zipfile.ZipFile(path)
    plist_path = find_path(ipa_file, 'Payload/[^/]*.app/Info.plist')
    # 读取plist内容
    plist_data = ipa_file.read(plist_path)
    # 解析plist内容
    plist_detail_info = plistlib.loads(plist_data)
    # 获取plist信息
    get_ipa_info(plist_detail_info)

    # 获取mobileprovision文件路径
    provision_path = find_path(ipa_file, 'Payload/[^/]*.app/embedded.mobileprovision')
    # 临时解压
    ipa_file.extract(provision_path, './')
    # 获取当前路径
    current_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + ".")

    # 获取mobileprovision路径并保存为plist
    string_mobileprovision = string_subprocessPopen('security cms -D -i %s > ./temp.plist' % (current_path + '/' + provision_path),
                                                    None, False)
    temp_plist = './temp.plist'
    #加载plist并获取信息
    with open(temp_plist,'rb') as fb:
        plist_info = plistlib.load(fb)
        print('过期时间:',plist_info['ExpirationDate'])
        print('UDID:' + str(len(plist_info['ProvisionedDevices'])) + '个')
        for i in plist_info['ProvisionedDevices']:
            print(i)
    # 删除临时解压文件
    shutil.rmtree('./Payload')
    os.remove(temp_plist)


# 获取plist路径
def find_path(zip_file, pattern_str):
    name_list = zip_file.namelist()
    pattern = re.compile(pattern_str)
    for path in name_list:
        m = pattern.match(path)
        if m is not None:
            return m.group()



# 获取ipa信息
def get_ipa_info(plist_info):
    print('软件名称: %s' % str(plist_info['CFBundleDisplayName']))
    print('软件标识: %s' % str(plist_info['CFBundleIdentifier']))
    print('软件版本: %s' % str(plist_info['CFBundleShortVersionString']))
    print('支持版本: %s' % str(plist_info['MinimumOSVersion']))


def string_subprocessPopen(command, cwd_patch, cancel_newline):
    command_file = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    cwd=cwd_patch)
    command_file.wait()
    command_string = command_file.stdout.read().decode()
    if cancel_newline == True:
        command_string = command_string.replace("\n", '')
    return command_string


if __name__ == '__main__':
    flag = False
    for filename in os.listdir(os.getcwd()):
        suffix = os.path.splitext(filename)[-1][1:]
        if suffix == 'ipa':
            flag = True
            unzip_ipa('./' + filename)
            break

    if not flag :
        print('请将ipa放在当前目录')

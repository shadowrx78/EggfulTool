#!/usr/bin/env python3
#coding:utf-8

import shutil
import os
# import plistlib
import subprocess
import sys
import re
import random
import ctypes
import zipfile
import time

import json
# import commands

from collections import OrderedDict

from sys import platform

from tkinter import *
from tkinter import messagebox
from tkinter import font
import traceback


IS_ERROR_SHOW_MESSAGEBOX = True
# 彩色输出
STD_OUTPUT_HANDLE = -11
std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
'''Logging class for log manager'''
class Logging:
    # Windows CMD命令行 字体颜色定义 text colors
    FOREGROUND_BLACK = 0x00 # black.
    FOREGROUND_DARKBLUE = 0x01 # dark blue.
    FOREGROUND_DARKGREEN = 0x02 # dark green.
    FOREGROUND_DARKSKYBLUE = 0x03 # dark skyblue.
    FOREGROUND_DARKRED = 0x04 # dark red.
    FOREGROUND_DARKMAGENTA = 0x05 # dark magenta.
    FOREGROUND_DARKYELLOW = 0x06 # dark yellow.
    FOREGROUND_DARKWHITE = 0x07 # dark white.
    FOREGROUND_DARKGRAY = 0x08 # dark gray.
    FOREGROUND_BLUE = 0x09 # blue.
    FOREGROUND_GREEN = 0x0a # green.
    FOREGROUND_SKYBLUE = 0x0b # skyblue.
    FOREGROUND_RED = 0x0c # red.
    FOREGROUND_MAGENTA = 0x0d # magenta.    品红 偏紫色
    FOREGROUND_YELLOW = 0x0e # yellow.
    FOREGROUND_WHITE = 0x0f # white.

    # Windows CMD命令行 背景颜色定义 background colors
    BACKGROUND_BLUE = 0x10 # dark blue.
    BACKGROUND_GREEN = 0x20 # dark green.
    BACKGROUND_DARKSKYBLUE = 0x30 # dark skyblue.
    BACKGROUND_DARKRED = 0x40 # dark red.
    BACKGROUND_DARKMAGENTA = 0x50 # dark magenta.
    BACKGROUND_DARKYELLOW = 0x60 # dark yellow.
    BACKGROUND_DARKWHITE = 0x70 # dark white.
    BACKGROUND_DARKGRAY = 0x80 # dark gray.
    BACKGROUND_BLUE = 0x90 # blue.
    BACKGROUND_GREEN = 0xa0 # green.
    BACKGROUND_SKYBLUE = 0xb0 # skyblue.
    BACKGROUND_RED = 0xc0 # red.
    BACKGROUND_MAGENTA = 0xd0 # magenta.
    BACKGROUND_YELLOW = 0xe0 # yellow.
    BACKGROUND_WHITE = 0xf0 # white.


    @staticmethod
    def log(*s, color=FOREGROUND_DARKWHITE, end='\n'):
        Logging.set_cmd_text_color(color)
        print(*s, end=end)
        Logging.reset_color()

    @staticmethod
    def debug(*s, end='\n'):
        Logging.log(*s, color=Logging.FOREGROUND_MAGENTA, end=end)

    @staticmethod
    def info(*s, end='\n'):
        Logging.log(*s, color=Logging.FOREGROUND_GREEN, end=end)

    @staticmethod
    def info2(*s, end='\n'):
        Logging.log(*s, color=Logging.FOREGROUND_BLUE, end=end)

    @staticmethod
    def warning(*s, end='\n'):
        Logging.log(*s, color=Logging.FOREGROUND_YELLOW, end=end)

    @staticmethod
    def error(*s, end='\n', isShowMessageBox=IS_ERROR_SHOW_MESSAGEBOX, messageboxParent=None):
        Logging.error_(*s, end=end)
        errStr = traceback.format_exc()
        Logging.error_(errStr, end=end)
        if isShowMessageBox:
            messageboxShowerror('错误', errStr, parent=messageboxParent)

    @staticmethod
    def error_(*s, end='\n'):
        Logging.log(*s, color=Logging.FOREGROUND_RED, end=end)

    @staticmethod
    def set_cmd_text_color(color, handle=std_out_handle):
        Bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
        return 

    @staticmethod
    def reset_color():
        # Logging.set_cmd_text_color(Logging.RED | Logging.GREEN | Logging.BLUE)
        Logging.set_cmd_text_color(Logging.FOREGROUND_DARKWHITE)


    # 测试用
    @staticmethod
    def debug2(*s, end='\n'):
        Logging.log(*s, color=Logging.FOREGROUND_SKYBLUE, end=end)

    @staticmethod
    def debug3(*s, end='\n'):
        # Logging.log(*s, color=Logging.FOREGROUND_BLUE|Logging.BACKGROUND_YELLOW, end=end)
        Logging.log(*s, color=Logging.FOREGROUND_DARKSKYBLUE, end=end)


# run cmd 
def run_cmd(cmd):
    ret = subprocess.call(cmd, shell=True)
    if ret != 0:
        msg = "Error running cmd, return code: %s" % str(ret)
        print(msg)

# 判断是否数字
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False

# 解析终端传入的路径(mac)
def path_parse(path):
    pattern = re.compile(r"\s+$")
    match = pattern.sub(u"", path, 1)
    fPath = match

    strArray = [(r"\\\(", u"("),
                (r"\\\)", u")"),
                (r"\\\%", u"%"),
                (r"\\\s", u" "),
                (r"\\\&", u"&")]
    for strs in strArray:
        p0 = re.compile(strs[0])
        fPath = p0.sub(strs[1], fPath)
    if platform != 'darwin':
        fPath = fPath.replace('"', '')

    return fPath

# 检查路径 没有就创建
def check_dir(dirPath):
    if not os.path.isdir(dirPath):
        os.makedirs(dirPath)

    return dirPath


# 标准化windows路径
def getWinPyPath(winPath):
    path = winPath.replace('"', '')
    path = path.replace('\\', '/')
    # path = try_decode_str(path)
    return path


# # 尝试解码
# def try_decode_str(tryStr):
#     if not isinstance(tryStr, unicode):
#         tl_code = ['utf-8', 'ascii', 'gbk']
#         decode_suc = False
#         decode_str = None
#         for code in tl_code:
#             if not decode_suc:
#                 try:
#                     decode_str = tryStr.decode(code)
#                     decode_suc = True
#                 except Exception as e:
#                     # raise e
#                     pass

#         if decode_suc and decode_str != None:
#             tryStr = decode_str
#     return tryStr


# 获取当前路径
def get_current_path():
    if getattr(sys, 'frozen', None):    #被打成exe
        ret = os.path.realpath(os.path.dirname(sys.executable))
    else:
        # __file__返回模块所在的路径  sys.argv[0]返回主执行文件路径
        # ret = os.path.realpath(os.path.dirname(__file__))
        ret = os.path.realpath(os.path.dirname(sys.argv[0]))

    return ret


# 复制文件
def copy_file_in_dir(src, des):
    if os.path.isfile(src):
        shutil.copy(src,des)
    elif os.path.isdir(src):
        for item in os.listdir(src):
            path = os.path.join(src, item)
            if os.path.isfile(path):
                shutil.copy(path,des)
            if os.path.isdir(path):
                new_des = os.path.join(des, item)
                if not os.path.isdir(new_des):
                    os.makedirs(new_des)
                copy_file_in_dir(path, new_des)


# 删除文件和文件夹
def delete_file_folder(src):
    '''delete files and folders'''
    if os.path.isfile(src):
        try:
            os.remove(src)
        except:
            Logging.error(u"不存在文件:%s" % src)
    elif os.path.isdir(src):
        for item in os.listdir(src):
            itemsrc=os.path.join(src,item)
            delete_file_folder(itemsrc)
        try:
            os.rmdir(src)
        except:
            pass


# 删除文件夹下全部东西
def delete_all_file_in_folder(src):
    if not os.path.isdir(src):
        Logging.error(u"不存在文件夹:%s" % src)
        return
    for item in os.listdir(src):
        path = os.path.join(src, item)
        delete_file_folder(path)


# 同步文件
# src_relpath_base src的相对根目录
# des_relpath_base 同步的目标根目录
# 例:src='app/assets/temp.json'
#    src_relpath_base='app'
#    des_relpath_base='des'
#    结果路径='des/assets/temp.json'
def sync_file_with_relpath(src, src_relpath_base, des_relpath_base, print_error=True, print_info=False):
    result = False
    src = getWinPyPath(os.path.abspath(src))
    src_relpath_base = getWinPyPath(os.path.abspath(src_relpath_base))
    if not os.path.exists(src) or not os.path.exists(src_relpath_base):
        if print_error:
            # print u'E   ====路径不存在'
            Logging.error(u'E   ====路径不存在')
    elif not re.match(r'^%s' % (src_relpath_base), src):
        if print_error:
            # print u'E   ====路径不在 "%s" 目录下' % src_relpath_base
            Logging.error(u'E   ====路径不在 "%s" 目录下' % src_relpath_base)
            Logging.error(u'E   ====%s' % src)
    else:
        des_relpath_base = getWinPyPath(os.path.abspath(des_relpath_base))
        rel_path = getWinPyPath(os.path.relpath(src, src_relpath_base))
        to_path = des_relpath_base + '/' + rel_path
        if os.path.isfile(src):
            check_dir(os.path.split(to_path)[0])
        else:
            check_dir(to_path)
        copy_file_in_dir(src, to_path)
        if print_info:
            # print u'I   ====复制到路径:%s' % to_path
            Logging.info(u'I   ====复制到路径:%s' % to_path)
        result = True
    return result


USE_SCANDIR = True
try:
    import scandir
except Exception as e:
    USE_SCANDIR = False

def os_walk(path):
    if USE_SCANDIR:
        return scandir.walk(path)
    else:
        return os.walk(path)


# 读取json到list
def loadJsonToList(path, ignoreLog=False, isOrdered=True):
    if not os.path.isfile(path):
        if not ignoreLog:
            Logging.error("不存在文件:%s" % path)
        return False

    _config = open(path,'r',encoding='UTF-8')
    try:
        fileContent = _config.read()
    finally:
        _config.close()
    config_List = None
    try:
        if isOrdered:
            config_List = json.loads(fileContent, object_pairs_hook=OrderedDict)
        else:
            config_List = json.loads(fileContent)
    except json.JSONDecodeError as e:
        # raise e
        pass
    return config_List


# 将list写入json
def dumpJsonFromList(path, config_List, indent=None, sort_keys=False, print_dump_path=True):
    if not config_List or not path:
        return False

    with open(path,"wb") as _config:
        content = json.dumps(config_List, ensure_ascii=False, indent=indent, sort_keys=sort_keys)
        try:
            _config.write(content.encode('utf-8'))
        finally:
            _config.close()
        if print_dump_path:
            Logging.info("写入json:%s" % path)
        return True
    return False


# # 编码json列表里的字符串
# def encode_j_list(j_list):
#     if isinstance(j_list, dict):
#         for key in j_list:
#             if isinstance(key, unicode):
#                 j_list[key.encode('utf-8')] = j_list.pop(key)

#         for key in j_list:
#             if isinstance(j_list[key], dict) or isinstance(j_list[key], list):
#                 encode_j_list(j_list[key])
#             elif isinstance(j_list[key], unicode):
#                 j_list[key] = j_list[key].encode('utf-8')
#     elif isinstance(j_list, list):
#         for i in range(0,len(j_list)):
#             if isinstance(j_list[i], dict) or isinstance(j_list[i], list):
#                 encode_j_list(j_list[i])
#             elif isinstance(j_list[i], unicode):
#                 j_list[i] = j_list[i].encode('utf-8')


# 获取时间数组
def getTlTime(seconds, tl_chunks=None):
    if not tl_chunks or tl_chunks == []:
        tl_chunks = [
            60*60,
            60,
            1
        ]
    temp = seconds
    tl_time = []
    for v in tl_chunks:
        data = temp // v
        tl_time.append(data)
        temp = temp - (data * v)
    return tl_time


# 获取前缀后缀
def get_prefix_and_suffix(path):
    fileName = os.path.basename(path)
    prefixName = os.path.splitext(fileName)[0] #前缀
    suffixName = os.path.splitext(fileName)[1] #后缀
    return prefixName, suffixName


# 全字匹配修改
def subn_whole_word(search_str, replace_str, content, n=None):
    # p = r'\W+(%s)\W+' % search_str
    p = r'\b(%s)\b' % search_str
    pattern = re.compile(p)

    number = 0
    if n != None and n <= 0:
        return content, 0

    match = pattern.search(content)
    while match and (not n or (n and number < n)):
        n_str = match.group().replace(search_str, replace_str)
        content = content[:match.start()] + n_str + content[match.end():]
        match = pattern.search(content, match.start() + len(n_str))
        number += 1
    return content, number


# 是否空白字符串
def is_str_empty(s):
    if isinstance(s, str) or s == "":
        return re.match(r'^\s*$', s) and True
    else:
        return False


# 首字母转大小写
def upper_or_lower_first_char(str_, isLower=False):
    temp = str(str_)
    if not temp:
        return str_
    first_char = temp[:1]
    if isLower:
        first_char = first_char.lower()
    else:
        first_char = first_char.upper()
    return first_char + temp[1:]


# 黑框进度条字符
# print u'\r' + get_progress_str(i+1, 100),
def get_progress_str(now_num, total_num, use_precent=True):
    precent = now_num * 100 // total_num if total_num != 0 else 100
    k = 2
    num, num_max = precent // k, 100 // k
    prog_str = ('%d%%' % (precent)) if use_precent else ('%d/%d' % (now_num, total_num))
    p_str = u'%s: [%s%s]' % (prog_str, (u'#' * num), (u' ' * (num_max - num)))
    return p_str


# # 添加文件到压缩包
# # zipfile.ZIP_STORED
# # zipfile.ZIP_DEFLATED
# def zip_write(zip_path, filename, arcname=None, compression=zipfile.ZIP_STORED):
#     if not arcname:
#         arcname = filename

#     f = None
#     try:
#         f = zipfile.ZipFile(zip_path, "w", compression)
#         if os.path.isfile(filename):
#             f.write(filename, arcname, compression)
#         elif os.path.isdir(filename):
#             tl_data = list()
#             for root,dirs,files in os_walk(filename):
#                 for fil in files:
#                     f_path = os.path.abspath(os.path.join(root, fil))
#                     f_relpath = os.path.relpath(f_path, os.path.abspath(filename))
#                     tl_data.append([f_path, os.path.join(arcname, f_relpath)])
#             dis = max(len(tl_data) // 100, 10)
#             now_num = 0
#             for i in range(0,len(tl_data)):
#                 f.write(tl_data[i][0], tl_data[i][1], compression)
#                 if i - now_num >= dis:
#                     now_num = i
#                     # print u'\r' + get_progress_str(now_num+1, len(tl_data)),
#                     Logging.info(u'\r' + get_progress_str(now_num+1, len(tl_data)), end='')
#             # print u'\r' + get_progress_str(len(tl_data), len(tl_data))
#             Logging.info(u'\r' + get_progress_str(len(tl_data), len(tl_data)))
#     except Exception as e:
#         # raise e
#         Logging.error(u'压缩失败')
#         Logging.error(e)
#     finally:
#         if f:
#             f.close()
#         Logging.info2(u'压缩完成：%s' % (zip_path))


# 添加文件到压缩包（优化版）
# zipfile.ZIP_STORED
# zipfile.ZIP_DEFLATED
def zip_write(zip_path, tl_file_or_dir_path, compression=zipfile.ZIP_STORED):
    if tl_file_or_dir_path == None or len(tl_file_or_dir_path) == 0:
        Logging.error(u'压缩路径为空')
        Logging.error(u'压缩失败：%s' % (zip_path))
        return False

    success = True
    f = None
    try:
        f = zipfile.ZipFile(zip_path, "w", compression)
        tl_data = list()

        for file_or_dir_path in tl_file_or_dir_path:
            arcname = os.path.basename(file_or_dir_path)
            if os.path.isfile(file_or_dir_path):
                # f.write(file_or_dir_path, arcname, compression)
                tl_data.append([file_or_dir_path, arcname])
            elif os.path.isdir(file_or_dir_path):
                for root,dirs,files in os_walk(file_or_dir_path):
                    for fil in files:
                        f_path = os.path.abspath(os.path.join(root, fil))
                        f_relpath = os.path.relpath(f_path, os.path.abspath(file_or_dir_path))
                        tl_data.append([f_path, os.path.join(arcname, f_relpath)])

        if len(tl_data) > 0:
            dis = max(len(tl_data) // 100, 10)
            now_num = 0
            for i in range(0,len(tl_data)):
                f.write(tl_data[i][0], tl_data[i][1], compression)
                if i - now_num >= dis:
                    now_num = i
                    # print u'\r' + get_progress_str(now_num+1, len(tl_data)),
                    Logging.info(u'\r' + get_progress_str(now_num+1, len(tl_data)), end='')
            # print u'\r' + get_progress_str(len(tl_data), len(tl_data))
            Logging.info(u'\r' + get_progress_str(len(tl_data), len(tl_data)))
    except Exception as e:
        # raise e
        Logging.error(u'压缩失败：%s' % (zip_path))
        Logging.error(e)
        success = False
    finally:
        if f:
            f.close()
        if success:
            Logging.info2(u'压缩完成：%s' % (zip_path))
    return success


# 输出进度条工具类
class PrintProgressHelper:
    # totalNum 总数
    # usePrecent 是否使用百分比
    # disRate 进度限制比例，dis = totalNum // disRate，数量变化没超过dis就不会刷新输出
    # disMin 进度限制最小值，防止总数过少导致输出拖慢脚本
    def __init__(self, totalNum=-1, usePrecent=True, disRate=100, disMin=10):
        self.usePrecent = usePrecent
        # self.disRate = disRate
        # self.disMin = disMin
        self.nowNum = 0
        self.numTemp = 0
        self.printOnceLock = True
        self.disRate = disRate
        self.disMin = disMin

        self.totalNum = totalNum
        self.dis = None
        self._refreshDis()
        # self.setTotalNum(totalNum)
        # self.totalNum = totalNum
        # self.dis = max(self.totalNum // disRate, disMin)

    def setTotalNum(self, totalNum):
        isClear = self.totalNum != totalNum
        self.totalNum = totalNum
        self._refreshDis(isClear=isClear)

    def setDisRateAndMin(self, disRate=100, disMin=10):
        isClear = self.disRate != disRate or self.disMin != disMin
        self.disRate = disRate
        self.disMin = disMin
        self._refreshDis(isClear=isClear)

    def _refreshDis(self, isClear=False):
        if isClear:
            self.nowNum = 0
            self.numTemp = 0
            self.printOnceLock = True
        self.dis = max(self.totalNum // self.disRate, self.disMin)

    # 输出进度条
    # notEnd 是否不换行
    # ignoreDis 是否无视进度限制
    def printProgress(self, notEnd=True, ignoreDis=False):
        if (self.nowNum - self.numTemp >= self.dis) or self.printOnceLock or ignoreDis:
            self.numTemp = self.nowNum
            self.printOnceLock = False
            Logging.info(u'\r' + get_progress_str(self.nowNum, self.totalNum, use_precent=self.usePrecent), end='' if notEnd else '\n')

    def printZero(self, notEnd=True, ignoreDis=True):
        self.nowNum = 0
        self.printProgress(notEnd=notEnd, ignoreDis=ignoreDis)

    def printChange(self, changeNum, notEnd=True, ignoreDis=False):
        self.nowNum = min(self.totalNum, max(0, self.nowNum + changeNum))
        self.printProgress(notEnd=notEnd, ignoreDis=ignoreDis)

    def printNum(self, num, notEnd=True, ignoreDis=True):
        self.nowNum = min(self.totalNum, max(0, num))
        self.printProgress(notEnd=notEnd, ignoreDis=ignoreDis)

    def printFull(self, notEnd=False, ignoreDis=True):
        self.nowNum = self.totalNum
        self.printProgress(notEnd=notEnd, ignoreDis=ignoreDis)



# cmd命令相关
# 会新建子进程但不等待
def popen(cmd, mode='r', bufsize=-1):
    # print "--------popen"
    # print cmd
    if mode == 'w':
        return subprocess.Popen(cmd, shell=True, bufsize=bufsize, stdin=subprocess.PIPE).stdin
    else:
        return subprocess.Popen(cmd, shell=True, bufsize=bufsize, stdout=subprocess.PIPE).stdout
        # return subprocess.Popen(cmd, shell=True, bufsize=bufsize, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL).stdout

# 会新建子进程并等待
def system(cmd):
    # print "--------system"
    # print cmd
    # https://docs.python.org/zh-cn/3/library/subprocess.html
    # 请不要在此函数中使用 stdout=PIPE 或 stderr=PIPE。 如果子进程向管道生成了足以填满 OS 管理缓冲区的输出而管道还未被读取时它将会阻塞。
    return subprocess.call(cmd, shell=True)

def popen_and_return_log(cmd):
    p = subprocess.Popen(cmd, shell=True, bufsize=1, stdout=subprocess.PIPE)
    log_str = ''
    for line in iter(p.stdout.readline, b''):
        print(line)
        log_str += line
    p.stdout.close()
    p.wait()
    return log_str


def loadContentFromFile(path):
    if not os.path.isfile(path):
        if not ignoreLog:
            Logging.error("不存在文件:%s" % path)
        return False

    _config = open(path,'r',encoding='UTF-8')
    fileContent = None
    try:
        fileContent = _config.read()
    finally:
        _config.close()
    return fileContent


# 写入文件
def dumpToFile(path, content, encoding=None, ignoreLog=False):
    with open(path,"wb") as _config:
        try:
            if encoding:
                _config.write(content.encode(encoding))
            else:
                _config.write(content)
        finally:
            _config.close()
        if not ignoreLog:
            Logging.info(u'写入:%s' % os.path.realpath(path))


# 重命名文件
def renameFile(root, oldName, newName, new_root=None):
    if new_root == None:
        os.rename(os.path.join(root, oldName), os.path.join(root, newName))
    else:
        check_dir(new_root)
        os.rename(os.path.join(root, oldName), os.path.join(new_root, newName))


# 格式化json
def format_json(path, indent=None, ignoreLog=False):
    if os.path.isfile(path):
        # chardet_result = chardet.detect(path)

        # 路径编码问题
        # print_dump_path = False
        # if not isinstance(path, unicode):
        #     tl_code = ['utf-8', 'ascii', 'gbk']
        #     decode_suc = False
        #     decode_str = None
        #     for code in tl_code:
        #         if not decode_suc:
        #             try:
        #                 decode_str = path.decode(code)
        #                 decode_suc = True
        #             except Exception as e:
        #                 # raise e
        #                 pass

        #     if decode_suc and decode_str != None:
        #         print_dump_path = True
        #         path = decode_str
        print_dump_path = True

        try:
            j_list = loadJsonToList(path, True)
            if j_list:
                dumpJsonFromList(path, j_list, indent=indent, print_dump_path=print_dump_path)
            return True
        except Exception as e:
            if not ignoreLog:
                Logging.error('------------------------------')
                Logging.error(path)
                Logging.error(e)
            return False
    else:
        if not ignoreLog:
            Logging.error('------------------------------')
            Logging.error(u"不存在文件:%s" % path)
        return False


# 输入 input_str = input()

# 设置键值对，但是值与默认值相等时删除
def setKVInDataWithExcludeDefault(data, key, value, defaultValue):
    # if data != None and isinstance(data, dict):
    #     if defaultValue == value:
    #         if key in data:
    #             del data[key]
    #     else:
    #         data[key] = value
    setValueWithTlKey(data, [key], value, defaultValue, True)




# 检查路径关系
# path1相对path2 : 0完全相同, -1父路径, 1子路径, 2毫无关系
def comparePath(path1, path2):
    if not path1 or not path2:
        return 2

    if os.path.isdir(path1) and (not path1.endswith('/') or not path1.endswith('\\')):
        path1 += '/'
    if os.path.isdir(path2) and (not path2.endswith('/') or not path2.endswith('\\')):
        path2 += '/'

    path1Len =  len(path1)
    path2Len =  len(path2)
 
    if path1Len > path2Len:
        longPath = path1
        shortPath = path2
        cmpFator  = 1
    else:
        longPath = path2
        shortPath = path1
        cmpFator  = -1
 
    shortPathLen = len(shortPath)
    longPathLen = len(longPath)
    i = 0
    j = 0
    while i < shortPathLen and j < longPathLen:
        c1 = shortPath[i]
        c2 = longPath[j]
        if isSlash(c1):
            if not isSlash(c2):
                return 2
            while i < shortPathLen and isSlash(shortPath[i]):
                i += 1
            while j < longPathLen and isSlash(longPath[j]):
                j += 1
        else:
            if c1 != c2:
                if i == shortPathLen:
                    return cmpFator
                else:
                    return 2
            i += 1
            j += 1
 
    if i == shortPathLen:
        if j == longPathLen:
            return 0
        while j < longPathLen:
            if not isSlash(longPath[j]):
                return cmpFator
            j += 1
        return 0
    else:
        return 2
     
def isSlash(c):
    return c == '/' or c == '\\'




# 深拷贝 分层遍历
def deep_copy_dict(base_dict, isOrdered=None, isIgnoreType=False):
    temp_dict = None
    if isinstance(base_dict, dict):
        if isOrdered == None:
            isOrdered = isinstance(base_dict, OrderedDict)
        temp_dict = OrderedDict() if isOrdered else dict()
    elif isinstance(base_dict, list):
        temp_dict = list()
    else:
        if isIgnoreType:
            return base_dict
        else:
            Logging.error(u'数据类型只能是dict|list')
            return False

    remain_copy_list = list()
    remain_copy_list.append([base_dict, temp_dict])

    while len(remain_copy_list) > 0:
        remain_copy_list_ = list()
        for i in range(0,len(remain_copy_list)):
            temp_ = remain_copy_list[i][1]
            base_ = remain_copy_list[i][0]
            if isinstance(base_, dict):
                for key in base_:
                    if isinstance(base_[key], dict):
                        temp_[key] = OrderedDict() if isOrdered else dict()
                        remain_copy_list_.append([base_[key], temp_[key]])
                    elif isinstance(base_[key], list):
                        temp_[key] = list()
                        remain_copy_list_.append([base_[key], temp_[key]])
                    else:
                        temp_[key] = base_[key]
            elif isinstance(base_, list):
                for key in range(0,len(base_)):
                    if isinstance(base_[key], dict):
                        temp_.append(OrderedDict() if isOrdered else dict())
                        remain_copy_list_.append([base_[key], temp_[key]])
                    elif isinstance(base_[key], list):
                        temp_.append(list())
                        remain_copy_list_.append([base_[key], temp_[key]])
                    else:
                        temp_.append(base_[key])
            else:
                temp_ = base_
        remain_copy_list = remain_copy_list_
    return temp_dict

# 补全默认字段 递归，深度太高会炸
def sync_json_field(default_j_list, j_list):
    hasModify = False
    for key in default_j_list:
        if not key in j_list:
            j_list[key] = default_j_list[key]
            hasModify = True
        else:
            if isinstance(j_list[key], dict):
                temp_list, hasModify_ = sync_json_field(default_j_list[key], j_list[key])
                j_list[key] = temp_list
                hasModify = (hasModify or hasModify_)
    return j_list, hasModify

# 补全或排除默认值字段 分层遍历
# exclude True当字段值==默认值时删除字段，False当字段不存在时按照默认值补全字段
def sync_json_field2(default_j_list, j_list=None, exclude=False):
    isReturnDefault = False
    try:
        if j_list == None or (isinstance(default_j_list, list) and len(j_list) == 0) or (isinstance(default_j_list, dict) and not bool(j_list)):
            isReturnDefault = True
    except Exception as e:
        isReturnDefault = True
    if isReturnDefault:
        if not isinstance(default_j_list, dict) and not isinstance(default_j_list, list):
            return j_list
        if isinstance(default_j_list, dict):
            return (dict() if j_list == None else j_list) if exclude else deep_copy_dict(default_j_list)
        elif isinstance(default_j_list, list):
            return (list() if j_list == None else j_list) if exclude else deep_copy_dict(default_j_list)
    elif isinstance(default_j_list, list):  #列表不处理
        return j_list

    tlTlKey = list()
    tlTlKeyTemp = getTlTlKey(j_list, isEmptyDictOrListAsValue=True)
    for i in range(0,len(tlTlKeyTemp)):
        tlKey = tlTlKeyTemp[i]
        # 列表当作值处理
        if isinstance(tlKey[len(tlKey)-1], int):    #列表
            index = len(tlKey)-2
            while isinstance(tlKey[index], int) and index >= 0:
                index -= 1
            if index >= 0:
                tlKey = tlKey[:index+1]
                if not tlKey in tlTlKey:
                    tlTlKey.append(tlKey)
        else:
            tlTlKey.append(tlKey)
        # if not isinstance(tlKey[len(tlKey)-1], int):
        #     tlTlKey.append(tlKey)

    tmTemp = dict() if exclude else deep_copy_dict(default_j_list)
    for i in range(0,len(tlTlKey)):
        tlKey = tlTlKey[i]
        value, suc1 = getValueWithTlKey(j_list, tlKey)
        defaultValue, suc2 = getValueWithTlKey(default_j_list, tlKey)
        if suc1:
            if exclude and suc2:
                setValueWithTlKey(tmTemp, tlKey, value, defaultValue, isExcludeDefault=True)
            else:
                setValueWithTlKey(tmTemp, tlKey, value)
    return tmTemp

# 按模板排序字段 递归 深度太高会炸
def sort_json_field(default_j_list, j_list, isDeepCopy=True):
    default_j_list_ = deep_copy_dict(default_j_list) if isDeepCopy else default_j_list

    for key in j_list:
        if not key in default_j_list_:
            default_j_list_[key] = j_list[key]

    for key in default_j_list_:
        if key in j_list:
            if isinstance(default_j_list_[key], dict):
                default_j_list_[key] = sort_json_field(default_j_list_[key], j_list[key], False)
            else:
                default_j_list_[key] = j_list[key]

    return default_j_list_


# 根据key路径获取值
def getValueWithTlKey(dictOrList, tlKey):
    if dictOrList == None or (not isinstance(dictOrList, dict) and not isinstance(dictOrList, list)):
        return None, False
    if len(tlKey) == 0:
        return dictOrList, True
    temp = dictOrList
    for i in range(0,len(tlKey)):
        suc = False
        if isinstance(temp, dict):
            if tlKey[i] in temp:
                temp = temp[tlKey[i]]
                suc = True
        else:
            if tlKey[i] < len(temp):
                temp = temp[tlKey[i]]
                suc = True
        # 失败直接退出
        if not suc:
            return None, False
        if not isinstance(temp, dict) and not isinstance(temp, list):
            if i == len(tlKey) - 1:
                break
            else:
                return None, False
    return temp, True

# 获取所有到值的key路径
# isEmptyDictOrListAsValue:bool 是否将空字典和空列表当作值
def getTlTlKey(dictOrList, isEmptyDictOrListAsValue=False):
    if dictOrList == None or (not isinstance(dictOrList, dict) and not isinstance(dictOrList, list)):
        return None

    def helper(tmTemp, tlKeyLast, tempTlTlKeyHaveNext, tlTlKey):
        if isinstance(tmTemp, dict):
            for key in tmTemp:
                value = tmTemp[key]
                tlKeyTemp = deep_copy_dict(tlKeyLast)
                tlKeyTemp.append(key)
                if isinstance(value, dict):
                    if isEmptyDictOrListAsValue and not bool(value):
                        # 空字典空列表当值
                        tlTlKey.append(tlKeyTemp)
                    else:
                        # 有下级dict或list，记录为下一级父节点
                        tempTlTlKeyHaveNext.append(tlKeyTemp)
                elif isinstance(value, list):
                    if isEmptyDictOrListAsValue and len(value) == 0:
                        # 空字典空列表当值
                        tlTlKey.append(tlKeyTemp)
                    else:
                        # 有下级dict或list，记录为下一级父节点
                        tempTlTlKeyHaveNext.append(tlKeyTemp)
                else:
                    # 值，当作子节点终点
                    tlTlKey.append(tlKeyTemp)
        elif isinstance(tmTemp, list):
            for i in range(0,len(tmTemp)):
                value = tmTemp[i]
                tlKeyTemp = deep_copy_dict(tlKeyLast)
                tlKeyTemp.append(i)
                if isinstance(value, dict):
                    if isEmptyDictOrListAsValue and not bool(value):
                        # 空字典空列表当值
                        tlTlKey.append(tlKeyTemp)
                    else:
                        # 有下级dict或list，记录为下一级父节点
                        tempTlTlKeyHaveNext.append(tlKeyTemp)
                elif isinstance(value, list):
                    if isEmptyDictOrListAsValue and len(value) == 0:
                        # 空字典空列表当值
                        tlTlKey.append(tlKeyTemp)
                    else:
                        # 有下级dict或list，记录为下一级父节点
                        tempTlTlKeyHaveNext.append(tlKeyTemp)
                else:
                    # 值，当作子节点终点
                    tlTlKey.append(tlKeyTemp)


    tlTlKey = list()    #能取到值的路径列表
    tlTlKeyHaveNext = list()    #还有下级的路径列表

    # 第一层
    helper(dictOrList, list(), tlTlKeyHaveNext, tlTlKey)

    # 还有下级就继续遍历
    while len(tlTlKeyHaveNext) > 0:
        tempTlTlKeyHaveNext = list()
        for i in range(0,len(tlTlKeyHaveNext)):
            tlKeyHaveNext = tlTlKeyHaveNext[i]
            tmTemp, suc = getValueWithTlKey(dictOrList, tlKeyHaveNext)
            helper(tmTemp, tlKeyHaveNext, tempTlTlKeyHaveNext, tlTlKey)
        tlTlKeyHaveNext = tempTlTlKeyHaveNext

    return tlTlKey

# 根据key路径设置键值对
# tlKey:list 修改的字段在数据内地址，空列表表示修改整个dictOrList
# isExcludeDefault:bool True时，当值(value)与默认值(defaultValue)相等时删除
# isDel:bool True时删除字段
# isInsert:bool 是否插入字段，只有当值所在位置是list才生效，True时插入，False时覆盖
def setValueWithTlKey(dictOrList, tlKey, value, defaultValue=None, isExcludeDefault=False, isDel=False, isInsert=False):
    if dictOrList == None or (not isinstance(dictOrList, dict) and not isinstance(dictOrList, list)):
        return False

    needDel = False
    if isExcludeDefault and value == defaultValue:
        needDel = True
    if isDel:
        needDel = True

    tempValue, suc = getValueWithTlKey(dictOrList, tlKey)
    if needDel and not suc:
        # 需要删但是本来就没值
        return True

    # 空列表，修改整个dictOrList
    if len(tlKey) == 0:
        if isinstance(dictOrList, list):
            del dictOrList[0:]
            for i in range(0,len(value)):
                dictOrList.append(value[i])
        elif isinstance(dictOrList, dict):
            tlK = list()
            for k in dictOrList:
                tlK.append(k)
            for i in range(0,len(tlK)):
                del dictOrList[tlK[i]]
            for k in value:
                dictOrList[k] = value[k]
        return True

    temp = dictOrList
    for i in range(0,len(tlKey)):
        key = tlKey[i]
        if i == len(tlKey) - 1:
            if needDel:
                del temp[key]
            else:
                if isinstance(temp, list):
                    if key >= len(temp):    #超过长度直接添加
                        temp.append(value)
                    else:
                        if isInsert:    #插入
                            temp.insert(key, value)
                        else:       #覆盖
                            temp[key] = value
                else:
                    temp[key] = value
        else:
            if isinstance(temp, dict):
                if not isinstance(key, str):
                    # temp是字典key不是str，跳出
                    return False
                if not key in temp:
                    if isinstance(tlKey[i+1], int):     #key是int的是list
                        temp[key] = list()
                    else:
                        temp[key] = dict()
                temp = temp[key]
            elif isinstance(temp, list):
                if not isinstance(key, int):
                    # temp是列表key不是int，跳出
                    return False
                # key大于列表长度，填None补足
                if key >= len(temp):
                    for j in range(0,key - len(temp)):
                        temp.append(None)
                    if isinstance(tlKey[i+1], int):     #key是int的是list
                        temp.append(list())
                    else:
                        temp.append(dict())
                if temp[key] == None:
                    if isinstance(tlKey[i+1], int):     #key是int的是list
                        temp[key] = list()
                    else:
                        temp[key] = dict()
                temp = temp[key]
            else:
                # key路径没走完，temp不是dict或list，跳出
                return False
    return True





# 输出时间 测试代码耗时
def showtime(name, start_time=None, color=Logging.FOREGROUND_DARKWHITE):
    now_time = time.time()
    if start_time != None:
        Logging.log("[{}] nowTime: {:.4f}s, startTime: {:.4f}s, timeShift: {:.4f}s".format(name, now_time, start_time, now_time - start_time), color=color)
    else:
        Logging.log("[{}] nowTime: {:.4f}s".format(name, now_time), color=color)
    return now_time


#######################################
# ----------cmd脚本相关----------
# 序列化处理cmd操作说明
def getOperHelpDescAndTmOper(tlOper):
    tlFormatKey = ['ENTER', 'LINE', 'DESC']
    tmOper = dict()

    # 说明文本
    helpDesc = ''
    spaceCount = 4
    spaceStr = ''
    noError = True
    for i in range(0,spaceCount):
        spaceStr += ' '
    for oper in tlOper:
        if isinstance(oper, list):
            if not oper[0] in tlFormatKey:
                if len(oper) >= 3:
                    # [key, (str)对应函数名, (str)说明文本, (bool)隐藏]
                    if len(oper) < 4 or not oper[3]:
                        helpDesc += '\n%s%s : %s' % (spaceStr, oper[0], oper[2])
                    if not oper[0] in tmOper:
                        tmOper[oper[0]] = oper
                    else:
                        Logging.error('操作键冲突：%s' % oper[0])
                        noError = False
            else:
                if oper[0] == 'ENTER': #空行
                    helpDesc += '\n'
                elif oper[0] == 'LINE': #分隔线
                    # ['LINE', (bool)删除行头空格, (str)替换分隔字符, (int)字符数]
                    lineChar = '-'
                    needTab = True
                    strCount = 27 - spaceCount
                    if len(oper) > 1 and oper[1] == True:
                        needTab = False
                    if len(oper) > 2:
                        lineChar = oper[2]
                    if len(oper) > 3:
                        strCount = oper[3]
                    else:
                        if not needTab:
                            strCount += spaceCount
                    lineStr = ('%s' % spaceStr) if needTab else ''
                    for i in range(0,strCount):
                        lineStr += lineChar
                    helpDesc += '\n%s' % lineStr
                elif oper[0] == 'DESC':
                    # ['DESC', (str)描述字符串, (bool)删除行头空格]
                    needTab = True
                    if len(oper) > 2 and oper[2] == True:
                        needTab = False
                    descStr = ('%s' % spaceStr) if needTab else ''
                    if len(oper) > 1:
                        descStr += oper[1]
                    helpDesc += '\n%s' % descStr
    return helpDesc, tmOper, noError

##### 以下为getOperHelpDescAndTmOper使用示例
# def main():
#     tlOper = [
#         ['all', 'deployAll', '部署全部'],
#         ['ENTER'],
#         ['ref', 'deployRef', '部署配置表到工程+生成相关代码'],
#         ['refg', 'deployRefGenerate', '根据工程内配置表生成代码（RefMgrGen.cs和对应配置类）'],
#         ['ENTER'],
#         ['proto', 'deployProto', '部署proto'],
#         ['ENTER'],
#         ['ab', 'deployAssetBundle', '部署AssetBundle，并生成映射文件'],
#         ['abf', 'deployAssetBundleFast', '快速部署AssetBundle，并生成映射文件'],
#         ['abm', 'deployCreateAssetBundleMapJson', '生成本地路径与AssetBundle映射文件'],
#         ['ENTER'],
#         ['svn', 'svnUpdate', '更新resSource、refConfig、proto'],
#     ]
    
#     helpDesc, tmOper, noError = getOperHelpDescAndTmOper(tlOper)

#     print('''
# ---------------------------
# 请输入:%s


# 或者按其他任意键退出''' % helpDesc)

#     try:
#         params = input()
#         params = params.split(' ')
#         if params[0] in tmOper:
#             funName = tmOper[params[0]][1]
#             f = globals().get(funName, None)
#             if f != None:
#                 f()
#             else:
#                 py3_common.Logging.error('找不到函数：%s    key：%s' % (funName, params[0]))
#                 sys.exit(1)
#                 return
#                 # pass
#         else:
#             sys.exit(0)
#             return
#     except Exception as e:
#         py3_common.Logging.error(e)
#         input("err! press any key to exit")
#         sys.exit(1)



#######################################
# ----------tk相关----------
# 输入框
def getEntryText(entry):
    return entry.get()

def setEntryText(entry, text):
    try:
        entry.delete(0, END)
    except Exception as e:
        pass
    entry.insert(0, text)

# 文本框
def getTextText(text):
    str_ = text.get('1.0', END)
    match = re.search(r'^([\w\W]*)\n$', str_)
    if match:
        return match.group(1)
    else:
        return str_

def setTextText(text, textStr):
    try:
        text.delete('1.0', END)
    except Exception as e:
        pass
    text.insert('1.0', textStr)

# 输入框&文本框
def setEditorEnable(editor, enable):
    editor.configure(state='normal' if enable else 'disabled')

def setEditorText(editor, text):
    className = editor.__class__.__name__
    if className == 'Entry':
        return setEntryText(editor, text)
    elif className == 'Text':
        return setTextText(editor, text)

def getEditorText(editor):
    className = editor.__class__.__name__
    if className == 'Entry':
        return getEntryText(editor)
    elif className == 'Text':
        return getTextText(editor)

# 获取光标位置
def getEditorCursorPos(editor):
    className = editor.__class__.__name__
    line, column = None, None
    lineEnd, columnEnd = None, None
    if className == 'Entry':
        column = editor.index('insert')
        line = 1
        try:
            # 处理选中
            p1, p2 = editor.index('sel.first'), editor.index('sel.last')
            column = p1
            columnEnd = p2
            lineEnd = 1
        except Exception as e:
            # raise e
            pass
    elif className == 'Text':
        lcStr = editor.index('insert')
        tlStr = lcStr.split('.')
        try:
            # 处理选中
            p1, p2 = editor.index('sel.first'), editor.index('sel.last')
            tl1, tl2 = p1.split('.'), p2.split('.')
            line, column = int(tl1[0]), int(tl1[1])
            lineEnd, columnEnd = int(tl2[0]), int(tl2[1])
        except Exception as e:
            # raise e
            pass
        if (line == None or column == None) and len(tlStr) > 1:
            line = int(tlStr[0])
            column = int(tlStr[1])
    return line, column, lineEnd, columnEnd

# 设置光标位置
def setEditorCursorPos(editor, line, column):
    if line == None or column == None:
        return
    className = editor.__class__.__name__
    if className == 'Entry':
        editor.icursor(column)
    elif className == 'Text':
        editor.mark_set('insert', '%d.%d' % (line, column))

def _tkEditorCopy(editor, event=None):
    editor.event_generate("<<Copy>>")

def _tkEditorCut(editor, event=None):
    editor.event_generate("<<Cut>>")

def _tkEditorPaste(editor, event=None):
    editor.event_generate("<<Paste>>")

def _onTkEditorRightClick(event, editor, menubar):
    isEnable = True
    isEntry = False
    try:
        isEntry = editor.__class__.__name__ == 'Entry'
        isEnable = editor['state'] != 'disabled'
    except Exception as e:
        # raise e
        pass
    menubar.delete(0,END)
    if isEnable:
        menubar.add_command(label='复制', command=lambda:_tkEditorCopy(editor), accelerator='Ctrl+C')
        menubar.add_command(label='剪切', command=lambda:_tkEditorCut(editor), accelerator='Ctrl+X')
        menubar.add_command(label='粘贴', command=lambda:_tkEditorPaste(editor), accelerator='Ctrl+V')
    else:
        # 不可用时entry无法选中，text可以
        if not isEntry:
            menubar.add_command(label='复制', command=lambda:_tkEditorCopy(editor), accelerator='Ctrl+C')
    menubar.post(event.x_root,event.y_root)

# 绑定输入框右键（复制、剪切、粘贴）
def bindTkEditorRightClick(editor, root, tkThemeHelper=None):
    menubar = Menu(root, tearoff=False)
    if tkThemeHelper != None:
        tkThemeHelper.addTkObj(menubar)
    editor.bind('<Button-3>', lambda e, ent=editor, menu=menubar:_onTkEditorRightClick(e, ent, menu))

# 按钮
def setBtnEnable(btn, enable):
    # btn.configure(state='normal' if enable else 'disabled', fg='black' if enable else 'gray')
    btn.configure(state='normal' if enable else 'disabled')

# 选中框
def setCheckbuttonEnable(checkbutton, enable):
    checkbutton.configure(state='normal' if enable else 'disabled')

# 创建tk字体
def createTkFont(master, fontSize, fontName='TkDefaultFont', kwargs=dict()):
    tkFontActual = font.nametofont(fontName).actual()
    # fontSize = args['fontSize'] if 'fontSize' in args else GlobalValue.DEFAULT_TK_FONT_SIZE
    # if fontSize == None:
    #     fontSize = DEFAULT_TK_FONT_SIZE
    localFont = font.Font(master, size=fontSize)
    tkFontKwargs = dict()
    if 'weight' in tkFontActual:
        tkFontKwargs['weight'] = tkFontActual['weight']
    if 'family' in tkFontActual:
        tkFontKwargs['family'] = tkFontActual['family']
    if 'slant' in tkFontActual:
        tkFontKwargs['slant'] = tkFontActual['slant']
    if 'underline' in tkFontActual:
        tkFontKwargs['underline'] = tkFontActual['underline']
    if 'overstrike' in tkFontActual:
        tkFontKwargs['overstrike'] = tkFontActual['overstrike']
    sync_json_field(tkFontKwargs, kwargs)
    localFont.configure(**kwargs)

    return localFont

# tk表格设置值
# tlTitle:list 列标题
# tlRowIndex:list 行标题
# tlTlData:list[list] 每行数据
def setDataToTkSheet(sheet, tlTitle=list(), tlRowIndex=list(), tlTlData=list()):
    sheet.fix_select_col_with_tl_header(tlTitle)
    sheet.headers(tlTitle)
    sheet.row_index(tlRowIndex)
    sheet.set_sheet_data(tlTlData)
    try:
        if sheet.RI.get_current_width() < sheet.RI.get_default_width():
            sheet.RI.reset_width()
    except Exception as e:
        # raise e
        pass


# 解析tkdnd拖入事件数据，只接受('%D',)
# 绑定示例：dnd.bindtarget(frame, 'text/uri-list', '<Drop>', onDrop, ('%D',))
def parseDndFiles(files='', ignoreLog=False):
    if not ignoreLog:
        Logging.info(files)
    tlFile = list()

    tlFind = re.findall(r'\{([^\n\{\}]*)\}', files)     #有特殊字符或空格的找出来
    tlNoFind = re.sub(r'\{([^\n\{\}]*)\}', '', files).split()   #去掉有有特殊字符或空格的

    def pathRegulate(path):
        return path.replace('\\', '/')

    for s in tlFind:
        tlFile.append(pathRegulate(s))
    for s in tlNoFind:
        if len(s) > 0:
            tlFile.append(pathRegulate(s))

    return tlFile




# 报错弹框
# You would normally put that on the App class
def showError(self, *args):
    tlErr = traceback.format_exception(*args)
    errStr = ''
    for i in range(0,len(tlErr)):
        errStr += tlErr[i]
    Logging.error_(errStr, end='')
    messageboxShowerror('错误', errStr)

# # but this works too
# Tk.report_callback_exception = showError


# 报错弹框过滤
def messageboxShowerror(title, errStr, parent=None):
    tlSkipTagStr = [
        'WinError 1223',        #操作已被用户取消
    ]
    isSkip = False
    for skipTagStr in tlSkipTagStr:
        if re.search(r'%s' % skipTagStr, errStr):
            isSkip = True
            break

    # Logging.info('isSkip:%s' % isSkip)
    if not isSkip:
        if parent != None:
            messagebox.showerror('错误', errStr, parent=parent)
        else:
            messagebox.showerror('错误', errStr)


def messageboxShowerror2(title, errStr, isLoggingError=False, *args, **kwargs):
    if isLoggingError:
        Logging.error(errStr, isShowMessageBox=False)
    messagebox.showerror('错误', errStr, *args, **kwargs)
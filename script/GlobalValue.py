#! python3
# -*- coding: utf-8 -*-

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import font
from tkinter.messagebox import showerror
from tkinter.colorchooser import askcolor
import os, re
import hashlib
import time

import random
import json
import math
import ctypes
import subprocess
from collections import OrderedDict

import sys
from sys import platform
from importlib import import_module
import traceback

# import ccbparser
# import plistlib

from . import tkVirtualListHelper

from . import py3_common
from ctypes import windll
import pyperclip

# from . import EventProxy
from .EventProxy import *


# GlobalValue

#----------------global value & enum----------------

# debug模式
IS_DEBUG = True
# eventProxy派发事件是否显示参数
IS_EVENTPROXY_SHOW_ARGS = False

if IS_DEBUG:
    py3_common.LOGGING_LEVEL = py3_common.LoggingLevelEnum.DEBUG
    tkVirtualListHelper.LOGGING_LEVEL = tkVirtualListHelper.LoggingLevelEnum.DEBUG
else:
    py3_common.LOGGING_LEVEL = py3_common.LoggingLevelEnum.INFO
    tkVirtualListHelper.LOGGING_LEVEL = tkVirtualListHelper.LoggingLevelEnum.INFO

# 模式
class UiModeEnum:
    Normal = 0
    Edit = 1

UI_MODE = UiModeEnum.Normal


# 主窗口
INIT_WINDOW = None
INIT_WINDOW_GUI = None

# 事件代理
EVENT_PROXY = None

# 窗口图标
WINDOW_ICON_PATH = None


# 保存操作类型
class SaveNodeDataOper:
    Edit = 0
    Insert = 1
    Delete = 2


#####风格相关
# 默认字号
DEFAULT_TK_FONT_SIZE = None

BG_COLOR = 'gray94'

# 节点默认大小
FRAME_DEFAULT_WIDTH, FRAME_DEFAULT_HEIGHT = 160, 100

# SELECT_COLOR = 'light sky blue'

# 风格类型
class StyleEnum:
    Default = 0
    Black = 1

# 默认颜色
TM_BTN_TYPE_COLOR_DEFAULT = {
    'common':{'bgColor':BG_COLOR, 'fgColor':'black', 'selectColor':'light sky blue', 'canvasBgColor':BG_COLOR, 'btnDisabledFgColor':'gray30', 'btnFgColor':'blue', 'selectFgColor':'black',
        'tkEntry':{'bgColor':'white', 'selectBgColor':'#2478d5', 'selectFgColor':'white', 'disabledBgColor':BG_COLOR, 'disabledFgColor':'gray30', 'insertbackground':'black'},
        'tkMenu':{'selectBgColor':'DodgerBlue3', 'selectFgColor':'white'},
        'ttkProgressbar':{'background':'#14ab14'},
        'ttkScrollbar':{'background':{'normal':'gray87', 'active':'gray80', 'disabled':BG_COLOR},
                        'troughcolor':BG_COLOR,
                        'arrowcolor':{'normal':'gray30', 'disabled':'gray70'}},
        'ttkCombobox':{'background':{'normal':'gray87', 'active':'gray80', 'disabled':BG_COLOR, 'readonly':BG_COLOR},
                        'foreground':{'normal':'black', 'active':'black', 'disabled':'gray70', 'readonly':'black'},
                        'fieldbackground':{'normal':'white', 'active':'white', 'disabled':BG_COLOR, 'readonly':'white'},
                        'troughcolor':BG_COLOR,
                        'arrowcolor':{'normal':'gray30', 'disabled':'gray70'},
                        }},
    'line':{'bgColor':BG_COLOR, 'fgColor':'black', 'selectFgColor':'black'},
    'btn':{'bgColor':'gray87', 'btnBgColor':BG_COLOR, 'btnFgColor':'black',
            'markDropBgColor':'blue', 'markDropFgColor':'white', 'markBookmarkBgColor':'purple', 'markBookmarkFgColor':'white',
            'markAskExeBgColor':'#008000', 'markAskExeFgColor':'white',
            'typeDisableBgColor':'#c6c6c6', 'typeDisableTextColor':'#4b4b4b'},
    'folder':{'typeBgColor':'pink', 'typeTextColor':'black'},
    'exe':{'typeBgColor':'yellow', 'typeTextColor':'black'},
    'cmd':{'typeBgColor':'gray38', 'typeTextColor':'white'},
    'create':{'bgColor':'gray87', 'fgColor':'blue'},
    'sheet':{'theme':'light blue', 'highlightBgColor':'#d6effe', 'highlightFgColor':'black', 'highlightBgColor2':'#fefed6', 'highlightFgColor2':'black'}
}
# 白色风格默认颜色
TM_BTN_TYPE_COLOR = py3_common.deep_copy_dict(TM_BTN_TYPE_COLOR_DEFAULT)

# 黑色风格默认颜色
TM_BTN_TYPE_COLOR_BLACK = {
    "common":{"bgColor":"#303030", "fgColor":"#e7e7e7", "selectColor":"#ffa74f", "canvasBgColor":"#424242", "btnDisabledFgColor":"#a4a4a4", "btnFgColor":"#ffa74f", "selectFgColor":"black",
            "tkEntry":{"bgColor":"#535353", "selectBgColor":"#ffa74f", "selectFgColor":"#000000", "disabledBgColor":"#666666", "disabledFgColor":"#a4a4a4", "insertbackground":"white"},
            'tkMenu':{'selectBgColor':'#ffa74f', 'selectFgColor':'black'},
            'ttkProgressbar':{'background':'#14ab14'},
            "ttkScrollbar":{"troughcolor":"#4a4a4a",
                "background":{"active":"#787878", "disabled":"#787878", "normal":"#646464"},
                "arrowcolor":{"disabled":"#ababab"}},
            'ttkCombobox':{'background':{'normal':'gray87', 'active':'gray80', 'disabled':BG_COLOR, 'readonly':BG_COLOR},
                        'foreground':{'normal':'black', 'active':'black', 'disabled':'gray70', 'readonly':'black'},
                        'fieldbackground':{'normal':'white', 'active':'white', 'disabled':BG_COLOR, 'readonly':'white'},
                        'troughcolor':BG_COLOR,
                        'arrowcolor':{'normal':'gray30', 'disabled':'gray70'},
                        }},
    "line":{"bgColor":"#424242", "fgColor":"#e7e7e7", "selectFgColor":"#000000"},
    "btn":{"bgColor":"#303030", "btnBgColor":"#232323", "btnFgColor":"#e7e7e7", "markDropBgColor":"#7b7bff",
        "markDropFgColor":"#e7e7e7", "markBookmarkFgColor":"#e7e7e7", "markBookmarkBgColor":"#6d6b41",
        "markAskExeBgColor":"#654141", "markAskExeFgColor":"#e7e7e7",
        'typeDisableBgColor':'#646464', 'typeDisableTextColor':'#c7c7c7'},
    "folder":{"typeBgColor":"#0e79c9", "typeTextColor":"#e7e7e7"},
    "exe":{"typeBgColor":"#369645", "typeTextColor":"#e7e7e7"},
    "cmd":{"typeBgColor":"#b45227", "typeTextColor":"#e7e7e7"},
    "create":{"fgColor":"#009d00", "bgColor":"#303030"},
    'sheet':{'theme':'black', 'highlightBgColor':'#d56a00', 'highlightFgColor':'black', 'highlightBgColor2':'#a8a8ff', 'highlightFgColor2':'black'}
}

# 默认风格dict
TM_BTN_TYPE_COLOR_STYLE_DEFAULT = {
    StyleEnum.Default: TM_BTN_TYPE_COLOR_DEFAULT,
    StyleEnum.Black: TM_BTN_TYPE_COLOR_BLACK
}
# 当前风格类型
STYLE_TYPE = StyleEnum.Default

# 主窗口透明度
WINDOW_ALPHA = 100



#####界面行为相关
# 当前选中节点下标
NOW_SELECT_INDEX = None
# 强制显示当前选中
FORCE_SHOW_SELECT = False
# 方向类型
class ArrowDirEnum:
    Up = 0
    Down = 1
    Left = 2
    Right = 3

# 界面位置类型
class ViewPosEnum:
    LeftDown = 1
    Down = 2
    RightDown = 3
    Left = 4
    Center = 5
    Right = 6
    LeftUp = 7
    Up = 8
    RightUp = 9



#####节点相关
# 节点类型信息
TM_NODE_TYPE = None
# 格式
# TM_NODE_TYPE = {
#     'Base':{'class':tkVirtualListHelper.BaseNode, 'defaultSize':{'width':0, 'height':0}},     #父类 姑且能创但基本没用
#     'Line':{'class':LineNode, 'defaultSize':{'width':0, 'height':20}},     #分割线
#     'Btn':{'class':BtnNode, 'defaultSize':{'width':GlobalValue.FRAME_DEFAULT_WIDTH, 'height':GlobalValue.FRAME_DEFAULT_HEIGHT}},      #按钮
#     'Create':{'class':CreateNode, 'defaultSize':{'width':GlobalValue.FRAME_DEFAULT_WIDTH, 'height':GlobalValue.FRAME_DEFAULT_HEIGHT}}    #新建 编辑模式才出来
# }

# 支持类型列表（可外部配置）
TL_SETTING_KEY = ['line', 'folder', 'exe', 'cmd']
# 节点基本属性
TMTL_BASE_KEY = {
    'Line': ['nodeType', 'bgColor', 'height', 'lineTag', 'text'],
    'Btn': ['nodeType', 'bgColor', 'width', 'height', 'btnText', 'typeStr', 'useDrop', 'bookmark', 'askExeMark', 'disable']
}
# 节点额外属性
TMTL_TYPE_ADV_KEY = {
    'line': ['fgColor', 'fontSize'],
    'folder': ['folderPath'],
    'exe': ['exePath'],
    'cmd': ['command', 'tlFilePath', 'notClose', 'openNewCmdWindow', 'autoCd']
}




#####设置相关
###运行路径按入口py来
# 节点配置文件路径
NODES_CONFIG_JSON_PATH = './nodesConfig.json'
# 设置配置文件路径
SETTING_CONFIG_JSON_PATH = './settingConfig.json'
# 已删除节点备份文件路径
DELETED_NODES_BACKUP_JSON_PATH = './deletedNodes.json'
# 配置备份路径
JSON_BACKUP_DIR = './backup'
# 出错配置备份路径
JSON_ERROR_BACKUP_DIR = os.path.join(JSON_BACKUP_DIR, 'error')
# 记录初始化错误信息
TL_INIT_ERROR_MSG = list()
# 全局 执行前询问
ASK_BEFORE_EXECUTING = None
# 禁用右键编辑节点
DISABLE_RCLICK_EDIT_NODE = False
# 界面位置锚点字典
TM_DEFAULT_VIEW_POS_ANCHOR = {}
if True:
    TM_DEFAULT_VIEW_POS_ANCHOR[ViewPosEnum.LeftDown] = {'x':0.2, 'y':0.8}
    TM_DEFAULT_VIEW_POS_ANCHOR[ViewPosEnum.Down] = {'x':0.5, 'y':0.8}
    TM_DEFAULT_VIEW_POS_ANCHOR[ViewPosEnum.RightDown] = {'x':0.8, 'y':0.8}
    TM_DEFAULT_VIEW_POS_ANCHOR[ViewPosEnum.Left] = {'x':0.2, 'y':0.5}
    TM_DEFAULT_VIEW_POS_ANCHOR[ViewPosEnum.Center] = {'x':0.5, 'y':0.5}
    TM_DEFAULT_VIEW_POS_ANCHOR[ViewPosEnum.Right] = {'x':0.8, 'y':0.5}
    TM_DEFAULT_VIEW_POS_ANCHOR[ViewPosEnum.LeftUp] = {'x':0.2, 'y':0.2}
    TM_DEFAULT_VIEW_POS_ANCHOR[ViewPosEnum.Up] = {'x':0.5, 'y':0.2}
    TM_DEFAULT_VIEW_POS_ANCHOR[ViewPosEnum.RightUp] = {'x':0.8, 'y':0.2}
# 各界面位置默认值
TM_DEFAULT_VIEW_POS = {
    'MainGui': ViewPosEnum.Center,
    'ViewListLineNode': ViewPosEnum.Right,
    'ViewNodeSetting': ViewPosEnum.Center
}
# 各界面位置
TM_VIEW_POS = None



#####其他共享数据
# # 当前节点列表缓存
# TEMP_NODE_LIST = None
# # 节点列表缓存备份，还原或确定保存后销毁
# TEMP_NODE_LIST_BACKUP = None
# 节点缓存，节点数据和顺序数据分开保存
# {
#     "tlNode":[],  #实际节点数据
#     "tlIndex"[]   #顺序数据，对应节点index
# }
TEMP_TM_NODE_DATA = None
# 节点缓存备份，还原或确定保存后销毁
TEMP_TM_NODE_DATA_BACKUP = None
# 节点缓存初始值
TEMP_TM_NODE_DATA_INIT = {'tlNode':[], 'tlIndex':[]}
# 主界面线程池
ROOT_THREAD_POOL_EXECUTOR = None
# 搜索界面区分大小写
SEARCH_VIEW_NO_IGNORECASE = False
# 所有弹窗界面栈，用于获取当前顶部界面
VIEW_STACK = None
# 需要锁定焦点的界面栈，用于多级弹窗锁定焦点
VIEW_NEED_GRAB_STACK = None




#####次级界面相关
# 搜索界面类型
class ListLineNodeModeEnum():
    P = 0
    R = 1
    F = 2



#----------------class----------------
# 加载tkdnd
class TkDnD:
    def __init__(self, tkroot):
        self._tkroot = tkroot
        tkroot.tk.eval('package require tkdnd')
        # make self an attribute of the parent window for easy access in child classes
        tkroot.dnd = self
    
    def bindsource(self, widget, type=None, command=None, arguments=None, priority=None):
        '''Register widget as drag source; for details on type, command and arguments, see bindtarget().
        priority can be a value between 1 and 100, where 100 is the highest available priority (default: 50).
        If command is omitted, return the current binding for type; if both type and command are omitted,
        return a list of registered types for widget.'''
        command = self._generate_callback(command, arguments)
        tkcmd = self._generate_tkcommand('bindsource', widget, type, command, priority)
        res = self._tkroot.tk.eval(tkcmd)
        if type == None:
            res = res.split()
        return res
    
    def bindtarget(self, widget, type=None, sequence=None, command=None, arguments=None, priority=None):
        '''Register widget as drop target; type may be one of text/plain, text/uri-list, text/plain;charset=UTF-8
        (see the man page tkDND for details on other (platform specific) types);
        sequence may be one of '<Drag>', '<DragEnter>', '<DragLeave>', '<Drop>' or '<Ask>' ;
        command is the callback associated with the specified event, argument is an optional tuple of arguments
        that will be passed to the callback; possible arguments include: %A %a %b %C %c %D %d %L %m %T %t %W %X %x %Y %y
        (see the tkDND man page for details); priority may be a value in the range 1 to 100 ; if there are
        bindings for different types, the one with the priority value will be proceeded first (default: 50).
        If command is omitted, return the current binding for type, where sequence defaults to '<Drop>'.
        If both type and command are omitted, return a list of registered types for widget.'''
        command = self._generate_callback(command, arguments)
        tkcmd = self._generate_tkcommand('bindtarget', widget, type, sequence, command, priority)
        res = self._tkroot.tk.eval(tkcmd)
        if type == None:
            res = res.split()
        return res
    
    def clearsource(self, widget):
        '''Unregister widget as drag source.'''
        self._tkroot.tk.call('dnd', 'clearsource', widget)
    
    def cleartarget(self, widget):
        '''Unregister widget as drop target.'''
        self._tkroot.tk.call('dnd', 'cleartarget', widget)
    
    def drag(self, widget, actions=None, descriptions=None, cursorwindow=None, command=None, arguments=None):
        '''Initiate a drag operation with source widget.'''
        command = self._generate_callback(command, arguments)
        if actions:
            if actions[1:]:
                actions = '-actions {%s}' % ' '.join(actions)
            else:
                actions = '-actions %s' % actions[0]
        if descriptions:
            descriptions = ['{%s}'%i for i in descriptions]
            descriptions = '{%s}' % ' '.join(descriptions)
        if cursorwindow:
            cursorwindow = '-cursorwindow %s' % cursorwindow
        tkcmd = self._generate_tkcommand('drag', widget, actions, descriptions, cursorwindow, command)
        self._tkroot.tk.eval(tkcmd)
                
    def _generate_callback(self, command, arguments):
        '''Register command as tk callback with an optional list of arguments.'''
        cmd = None
        if command:
            cmd = self._tkroot._register(command)
            if arguments:
                cmd = '{%s %s}' % (cmd, ' '.join(arguments))
        return cmd
    
    def _generate_tkcommand(self, base, widget, *opts):
        '''Create the command string that will be passed to tk.'''
        tkcmd = 'dnd %s %s' % (base, widget)
        for i in opts:
            if i is not None:
                tkcmd += ' %s' % i
        return tkcmd





#----------------function----------------
def fixReInputStr(inputStr):
    tempStr = inputStr
    tlReplaceStr = [
        ['\\', '\\\\'],         #斜杠最优先
        ['(', '\\('],
        [')', '\\)'],
        ['[', '\\['],
        [']', '\\]'],
        ['{', '\\{'],
        ['}', '\\}'],
        ['+', '\\+'],
        ['?', '\\?'],
        ['*', '\\*'],
        ['^', '\\^'],
        ['$', '\\$'],
        ['.', '\\.'],
        ['|', '\\|'],
    ]
    for strs in tlReplaceStr:
        tempStr = tempStr.replace(strs[0], strs[1])

    return tempStr


def tkCenter(win, resetSize=False, anchorPos={'x':0.5, 'y':0.5}, forceInScreen=True):
    """
    centers a tkinter window
    :param win: the main window or Toplevel window to center
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    screen_width, screen_height = win.winfo_screenwidth(), win.winfo_screenheight()
    x = round(screen_width * anchorPos['x']) - win_width // 2
    y = round(screen_height * anchorPos['y']) - win_height // 2
    if forceInScreen:
        x = min(max(0, x), screen_width-width)
        y = min(max(0, y), screen_height-height)
    # py3_common.Logging.error(width, height, x, y)
    if resetSize:
        win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    else:
        win.geometry('+{}+{}'.format(x, y))
    win.deiconify()

def showError(self, *args):
    tlErr = traceback.format_exception(*args)
    errStr = ''
    for i in range(0,len(tlErr)):
        errStr += tlErr[i]
    py3_common.Logging.error_(errStr, end='')
    parent = None
    if VIEW_STACK != None and len(VIEW_STACK) > 0:
        parent = VIEW_STACK[-1]
    py3_common.messageboxShowerror('错误', errStr, parent=parent)


# 复制文本到剪贴板
def copyStr2Clipboard(str_):
    if str_ != None and isinstance(str_, str):
        pyperclip.copy(str_)

# 从剪贴板获取文本
def getStrFromClipboard():
    return pyperclip.paste()

# 设置窗口图标
def setWindowIcon(window, iconPath=None):
    if iconPath == None:
        iconPath = WINDOW_ICON_PATH
    if iconPath == None:
        return
    try:
        window.iconbitmap(iconPath)
    except Exception as e:
        # raise e
        pass


# 文件修改时间转日期字符串
def fileStMTimeToDataStr(filePath):
    if not os.path.isfile(filePath):
        return None
    stMTime = os.stat(filePath).st_mtime
    timeArray = time.localtime(stMTime)
    timeStr = time.strftime('%Y-%m-%d_%H-%M-%S', timeArray)
    return timeStr

# 备份配置json文件
def backupJson(filePath, toDir=None):
    if not os.path.isfile(filePath):
        return None
    if toDir == None:
        toDir = JSON_BACKUP_DIR
    py3_common.check_dir(toDir)
    # prefixName, suffixName = py3_common.get_prefix_and_suffix(filePath)
    # timeStr = fileStMTimeToDataStr(filePath)
    # oldFName = os.path.basename(filePath)
    # newFName = prefixName + '_' + timeStr + suffixName
    # newFPath = os.path.realpath(os.path.join(toDir, newFName))
    # i = 1
    # while os.path.isfile(newFPath):
    #     newFName = prefixName + '_' + timeStr + '(' + str(i) + ')' + suffixName
    #     i += 1
    #     newFPath = os.path.realpath(os.path.join(toDir, newFName))
    # py3_common.renameFile(os.path.dirname(filePath), oldFName, newFName, toDir)
    newFName = getBackupJsonName(filePath, toDir)
    newFPath = os.path.realpath(os.path.join(toDir, newFName))
    if os.path.isfile(newFPath):
        py3_common.delete_file_folder(newFPath)
    py3_common.check_dir(os.path.dirname(newFPath))
    py3_common.copy_file_in_dir(filePath, newFPath)
    return newFPath

# 将缓存备份到文件
def backupTempJson(jList, filePath, toDir):
    newFName = getBackupJsonName(filePath, toDir, useFileTime=False)
    newFPath = os.path.realpath(os.path.join(toDir, newFName))
    if os.path.isfile(newFPath):
        py3_common.delete_file_folder(newFPath)
    py3_common.check_dir(os.path.dirname(newFPath))
    dumpNodesConfigList(jList, newFPath, print_dump_path=True)
    return newFPath

# 将缓存导出到文件
def exportTempJson(jList, filePath, isNodesConfig=False):
    if os.path.isfile(filePath):
        py3_common.delete_file_folder(filePath)
    py3_common.check_dir(os.path.dirname(filePath))
    print_dump_path = True
    if isNodesConfig:
        dumpNodesConfigList(jList, filePath, print_dump_path=print_dump_path)
    else:
        py3_common.dumpJsonFromList(filePath, jList, 2, print_dump_path=print_dump_path)

# 获取备份文件名（添加日期信息）
def getBackupJsonName(filePath, toDir=None, useFileTime=True):
    timeStr = ''
    if os.path.isfile(filePath) and useFileTime:
        timeStr = fileStMTimeToDataStr(filePath)
    else:
        timeStamp = time.time()
        timeArray = time.localtime(timeStamp)
        timeStr = time.strftime('%Y-%m-%d_%H-%M-%S', timeArray)
    prefixName, suffixName = py3_common.get_prefix_and_suffix(filePath)
    oldFName = os.path.basename(filePath)
    newFName = prefixName + '_' + timeStr + suffixName

    # if toDir != None and os.path.isdir(toDir):
    #     i = 1
    #     while os.path.isfile(os.path.join(toDir, newFName)):
    #         newFName = prefixName + '_' + timeStr + '(' + str(i) + ')' + suffixName
    #         i += 1

    return newFName

# 弹出初始化错误提示
def showTlInitErrorMsg():
    global TL_INIT_ERROR_MSG
    if len(TL_INIT_ERROR_MSG) > 0:
        for i in range(0,len(TL_INIT_ERROR_MSG)):
            messagebox.showerror('错误', TL_INIT_ERROR_MSG[i])
        TL_INIT_ERROR_MSG = list()

# 刷新项目设置
def refreshProjectSetting():
    if os.path.isfile(SETTING_CONFIG_JSON_PATH):
        jList = py3_common.loadJsonToList(SETTING_CONFIG_JSON_PATH)
        if jList == None or not isinstance(jList, dict):
            # jList = list()
            backupFilePath = backupJson(SETTING_CONFIG_JSON_PATH, JSON_ERROR_BACKUP_DIR)
            errStr = '读取设置失败，已备份至"%s"' % backupFilePath
            # messagebox.showerror('错误', errStr)
            global TL_INIT_ERROR_MSG
            TL_INIT_ERROR_MSG.append(errStr)
        else:
            # 刷新window透明度
            if 'windowAlpha' in jList:
                global WINDOW_ALPHA
                WINDOW_ALPHA = jList['windowAlpha']
            # # 刷新节点类型列表
            # if 'tlSettingKey' in jList:
            #     global TL_SETTING_KEY
            #     TL_SETTING_KEY = jList['tlSettingKey']
            # 刷新风格
            if 'styleType' in jList:
                global STYLE_TYPE
                STYLE_TYPE = jList['styleType']
            # 刷新按钮颜色列表
            if 'tmSettingColor' in jList:
                global TM_BTN_TYPE_COLOR
                TM_BTN_TYPE_COLOR = getTmBtnTypeColorAddDefault(jList['tmSettingColor'])
            # 刷新全局执行前询问开关
            if 'askBeforeExecuting' in jList:
                global ASK_BEFORE_EXECUTING
                ASK_BEFORE_EXECUTING = jList['askBeforeExecuting']
                if ASK_BEFORE_EXECUTING != None:
                    initOptionAskBeforeExecuting(ASK_BEFORE_EXECUTING and True)
            # 刷新禁用右键编辑节点开关
            if 'disableRightClickEditNode' in jList:
                global DISABLE_RCLICK_EDIT_NODE
                DISABLE_RCLICK_EDIT_NODE = jList['disableRightClickEditNode']
            # 刷新各界面位置
            if 'tmViewPos' in jList:
                global TM_VIEW_POS
                TM_VIEW_POS = jList['tmViewPos']
    else:
        saveProjectSetting()

# 保存项目设置
def saveProjectSetting(print_dump_path=True):
    jList = getTmSettingData()
    py3_common.dumpJsonFromList(SETTING_CONFIG_JSON_PATH, jList, 2, print_dump_path=print_dump_path)


# 获取当前设置
def getTmSettingData():
    jList = OrderedDict()
    jList['tmSettingColor'] = getTmBtnTypeColorRemoveDefault()
    jList['windowAlpha'] = WINDOW_ALPHA
    # jList['tlSettingKey'] = TL_SETTING_KEY
    jList['styleType'] = STYLE_TYPE
    jList['askBeforeExecuting'] = ASK_BEFORE_EXECUTING
    jList['disableRightClickEditNode'] = DISABLE_RCLICK_EDIT_NODE
    if bool(TM_VIEW_POS):
        jList['tmViewPos'] = TM_VIEW_POS
    return jList


# 获取排除默认值的颜色清单，用于保存
def getTmBtnTypeColorRemoveDefault(tmColor=None, styleType=None):
    if tmColor == None:
        tmColor = TM_BTN_TYPE_COLOR
    if styleType == None:
        styleType = STYLE_TYPE
    return py3_common.sync_json_field2(TM_BTN_TYPE_COLOR_STYLE_DEFAULT[styleType], tmColor, exclude=True)

# 获取添加默认值的颜色清单，用于读取
def getTmBtnTypeColorAddDefault(tmColor, styleType=None):
    if styleType == None:
        styleType = STYLE_TYPE
    return py3_common.sync_json_field2(TM_BTN_TYPE_COLOR_STYLE_DEFAULT[styleType], tmColor)

# 获取界面位置枚举
def getViewPosEnum(className, exTmViewPos=None):
    if not className:
        return None
    tmViewPos = exTmViewPos or TM_VIEW_POS or {}
    if className in tmViewPos:
        return tmViewPos[className]
    if className in TM_DEFAULT_VIEW_POS:
        return TM_DEFAULT_VIEW_POS[className]
    return None

# 根据界面位置枚举获取界面位置锚点
def getViewPosAnchorWithViewPosEnum(viewPosEnum):
    if viewPosEnum == None or not viewPosEnum in TM_DEFAULT_VIEW_POS_ANCHOR:
        return None
    return py3_common.deep_copy_dict(TM_DEFAULT_VIEW_POS_ANCHOR[viewPosEnum])

# 获取界面位置锚点
def getViewPosAnchor(className, exTmViewPos=None):
    viewPosEnum = getViewPosEnum(className, exTmViewPos=exTmViewPos)
    return getViewPosAnchorWithViewPosEnum(viewPosEnum)


# 刷新节点列表
def refreshNodesConfig():
    # global TEMP_NODE_LIST
    global TEMP_TM_NODE_DATA
    global TL_INIT_ERROR_MSG
    if os.path.isfile(NODES_CONFIG_JSON_PATH):
        jList = py3_common.loadJsonToList(NODES_CONFIG_JSON_PATH)
        # if jList and 'nodeList' in jList:
        #     TEMP_NODE_LIST = jList['nodeList']
        # 数据有问题，要先备份下
        if jList == None or not isinstance(jList, list):
            # jList = list()
            backupFilePath = backupJson(NODES_CONFIG_JSON_PATH, JSON_ERROR_BACKUP_DIR)
            errStr = '读取节点配置失败，已备份至"%s"' % backupFilePath
            # messagebox.showerror('错误', errStr)
            TL_INIT_ERROR_MSG.append(errStr)
            jList = list()
        # TEMP_NODE_LIST = jList

        # 新结构缓存
        tmTemp = dict()
        tmTemp['tlNode'] = jList
        tlIndex = list()
        for i in range(0,len(jList)):
            tlIndex.append(i)
        tmTemp['tlIndex'] = tlIndex
        TEMP_TM_NODE_DATA = tmTemp
    else:
        # if TEMP_NODE_LIST != None and len(TEMP_NODE_LIST) > 0:
        #     backupFilePath = backupTempJson(TEMP_NODE_LIST, NODES_CONFIG_JSON_PATH, JSON_BACKUP_DIR)
        #     errStr = '节点配置文件丢失，已将当前节点数据备份至"%s"' % backupFilePath
        #     TL_INIT_ERROR_MSG.append(errStr)
        # TEMP_NODE_LIST = list()

        if TEMP_TM_NODE_DATA != None and 'tlIndex' in TEMP_TM_NODE_DATA and len(TEMP_TM_NODE_DATA['tlIndex']) > 0:
            backupFilePath = backupTempJson(TEMP_TM_NODE_DATA, NODES_CONFIG_JSON_PATH, JSON_BACKUP_DIR)
            errStr = '节点配置文件丢失，已将当前节点数据备份至"%s"' % backupFilePath
            TL_INIT_ERROR_MSG.append(errStr)
        TEMP_TM_NODE_DATA = py3_common.deep_copy_dict(TEMP_TM_NODE_DATA_INIT)

# 初始化节点列表
def initNodesConfig():
    # global TEMP_NODE_LIST
    global TEMP_TM_NODE_DATA
    refreshNodesConfig()
    # if not TEMP_NODE_LIST:
    #     TEMP_NODE_LIST = list()
    if not TEMP_TM_NODE_DATA:
        TEMP_TM_NODE_DATA = py3_common.deep_copy_dict(TEMP_TM_NODE_DATA_INIT)


# 创建节点配置json
def createNodesConfigJson():
    # jList = TEMP_NODE_LIST
    jList = TEMP_TM_NODE_DATA
    if jList == None or not isinstance(jList, dict):
        jList = py3_common.deep_copy_dict(TEMP_TM_NODE_DATA_INIT)
    dumpNodesConfigList(jList)

# 按各项单行格式保存list到文件
def dumpListToJsonFile(jList, path, print_dump_path=True):
    # 自定义格式化
    jStr = '['
    for i in range(0,len(jList)):
        data = jList[i]
        content = json.dumps(data, ensure_ascii=False, indent=None, sort_keys=False)
        jStr += (',' if i != 0 else '') + '\n  ' + content
    jStr += '\n]'
    # print(jStr)
    py3_common.check_dir(os.path.dirname(path))
    with open(path,"wb") as _config:
        try:
            _config.write(jStr.encode('utf-8'))
        finally:
            _config.close()
        if print_dump_path:
            py3_common.Logging.info("写入json:%s" % path)
        return True
    return False

# 保存节点配置
def dumpNodesConfigList(jList=None, path=None, print_dump_path=True):
    if jList == None:
        # jList = TEMP_NODE_LIST
        jList = TEMP_TM_NODE_DATA
    # py3_common.Logging.debug(jList)
    if path == None:
        path = NODES_CONFIG_JSON_PATH
    tlNodeData = list()
    # for i in range(0,len(jList)):
    #     nodeData = jList[i]
    #     if nodeData['nodeType'] != 'Create':
    #         tlNodeData.append(nodeData)
    tlIndex = jList['tlIndex']
    tlNode = jList['tlNode']
    for i in range(0,len(tlIndex)):
        index = tlIndex[i]
        if index >= 0 and index < len(tlNode):
            tlNodeData.append(tlNode[index])
    return dumpListToJsonFile(tlNodeData, path, print_dump_path=print_dump_path)

# 记录删除节点
def addDeletedNodeBackup(nodeConfig):
    tlDeletedNode = None
    if os.path.isfile(DELETED_NODES_BACKUP_JSON_PATH):
        tlDeletedNode = py3_common.loadJsonToList(DELETED_NODES_BACKUP_JSON_PATH)
    if tlDeletedNode == None or not isinstance(tlDeletedNode, list):
        tlDeletedNode = list()
    tlDeletedNode.append(nodeConfig)
    # py3_common.dumpJsonFromList(DELETED_NODES_BACKUP_JSON_PATH, tlDeletedNode, 2, print_dump_path=True)
    return dumpListToJsonFile(tlDeletedNode, DELETED_NODES_BACKUP_JSON_PATH, print_dump_path=True)

# 获取标准格式节点数据
def getStandardNodeData(nodeData):
    tempData = py3_common.deep_copy_dict(nodeData)

    # 筛选保留字段
    try:
        key = getSettingKey(tempData)
        tlSaveKey = set()

        for k in TMTL_BASE_KEY[tempData['nodeType']]:
            tlSaveKey.add(k)

        tlAdvSaveKey = TMTL_TYPE_ADV_KEY[key]
        for k in tlAdvSaveKey:
            tlSaveKey.add(k)

        tlDelKey = list()
        for k in tempData:
            if not k in tlSaveKey:
                tlDelKey.append(k)
        for k in tlDelKey:
            del tempData[k]
    except Exception as e:
        py3_common.Logging.error(e)

    return tempData

# 创建颜色配置json
def createSettingConfigJson():
    saveProjectSetting()

# 获取颜色，例：getColorWithTlKey(['folder', 'bgColor'])
def getColorWithTlKey(tlKey, default=False, styleType=None):
    temp = TM_BTN_TYPE_COLOR_STYLE_DEFAULT[styleType if styleType != None else STYLE_TYPE] if default else TM_BTN_TYPE_COLOR
    value, suc = py3_common.getValueWithTlKey(temp, tlKey)
    return value

def getColorWithTlKeyAutoDefault(tlKey):
    colorTemp = getColorWithTlKey(tlKey)
    if not colorTemp:
        colorTemp = getColorWithTlKey(tlKey, True)
    return colorTemp

def setColorWithTlKey(tlKey, color):
    # global TM_BTN_TYPE_COLOR
    temp = TM_BTN_TYPE_COLOR
    for i in range(0,len(tlKey)):
        if i == len(tlKey) - 1:
            temp[tlKey[i]] = color
        else:
            if not tlKey[i] in temp:
                temp[tlKey[i]] = dict()
            temp = temp[tlKey[i]]
    # saveProjectSetting()

def configureTkObjectColor(tkObject):
    className = tkObject.winfo_class()
    fc_ = getColorWithTlKeyAutoDefault
    # py3_common.Logging.debug2(className)
    if className == 'Entry':
        tkObject.configure(bg=fc_(['common', 'tkEntry', 'bgColor']), fg=fc_(['common', 'fgColor']),
                    selectbackground=fc_(['common', 'tkEntry', 'selectBgColor']), selectforeground=fc_(['common', 'tkEntry', 'selectFgColor']),
                    disabledbackground=fc_(['common', 'tkEntry', 'disabledBgColor']), disabledforeground=fc_(['common', 'tkEntry', 'disabledFgColor']),
                    insertbackground=fc_(['common', 'tkEntry', 'insertbackground']))
    elif className == 'Text':
        tkObject.configure(bg=fc_(['common', 'tkEntry', 'bgColor']), fg=fc_(['common', 'fgColor']),
                    selectbackground=fc_(['common', 'tkEntry', 'selectBgColor']), selectforeground=fc_(['common', 'tkEntry', 'selectFgColor']),
                    insertbackground=fc_(['common', 'tkEntry', 'insertbackground']))
    elif className == 'Label':
        tkObject.configure(bg=fc_(['common', 'bgColor']), fg=fc_(['common', 'fgColor']))
    elif className == 'Frame' or className == 'Toplevel' or className == 'Panedwindow':
        tkObject.configure(bg=fc_(['common', 'bgColor']))
    elif className == 'Radiobutton':
        tkObject.configure(bg=fc_(['common', 'bgColor']), fg=fc_(['common', 'fgColor']), selectcolor=fc_(['common', 'bgColor']), activebackground=fc_(['common', 'bgColor']), activeforeground=fc_(['common', 'fgColor']))
    elif className == 'Button':
        tkObject.configure(bg=fc_(['common', 'bgColor']), fg=fc_(['common', 'btnFgColor']), activebackground=fc_(['common', 'bgColor']), activeforeground=fc_(['common', 'btnFgColor']), disabledforeground=fc_(['common', 'btnDisabledFgColor']))
    elif className == 'Canvas':
        tkObject.configure(bg=fc_(['common', 'canvasBgColor']))
    elif className == 'Checkbutton':
        tkObject.configure(bg=fc_(['common', 'bgColor']), fg=fc_(['common', 'fgColor']), selectcolor=fc_(['common', 'bgColor']),
                            activebackground=fc_(['common', 'bgColor']), activeforeground=fc_(['common', 'fgColor']), disabledforeground=fc_(['common', 'btnDisabledFgColor']))
    elif className == 'Scale':
        tkObject.configure(bg=fc_(['common', 'bgColor']), fg=fc_(['common', 'fgColor']), activebackground=fc_(['common', 'bgColor']), troughcolor=fc_(['common', 'ttkScrollbar', 'background', 'normal']))
    elif className == 'Listbox':
        tkObject.configure(bg=fc_(['common', 'tkEntry', 'bgColor']), fg=fc_(['common', 'fgColor']),
                            disabledforeground=fc_(['common', 'tkEntry', 'disabledBgColor']), selectbackground=fc_(['common', 'tkEntry', 'selectBgColor']),
                            selectforeground=fc_(['common', 'tkEntry', 'selectFgColor']))
    elif className == 'Menu':
        tkObject.configure(bg=fc_(['common', 'bgColor']), fg=fc_(['common', 'fgColor']),
                            selectcolor=fc_(['common', 'fgColor']),
                            activebackground=fc_(['common', 'tkMenu', 'selectBgColor']), activeforeground=fc_(['common', 'tkMenu', 'selectFgColor']), disabledforeground=fc_(['common', 'btnDisabledFgColor']))

# 改变tk扩展类颜色
def configureExTkObjectColor(tkObject):
    className = tkObject.__class__.__name__
    fc_ = getColorWithTlKeyAutoDefault
    if className == 'Sheet':
        tkObject.change_theme(theme=fc_(['sheet', 'theme']))
    elif className == 'VirtualListFrame':
        tkObject.configure(bg=fc_(['common', 'canvasBgColor']))
        tkObject.virtualListCanvas.configure(bg=fc_(['common', 'canvasBgColor']))
        tkObject.virtualListCanvas.scrollFrame.configure(bg=fc_(['common', 'canvasBgColor']))

# 改变ttk风格颜色
def configureTtkStyle(rootTk = None):
    if rootTk == None:
        rootTk = INIT_WINDOW
    # print(getColorWithTlKeyAutoDefault(['common', 'bgColor']))
    # windows无效
    # self.mbar.configure(background='black', fg='white', activebackground='#004c99', activeforeground='white')
    fc_ = getColorWithTlKeyAutoDefault
    # self.configure(bg=fc_(['common', 'bgColor']))
    # configureTkObjectColor(self)
    # # self.panelWindow1.configure(bg=fc_(['common', 'bgColor']))
    # configureTkObjectColor(self.panelWindow1)
    # # self.frameMain.configure(bg=fc_(['common', 'bgColor']))
    # configureTkObjectColor(self.frameMain)
    # # self.frameMode.configure(bg=fc_(['common', 'bgColor']))
    # configureTkObjectColor(self.frameMode)
    # # self.frameModeSelectBtn.configure(bg=fc_(['common', 'bgColor']))
    # configureTkObjectColor(self.frameModeSelectBtn)
    # # self.frameModeLabel.configure(bg=fc_(['common', 'bgColor']), fg=fc_(['common', 'fgColor']))
    # configureTkObjectColor(self.frameModeLabel)
    # for i in range(0,len(self.tlModeRadiobutton)):
    #     # self.tlModeRadiobutton[i].configure(bg=fc_(['common', 'bgColor']), fg=fc_(['common', 'fgColor']), selectcolor=fc_(['common', 'bgColor']), activebackground=fc_(['common', 'bgColor']), activeforeground=fc_(['common', 'fgColor']))
    #     configureTkObjectColor(self.tlModeRadiobutton[i])

    # self.virtualListFrame.configure(bg=fc_(['common', 'canvasBgColor']))
    # self.virtualListFrame.virtualListCanvas.configure(bg=fc_(['common', 'canvasBgColor']))
    # self.virtualListFrame.virtualListCanvas.scrollFrame.configure(bg=fc_(['common', 'canvasBgColor']))
    # # self.virtualListFrame.canvasVsb.configure(bg='blue')

    tlStyleKeyMark = list()
    def fc_mark(tlKey):
        tlStyleKeyMark.append(tlKey)
        return fc_(tlKey)

    style = ttk.Style()
    # py3_common.Logging.debug(ttk.Style.__init__.__code__.co_varnames)
    # py3_common.Logging.debug(style.configure.__code__.co_varnames)
    # py3_common.Logging.debug('theme_names', style.theme_names())
    # ('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
    # style.theme_use('clam')
    style.theme_use('default')
    style.configure("Vertical.TScrollbar", gripcount=0, borderwidth=0, arrowsize=16,
                    # sliderrelief='flat',
                    background=fc_mark(['common', 'ttkScrollbar', 'background', 'normal']),
                    # foreground='yellow',
                    # darkcolor="yellow",
                    # lightcolor="yellow",
                    troughcolor=fc_mark(['common', 'ttkScrollbar', 'troughcolor']),
                    # bordercolor="yellow",
                    # arrowcolor=fc_mark(['common', 'ttkScrollbar', 'arrowcolor', 'normal']))
                    arrowcolor=fc_mark(['common', 'fgColor']))
    style.map('Vertical.TScrollbar',
                background=[('active', fc_mark(['common', 'ttkScrollbar', 'background', 'active'])),
                            ('disabled', fc_mark(['common', 'ttkScrollbar', 'background', 'disabled']))],
                            # ('readonly', fc_mark(['common', 'ttkScrollbar', 'background', 'disabled']))],
                # foreground=[('active', 'yellow'), ('disabled', 'yellow')],
                arrowcolor=[('disabled', fc_mark(['common', 'ttkScrollbar', 'arrowcolor', 'disabled']))])
    style.configure("Horizontal.TScrollbar", gripcount=0, borderwidth=0, arrowsize=16,
                    # sliderrelief='flat',
                    background=fc_mark(['common', 'ttkScrollbar', 'background', 'normal']),
                    # foreground='yellow',
                    # darkcolor="yellow",
                    # lightcolor="yellow",
                    troughcolor=fc_mark(['common', 'ttkScrollbar', 'troughcolor']),
                    # bordercolor="yellow",
                    # arrowcolor=fc_mark(['common', 'ttkScrollbar', 'arrowcolor', 'normal']))
                    arrowcolor=fc_mark(['common', 'fgColor']))
    style.map('Horizontal.TScrollbar',
                background=[('active', fc_mark(['common', 'ttkScrollbar', 'background', 'active'])),
                            ('disabled', fc_mark(['common', 'ttkScrollbar', 'background', 'disabled']))],
                            # ('readonly', fc_mark(['common', 'ttkScrollbar', 'background', 'disabled']))],
                # foreground=[('active', 'yellow'), ('disabled', 'yellow')],
                arrowcolor=[('disabled', fc_mark(['common', 'ttkScrollbar', 'arrowcolor', 'disabled']))])
    style.configure("TCombobox", gripcount=0, borderwidth=1, arrowsize=16, selectborderwidth=0,
                    # sliderrelief='flat',
                    # background=fc_mark(['common', 'ttkCombobox', 'background', 'normal']),
                    background=fc_mark(['common', 'bgColor']),
                    # foreground=fc_mark(['common', 'ttkCombobox', 'foreground', 'normal']),
                    foreground=fc_mark(['common', 'fgColor']),
                    # fieldbackground=fc_mark(['common', 'ttkCombobox', 'fieldbackground', 'normal']),
                    fieldbackground=fc_mark(['common', 'tkEntry', 'bgColor']),
                    # darkcolor="yellow",
                    # lightcolor="yellow",
                    troughcolor=fc_mark(['common', 'ttkCombobox', 'troughcolor']),
                    # bordercolor="yellow",
                    # arrowcolor=fc_mark(['common', 'ttkCombobox', 'arrowcolor', 'normal']))
                    arrowcolor=fc_mark(['common', 'fgColor']),
                    selectbackground=fc_mark(['common', 'tkEntry', 'selectBgColor']),
                    selectforeground=fc_mark(['common', 'tkEntry', 'selectFgColor'])
                    # selectforeground=fc_mark(['common', 'ttkCombobox', 'selectforeground']),
                    # insertcolor=fc_mark(['common', 'ttkCombobox', 'insertcolor'])
                    )
    rootTk.option_add('*TCombobox*Listbox*Background', fc_mark(['common', 'tkEntry', 'bgColor']))
    rootTk.option_add('*TCombobox*Listbox*Foreground', fc_mark(['common', 'fgColor']))
    rootTk.option_add('*TCombobox*Listbox*selectBackground', fc_mark(['common', 'tkEntry', 'selectBgColor']))
    rootTk.option_add('*TCombobox*Listbox*selectForeground', fc_mark(['common', 'tkEntry', 'selectFgColor']))
    # rootTk.option_add('Menu*bordercolor', fc_mark(['common', 'bgColor']))
    style.map('TCombobox',
                background=[('active', fc_mark(['common', 'ttkScrollbar', 'background', 'active'])),
                            ('disabled', fc_mark(['common', 'ttkCombobox', 'background', 'disabled'])),
                            # ('readonly', fc_mark(['common', 'ttkCombobox', 'background', 'readonly']))],
                            ('readonly', fc_mark(['common', 'bgColor']))],
                foreground=[('active', fc_mark(['common', 'ttkCombobox', 'foreground', 'active'])),
                            ('disabled', fc_mark(['common', 'ttkCombobox', 'foreground', 'disabled'])),
                            # ('readonly', fc_mark(['common', 'ttkCombobox', 'foreground', 'readonly']))],
                            ('readonly', fc_mark(['common', 'fgColor']))],
                fieldbackground=[('active', fc_mark(['common', 'tkEntry', 'bgColor'])),
                            ('disabled', fc_mark(['common', 'tkEntry', 'disabledBgColor'])),
                            # ('readonly', fc_mark(['common', 'ttkCombobox', 'fieldbackground', 'readonly']))],
                            ('readonly', fc_mark(['common', 'tkEntry', 'bgColor']))],
                arrowcolor=[('disabled', fc_mark(['common', 'ttkScrollbar', 'arrowcolor', 'disabled']))])
    style.configure("TSeparator", gripcount=0, borderwidth=1, arrowsize=16, selectborderwidth=0,
                    background=fc_mark(['common', 'bgColor']),
                    )
    style.configure("Horizontal.TProgressbar", gripcount=0, borderwidth=0, arrowsize=16,
                    # sliderrelief='groove',
                    background=fc_mark(['common', 'ttkProgressbar', 'background']),
                    # foreground='yellow',
                    # darkcolor="yellow",
                    # lightcolor="yellow",
                    troughcolor=fc_mark(['common', 'ttkScrollbar', 'troughcolor']),
                    # bordercolor="yellow",
                    # arrowcolor=fc_mark(['common', 'ttkScrollbar', 'arrowcolor', 'normal']))
                    # arrowcolor=fc_mark(['common', 'fgColor'])
                    )

    isAllDefault = True
    for k in tlStyleKeyMark:
        rgbCn = tuple((c//256 for c in rootTk.winfo_rgb(getColorWithTlKeyAutoDefault(k))))
        rgbCd = tuple((c//256 for c in rootTk.winfo_rgb(getColorWithTlKey(k, True, StyleEnum.Default))))
        if rgbCn[0] != rgbCd[0] or rgbCn[1] != rgbCd[1] or rgbCn[2] != rgbCd[2]:
            isAllDefault = False
            break
    if isAllDefault:
        style.theme_use('vista')


def getSettingKey(data):
    if 'nodeType' in data and data['nodeType'] == 'Line':
        return 'line'
    elif 'typeStr' in data:
        return data['typeStr']
    return None


# 设置主界面透明度
def setInitWindowAlpha(alpha=None):
    if alpha == None:
        alpha = WINDOW_ALPHA
    if INIT_WINDOW:
        INIT_WINDOW.attributes("-alpha", alpha/100.0)



########选项
# 初始化执行前提示
def initOptionAskBeforeExecuting(initValue=False):
    global ASK_BEFORE_EXECUTING
    if ASK_BEFORE_EXECUTING == None or not isinstance(ASK_BEFORE_EXECUTING, dict):
        ASK_BEFORE_EXECUTING = dict()
        for i in range(0,len(TL_SETTING_KEY)):
            key = TL_SETTING_KEY[i]
            if key != 'line':
                ASK_BEFORE_EXECUTING[key] = initValue

def getOptionAskBeforeExecuting(typeStr):
    if ASK_BEFORE_EXECUTING != None and typeStr in ASK_BEFORE_EXECUTING:
        return ASK_BEFORE_EXECUTING[typeStr]
    return False

def setOptionAskBeforeExecuting(typeStr, value):
    global ASK_BEFORE_EXECUTING
    if ASK_BEFORE_EXECUTING == None or not isinstance(ASK_BEFORE_EXECUTING, dict):
        initOptionAskBeforeExecuting()
    ASK_BEFORE_EXECUTING[typeStr] = value

# 初始化各种选项
def initOptions():
    initOptionAskBeforeExecuting()
initOptions()



########模块
# 模块导入，本来写在入口py的，说不定会炸
TM_IMPORT_MODULE = dict()
def getImportModule(moduleName):
    global TM_IMPORT_MODULE
    if not moduleName in TM_IMPORT_MODULE:
        TM_IMPORT_MODULE[moduleName] = import_module(moduleName)
    # TM_IMPORT_MODULE[moduleName].setDebug(False)
    return TM_IMPORT_MODULE[moduleName]

def getModuleNameWithTypeStr(typeStr):
    moduleBase = 'script.nodeScript'
    scriptName = py3_common.upper_or_lower_first_char(typeStr) + 'Script'
    scriptPath = os.path.join('.', moduleBase, scriptName + '.py')
    # if not os.path.isfile(scriptPath):
    #     scriptName = 'BaseScript'
    return moduleBase + '.' + scriptName

# 初始化引入一下，防止被释放
def initImportModules():
    for key in TL_SETTING_KEY:
        getImportModule(getModuleNameWithTypeStr(key))
initImportModules()


########事件
# 初始化事件代理
def initEventProxy():
    global EVENT_PROXY
    if EVENT_PROXY == None:
        EVENT_PROXY = EventProxy(IS_DEBUG, IS_EVENTPROXY_SHOW_ARGS)

# 添加事件监听
def addEventListener(eventType, fCallback):
    if EVENT_PROXY == None:
        return None
    return EVENT_PROXY.addEventListener(eventType, fCallback)

# 移除事件监听
def removeEventListener(handle):
    if EVENT_PROXY == None:
        return False
    return EVENT_PROXY.removeEventListener(handle)

# 移除多个事件监听
def removeTlEventListener(tlHandle):
    if EVENT_PROXY == None:
        return
    EVENT_PROXY.removeTlEventListener(tlHandle)

# 派发事件
def dispatchEvent(eventType, *args):
    if EVENT_PROXY == None:
        return
    EVENT_PROXY.dispatchEvent(eventType, *args)






initEventProxy()
initNodesConfig()
refreshProjectSetting()


# 初始化json
if not os.path.isfile(NODES_CONFIG_JSON_PATH):
    py3_common.Logging.info(u'没有找到节点配置json，初始化')
    createNodesConfigJson()
if not os.path.isfile(SETTING_CONFIG_JSON_PATH):
    py3_common.Logging.info(u'没有找到设定配置json，初始化')
    createSettingConfigJson()



########界面栈相关
def initViewNeedGrabEventListen():
    addEventListener(EventType.Event_ViewShow, onEvent_ViewShow)
    addEventListener(EventType.Event_ViewClose, onEvent_ViewClose)
    addEventListener(EventType.Event_ViewFocusIn, onEvent_ViewFocusIn)
    addEventListener(EventType.Event_ViewNeedGrabShow, onEvent_ViewNeedGrabShow)
    addEventListener(EventType.Event_ViewNeedGrabClose, onEvent_ViewNeedGrabClose)

def onEvent_ViewShow(view):
    if VIEW_STACK == None:
        return
    VIEW_STACK.append(view)

def onEvent_ViewClose(view):
    if VIEW_STACK == None:
        return
    if len(VIEW_STACK) > 0:
        tlDelIndex = list()
        for i in range(0,len(VIEW_STACK)):
            if view == VIEW_STACK[i]:
                tlDelIndex.append(i)
        for i in range(len(tlDelIndex)-1,-1,-1):
            del VIEW_STACK[tlDelIndex[i]]
        # 重设焦点
        def fHelper(v):
            v.focus_force()
            try:
                v.reFocusOldFocusWidget()
            except Exception as e:
                raise e
        if len(VIEW_STACK) > 0:
            view = VIEW_STACK[len(VIEW_STACK)-1]
            view.after(1, lambda v=view: fHelper(v))
        else:
            # 没弹窗了定焦点到主窗口
            INIT_WINDOW_GUI.after(1, lambda v=INIT_WINDOW_GUI: fHelper(v))

def onEvent_ViewFocusIn(view):
    if VIEW_STACK == None:
        return
    if len(VIEW_STACK) > 0:
        if VIEW_STACK[len(VIEW_STACK)-1] == view:
            return
        tlDelIndex = list()
        for i in range(0,len(VIEW_STACK)):
            if view == VIEW_STACK[i]:
                tlDelIndex.append(i)
        for i in range(len(tlDelIndex)-1,-1,-1):
            del VIEW_STACK[tlDelIndex[i]]
    VIEW_STACK.append(view)

def hasSameClassView(view):
    if VIEW_STACK == None or len(VIEW_STACK) == 0:
        return False
    viewClassName = view.__class__.__name__
    for i in range(0,len(VIEW_STACK)):
        cName = VIEW_STACK[i].__class__.__name__
        if viewClassName == cName:
            return True
    return False

def getTlViewByClassName(viewClassName):
    if VIEW_STACK == None or len(VIEW_STACK) == 0:
        return None
    tlView = list()
    for i in range(0,len(VIEW_STACK)):
        view = VIEW_STACK[i]
        cName = view.__class__.__name__
        if viewClassName == cName:
            tlView.append(view)
    if len(tlView) > 0:
        return tlView
    return None

def onEvent_ViewNeedGrabShow(view):
    if VIEW_NEED_GRAB_STACK == None:
        return
    VIEW_NEED_GRAB_STACK.append(view)
    # 锁定焦点
    view.grab_set()

def onEvent_ViewNeedGrabClose(view):
    if VIEW_NEED_GRAB_STACK == None:
        return
    if len(VIEW_NEED_GRAB_STACK) > 0:
        tlDelIndex = list()
        for i in range(0,len(VIEW_NEED_GRAB_STACK)):
            if view == VIEW_NEED_GRAB_STACK[i]:
                tlDelIndex.append(i)
        for i in range(len(tlDelIndex)-1,-1,-1):
            del VIEW_NEED_GRAB_STACK[tlDelIndex[i]]
    if len(VIEW_NEED_GRAB_STACK) > 0:
        # 锁定焦点
        VIEW_NEED_GRAB_STACK[len(VIEW_NEED_GRAB_STACK)-1].grab_set()

initViewNeedGrabEventListen()





########其他事件相关
def initViewOtherEventListen():
    addEventListener(EventType.Event_SettingColorChange, onEvent_SettingColorChange)

# 风格改变
def onEvent_SettingColorChange():
    configureTtkStyle()

initViewOtherEventListen()
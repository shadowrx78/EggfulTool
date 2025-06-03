#! python3
# -*- coding: utf-8 -*-

import os, re, subprocess
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter.messagebox import showerror
from .. import py3_common
from .. import GlobalValue

SCRIPT_NAME = 'ExeScript'
DEBUG = True
def setDebug(debug=False):
    global DEBUG
    DEBUG = debug


REL_PATH_VAR = None
# 修改界面
def createEditUi(frame, tmExUi, data, cTkObjFun, dnd=None, tmExFun=None, tmExObj=None):
    if DEBUG:
        py3_common.Logging.debug('-----%s createEditUi-----' % SCRIPT_NAME)

    frame.columnconfigure(0,weight=1)
    # 路径文本框
    frameLabelPath = Frame(frame)
    frameLabelPath.grid(row=0,column=0,sticky='ew')
    cTkObjFun(frameLabelPath)
    labelPath = Label(frameLabelPath, text='路径：(只能一条)', anchor='w')
    labelPath.grid(row=0,column=0,sticky='ew')
    cTkObjFun(labelPath)

    # 相对路径
    global REL_PATH_VAR
    REL_PATH_VAR = IntVar()
    REL_PATH_VAR.set(0)
    checkbuttonRelPath = Checkbutton(frameLabelPath, text=str('相对路径'), variable=REL_PATH_VAR, command=lambda v=REL_PATH_VAR:True)
    # checkbuttonDrop.grid(row=0, column=1, padx=10)
    checkbuttonRelPath.grid(row=0, column=1, sticky='w', padx=10)
    cTkObjFun(checkbuttonRelPath)

    entryPath = tmExObj['UndoEntry'](frame)
    py3_common.bindTkEditorRightClick(entryPath, frame, tkThemeHelper=tmExObj['tkThemeHelper'])
    entryPath.grid(row=1,column=0,sticky='ew',padx=4,ipady=10)
    cTkObjFun(entryPath, isForceRaw=True)
    tmExUi['entryPath'] = entryPath
    if dnd:
        dnd.bindtarget(entryPath, 'text/uri-list', '<Drop>', lambda files,tmExUi=tmExUi:onEntryPathDrop(tmExUi, files), ('%D',))

    # 初始化
    if 'exePath' in data:
        py3_common.setEntryText(entryPath, data['exePath'])
        try:
            entryPath.clearLog()
        except Exception as e:
            pass


def onEntryPathDrop(tmExUi, files=''):
    if not 'entryPath' in tmExUi:
        return
    tlFile = py3_common.parseDndFiles(files)
    if not os.path.isfile(tlFile[0]):
        messagebox.showerror('错误','不是文件路径', parent=tmExUi['entryPath'])
        return
    filePath = os.path.normpath(tlFile[0])
    if REL_PATH_VAR.get() > 0:
        try:
            filePath = os.path.normpath(os.path.relpath(tlFile[0], '.'))
        except Exception as e:
            pass
    py3_common.setEntryText(tmExUi['entryPath'], filePath)

# 保存数据
def saveData(tmExUi, data):
    if DEBUG:
        py3_common.Logging.debug('-----%s saveData-----' % SCRIPT_NAME)
    text = py3_common.getEntryText(tmExUi['entryPath'])
    if re.search(r'^\s*$', text):
        messagebox.showerror('错误','路径不能为空', parent=tmExUi['entryPath'])
        return False
    if not os.path.isfile(text):
        messagebox.showerror('错误','不是文件路径', parent=tmExUi['entryPath'])
        return False
    data['exePath'] = text
    return True

# 额外的保留字段
def getTlAdvSaveKey():
    # return ['exePath']
    return GlobalValue.TMTL_TYPE_ADV_KEY['exe']

# 按钮操作
def onBtnClick(data=None):
    if DEBUG:
        py3_common.Logging.debug('-----%s onBtnClick-----' % SCRIPT_NAME)
    if data == None:
        return
    path_ = getPath(data)
    if path_ and os.path.isfile(path_):
        if DEBUG:
            py3_common.Logging.debug(os.path.abspath(path_))
        oldWorkPath = os.getcwd()
        pathDisk = getDiskNameByPath(path_)
        os.chdir(os.path.abspath(os.path.dirname(path_)))
        try:
            os.startfile(os.path.abspath(path_))
        except Exception as e:
            raise e
        finally:
            if pathDisk != None:
                os.chdir(pathDisk + ':\\')
            os.chdir(oldWorkPath)
    else:
        messagebox.showerror('错误','文件路径不存在')

# 拖入操作
def onDrop(data=None, tlFile=None):
    if DEBUG:
        py3_common.Logging.debug('-----%s onDrop-----' % SCRIPT_NAME)
    if data == None or tlFile == None or len(tlFile) <= 0:
        return
    path_ = getPath(data)
    if path_ and os.path.isfile(path_):
        cmd = '"%s"' % (path_)
        for fil in tlFile:
            cmd += ' "%s"' % (os.path.abspath(fil))
        if DEBUG:
            py3_common.Logging.debug(cmd)
        oldWorkPath = os.getcwd()
        pathDisk = getDiskNameByPath(path_)
        os.chdir(os.path.abspath(os.path.dirname(path_)))
        try:
            subprocess.Popen(cmd, shell=True)
        except Exception as e:
            raise e
        finally:
            if pathDisk != None:
                os.chdir(pathDisk + ':\\')
            os.chdir(oldWorkPath)

# 根据路径获取盘符
def getDiskNameByPath(path):
    match = re.search(r':', path)
    if not match:
        return None
    diskName = path[:match.start()]
    return diskName

def getPath(data=None, tmExUi=None):
    if DEBUG:
        py3_common.Logging.debug('-----%s getPath-----' % SCRIPT_NAME)
    if tmExUi:
        if 'entryPath' in tmExUi:
            return py3_common.getEntryText(tmExUi['entryPath'])
    else:
        return data['exePath'] if data != None and 'exePath' in data else None
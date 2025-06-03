#! python3
# -*- coding: utf-8 -*-

import os, re, subprocess
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter.messagebox import showerror
from sys import platform
from .. import py3_common
from .. import GlobalValue

SCRIPT_NAME = 'CmdScript'
DEBUG = True
def setDebug(debug=False):
    global DEBUG
    DEBUG = debug

OPEN_NEW_CMD_WINDOW_VAR = None
NOT_CLOSE_VAR = None
AUTO_CD_VAR = None
REL_PATH_VAR = None
# 修改界面
def createEditUi(frame, tmExUi, data, cTkObjFun, dnd=None, tmExFun=None, tmExObj=None):
    if DEBUG:
        py3_common.Logging.debug('-----%s createEditUi-----' % SCRIPT_NAME)
    
    # 命令文本框
    frameLabelCommand = Frame(frame)
    frameLabelCommand.grid(row=0,column=0,sticky='ew')
    cTkObjFun(frameLabelCommand)
    labelCommand = Label(frameLabelCommand, text='命令：', anchor='w')
    labelCommand.grid(row=0,column=0,sticky='ew')
    cTkObjFun(labelCommand)
    btnTipsCommand = Button(frameLabelCommand, text='!', width=3, command=lambda f=frame:onBtnTipsCommandClick(f))
    btnTipsCommand.grid(row=0,column=1)
    cTkObjFun(btnTipsCommand)

    global OPEN_NEW_CMD_WINDOW_VAR
    global NOT_CLOSE_VAR
    global AUTO_CD_VAR
    # 不关闭命令行窗口选中框
    NOT_CLOSE_VAR = IntVar()
    NOT_CLOSE_VAR.set(1 if 'notClose' in data and data['notClose'] else 0)
    checkbuttonNotClose = Checkbutton(frameLabelCommand, text=str('不关闭命令行窗口'), variable=NOT_CLOSE_VAR, command=lambda v=NOT_CLOSE_VAR:True)
    # checkbuttonDrop.grid(row=0, column=1, padx=10)
    checkbuttonNotClose.grid(row=0, column=3, sticky='w')
    cTkObjFun(checkbuttonNotClose)

    # 打开新命令行窗口选中框
    OPEN_NEW_CMD_WINDOW_VAR = IntVar()
    OPEN_NEW_CMD_WINDOW_VAR.set(1 if not 'openNewCmdWindow' in data or data['openNewCmdWindow'] else 0)
    checkbuttonOpenNewCmdWindow = Checkbutton(frameLabelCommand, text=str('打开新命令行窗口'), variable=OPEN_NEW_CMD_WINDOW_VAR, command=lambda v=OPEN_NEW_CMD_WINDOW_VAR,c=checkbuttonNotClose:py3_common.setCheckbuttonEnable(c, v.get() > 0))
    # checkbuttonDrop.grid(row=0, column=1, padx=10)
    checkbuttonOpenNewCmdWindow.grid(row=0, column=2, sticky='w', padx=10)
    cTkObjFun(checkbuttonOpenNewCmdWindow)
    py3_common.setCheckbuttonEnable(checkbuttonNotClose, OPEN_NEW_CMD_WINDOW_VAR.get() > 0)

    # 自动cd选中框
    AUTO_CD_VAR = IntVar()
    AUTO_CD_VAR.set(1 if 'autoCd' in data and data['autoCd'] else 0)
    checkbuttonAutoCd = Checkbutton(frameLabelCommand, text=str('自动cd'), variable=AUTO_CD_VAR, command=lambda v=AUTO_CD_VAR:True)
    # checkbuttonDrop.grid(row=0, column=1, padx=10)
    checkbuttonAutoCd.grid(row=0, column=4, sticky='w', padx=10)
    cTkObjFun(checkbuttonAutoCd)

    textCommand = tmExObj['UndoText'](frame, height=4)
    py3_common.bindTkEditorRightClick(textCommand, frame, tkThemeHelper=tmExObj['tkThemeHelper'])
    textCommand.grid(row=1,column=0,sticky='nsew')
    cTkObjFun(textCommand, isForceRaw=True)
    tmExUi['textCommand'] = textCommand

    textCommandVsb = ttk.Scrollbar(frame,orient="vertical",command=textCommand.yview)
    textCommand.configure(yscrollcommand=textCommandVsb.set)
    textCommandVsb.grid(column=1, row=1, sticky='ns')

    # 路径文本框
    frameLabelPath = Frame(frame)
    frameLabelPath.grid(row=2,column=0,sticky='ew')
    cTkObjFun(frameLabelPath)
    labelPath = Label(frameLabelPath, text='路径：', anchor='w')
    labelPath.grid(row=0,column=0,sticky='ew')
    cTkObjFun(labelPath)
    btnTipsPath = Button(frameLabelPath, text='!', width=3, command=lambda f=frame:onBtnTipsPathClick(f))
    btnTipsPath.grid(row=0,column=1)
    cTkObjFun(btnTipsPath)

    # 选择路径
    labelpathCombobox = Label(frameLabelPath, text='选择打开路径下标：', anchor='e')
    labelpathCombobox.grid(row=0,column=3,sticky='ew',padx=10)
    cTkObjFun(labelpathCombobox)
    pathCombobox = ttk.Combobox(frameLabelPath, state='readonly', width=4)
    # pathCombobox['values'] = TL_SETTING_KEY
    # pathCombobox.current(0)
    pathCombobox.bind("<<ComboboxSelected>>",lambda f=frame,tmExUi=tmExUi,data=data:onPathComboboxSelect(f, tmExUi, data))
    pathCombobox.bind("<Button-1>", lambda e,tmExUi=tmExUi:refreshPathCombobox(tmExUi))
    if platform == "linux" or platform == "linux2":
        pathCombobox.unbind_class("TCombobox", "<Button-4>")
        pathCombobox.unbind_class("TCombobox", "<Button-5>")
    else:
        pathCombobox.unbind_class("TCombobox", "<MouseWheel>")
    pathCombobox.grid(row=0,column=4,sticky='w')
    tmExUi['pathCombobox'] = pathCombobox

    # 相对路径
    global REL_PATH_VAR
    REL_PATH_VAR = IntVar()
    REL_PATH_VAR.set(0)
    checkbuttonRelPath = Checkbutton(frameLabelPath, text=str('相对路径'), variable=REL_PATH_VAR, command=lambda v=REL_PATH_VAR:True)
    # checkbuttonDrop.grid(row=0, column=1, padx=10)
    checkbuttonRelPath.grid(row=0, column=2, sticky='w', padx=10)
    cTkObjFun(checkbuttonRelPath)

    textPath = tmExObj['UndoText'](frame, height=4)
    py3_common.bindTkEditorRightClick(textPath, frame, tkThemeHelper=tmExObj['tkThemeHelper'])
    textPath.grid(row=3,column=0,sticky='nsew')
    cTkObjFun(textPath, isForceRaw=True)
    tmExUi['textPath'] = textPath
    if dnd:
        dnd.bindtarget(textPath, 'text/uri-list', '<Drop>', lambda files,tmExUi=tmExUi:onTextPathDrop(tmExUi, files), ('%D',))

    textPathVsb = ttk.Scrollbar(frame,orient="vertical",command=textPath.yview)
    textPath.configure(yscrollcommand=textPathVsb.set)
    textPathVsb.grid(column=1, row=3, sticky='ns')

    # 初始化
    if 'tlFilePath' in data:
        str_ = ''
        for i in range(0,len(data['tlFilePath'])):
            str_ += ('\n' if i != 0 else '') + data['tlFilePath'][i]
        py3_common.setTextText(textPath, str_)
        try:
            textPath.clearLog()
        except Exception as e:
            pass
        refreshPathCombobox(tmExUi)
        pathCombobox.current(0)
    if 'command' in data:
        if isinstance(data['command'], list):
            str_ = ''
            for i in range(0,len(data['command'])):
                str_ += ('\n' if i != 0 else '') + data['command'][i]
            py3_common.setTextText(textCommand, str_)
        else:
            py3_common.setTextText(textCommand, data['command'])
        try:
            textCommand.clearLog()
        except Exception as e:
            pass

def onBtnTipsCommandClick(frame):
    tipsStr = u'''命令：
每行为1条命令，多条命令会同时执行
%p+数字代表第几条路径，%dp+数字代表第几条路径的盘符
%+数字代表第几个拖入文件路径，%d+数字代表第几个拖入文件路径的盘符

例：
python %p0 -s %0
cd %p0 && %dp0 && adb install %0

选项：
自动cd：
使用%p+数字方式表示路径会自动cd到路径下再调用
例如：“py -3 %p0” 会转换成 "cd <%p0的父目录> && <%p0的盘符> && py -3 <%p0的文件名>"
假设“%p0” = “C:\\py\\test.py”，则“py -3 %p0” == “cd C:\\py && C: && py -3 test.py”'''
    messagebox.showinfo('帮助', tipsStr, parent=frame)

def onBtnTipsPathClick(frame):
    tipsStr = u'路径：\n按换行分隔，每行当作一条路径'
    messagebox.showinfo('帮助', tipsStr, parent=frame)

def onPathComboboxSelect(frame, tmExUi, data):
    if not 'pathCombobox' in tmExUi:
        return
    # key = tmExUi['pathCombobox'].get()
    # data['_pathComboboxKey'] = key

def onTextPathDrop(tmExUi, files=''):
    if not 'textPath' in tmExUi:
        return
    tlFile = py3_common.parseDndFiles(files)
    text = py3_common.getTextText(tmExUi['textPath'])
    hasEnter = text.endswith('\n')
    if re.search(r'^\s*$', text):
        text = ''
        hasEnter = True
    for i in range(0,len(tlFile)):
        filePath = os.path.normpath(tlFile[i])
        if REL_PATH_VAR.get() > 0:
            try:
                filePath = os.path.normpath(os.path.relpath(tlFile[i], '.'))
            except Exception as e:
                pass
        text += ('' if i == 0 and hasEnter else '\n') + filePath
    py3_common.setTextText(tmExUi['textPath'], text)

def refreshPathCombobox(tmExUi):
    if not 'pathCombobox' in tmExUi:
        return
    tlPath = getTlPathWithTextPath(tmExUi)
    tlValue = list()
    for i in range(0,len(tlPath)):
        tlValue.append(i)
    tmExUi['pathCombobox']['values'] = tlValue

def getTlStrWithTkText(tkText):
    if not tkText:
        return
    textStr = py3_common.getTextText(tkText)
    tlStr = re.split(r'\n', textStr)
    return tlStr

def getTlPathWithTextPath(tmExUi):
    if not 'textPath' in tmExUi:
        return
    return getTlStrWithTkText(tmExUi['textPath'])

def getTlCommandWithTextCommand(tmExUi):
    if not 'textCommand' in tmExUi:
        return
    return getTlStrWithTkText(tmExUi['textCommand'])


# 保存数据
def saveData(tmExUi, data):
    if DEBUG:
        py3_common.Logging.debug('-----%s saveData-----' % SCRIPT_NAME)
    # 路径
    data['tlFilePath'] = getTlPathWithTextPath(tmExUi)
    # 命令
    tlCommand = getTlCommandWithTextCommand(tmExUi)
    data['command'] = tlCommand if not tlCommand or len(tlCommand) > 1 else tlCommand[0]

    # data['openNewCmdWindow'] = OPEN_NEW_CMD_WINDOW_VAR.get() > 0
    py3_common.setKVInDataWithExcludeDefault(data, 'openNewCmdWindow', OPEN_NEW_CMD_WINDOW_VAR.get() > 0, True)
    # data['notClose'] = OPEN_NEW_CMD_WINDOW_VAR.get() > 0 and NOT_CLOSE_VAR.get() > 0
    py3_common.setKVInDataWithExcludeDefault(data, 'notClose', OPEN_NEW_CMD_WINDOW_VAR.get() > 0 and NOT_CLOSE_VAR.get() > 0, False)
    # data['autoCd'] = AUTO_CD_VAR.get() > 0
    py3_common.setKVInDataWithExcludeDefault(data, 'autoCd', AUTO_CD_VAR.get() > 0, False)
    return True

# 额外的保留字段
def getTlAdvSaveKey():
    # return ['command', 'tlFilePath', 'notClose', 'openNewCmdWindow', 'autoCd']
    return GlobalValue.TMTL_TYPE_ADV_KEY['cmd']

# 按钮操作
def onBtnClick(data=None):
    if DEBUG:
        py3_common.Logging.debug('-----%s onBtnClick-----' % SCRIPT_NAME)
    # if data == None:
    #     return
    tlCmd = parseCommand(data)
    if not tlCmd:
        return
    for i in range(0,len(tlCmd)):
        cmd = tlCmd[i]
        try:
            cmd_ = None
            if not 'openNewCmdWindow' in data or data['openNewCmdWindow']:
                cmd_ = 'start cmd /%s "%s"' % ('k' if 'notClose' in data and data['notClose'] else 'c', cmd)
            else:
                cmd_ = '%s' % (cmd)
            if DEBUG:
                py3_common.Logging.info(cmd_)
            # subprocess.Popen(cmd_, shell=True)
            env = os.environ.copy()
            if 'TCL_LIBRARY' in env:
                del env['TCL_LIBRARY']
            if 'TK_LIBRARY' in env:
                del env['TK_LIBRARY']
            subprocess.Popen(cmd_, shell=True, env=env)
            # os.system(cmd_)
            # CREATE_NO_WINDOW = 0x08000000
            # subprocess.call(cmd_, creationflags=CREATE_NO_WINDOW, shell=True)
        except Exception as e:
            py3_common.Logging.error(e)

# 拖入操作
def onDrop(data=None, tlFile=None):
    if DEBUG:
        py3_common.Logging.debug('-----%s onDrop-----' % SCRIPT_NAME)
    # if data == None or tlFile == None or len(tlFile) <= 0:
    #     return
    tlCmd = parseCommand(data, tlFile)
    if not tlCmd:
        return
    for i in range(0,len(tlCmd)):
        cmd = tlCmd[i]
        try:
            cmd_ = None
            if not 'openNewCmdWindow' in data or data['openNewCmdWindow']:
                cmd_ = 'start cmd /%s "%s"' % ('k' if 'notClose' in data and data['notClose'] else 'c', cmd)
            else:
                cmd_ = '%s' % (cmd)
            if DEBUG:
                py3_common.Logging.info(cmd_)
            # subprocess.Popen(cmd_, shell=True)
            env = os.environ.copy()
            if 'TCL_LIBRARY' in env:
                del env['TCL_LIBRARY']
            if 'TK_LIBRARY' in env:
                del env['TK_LIBRARY']
            subprocess.Popen(cmd_, shell=True, env=env)
            # os.system(cmd_)
        except Exception as e:
            py3_common.Logging.error(e)

def getPath(data=None, tmExUi=None):
    if DEBUG:
        py3_common.Logging.debug('-----%s getPath-----' % SCRIPT_NAME)
    if tmExUi:
        tlFilePath = getTlPathWithTextPath(tmExUi)
        if 'pathCombobox' in tmExUi:
            key = tmExUi['pathCombobox'].get()
            if re.search(r'\d+', key) and int(key) >= 0 and int(key) < len(tlFilePath):
                return tlFilePath[int(key)]
    else:
        tlFilePath = getTlPath(data)
        return tlFilePath[0] if tlFilePath != None and len(tlFilePath) > 0 else None
    return None

def getTlPath(data=None):
    if DEBUG:
        py3_common.Logging.debug('-----%s getTlPath-----' % SCRIPT_NAME)
    return data['tlFilePath'] if data != None and 'tlFilePath' in data else None

def getCommand(data=None):
    if DEBUG:
        py3_common.Logging.debug('-----%s getCommand-----' % SCRIPT_NAME)
    commandData = data['command'] if data != None and 'command' in data else None
    return commandData if not commandData or isinstance(commandData, list) else [commandData]

# 解析
def parseCommand(data=None, tlFile=None):
    if DEBUG:
        py3_common.Logging.debug('-----%s parseCommand-----' % SCRIPT_NAME)
    tlCmd = getCommand(data)
    tlCmd_ = list()
    tlFilePath = getTlPath(data)
    for i in range(0,len(tlCmd)):
        cmd = parseSingleCommand(tlCmd[i], tlFilePath, tlFile=tlFile, autoCd='autoCd' in data and data['autoCd'])
        if cmd:
            tlCmd_.append(cmd)
    return tlCmd_

def parseSingleCommand(cmd, tlFilePath, tlFile=None, autoCd=False):
    try:
        # 解析路径
        pattern = re.compile(r'\%p(\d+)(\s*)')
        match = pattern.search(cmd)
        # tlFilePath = getTlPath(data)
        while match:
            start_ = match.start()
            end_ = match.end()
            pathIndex = int(match.group(1))
            if not tlFilePath or len(tlFilePath) < pathIndex+1:
                py3_common.Logging.debug('not index %d in tlFilePath' % pathIndex)
                messagebox.showinfo('提示', 'not index %d in tlFilePath' % pathIndex)
                return
            # cmd = 'cd "%s" & ' % (os.path.dirname(os.path.abspath(path_))) + cmd[:match.start()] + '"%s"' % (os.path.basename(path_)) + cmd[match.end():]
            filePath = os.path.abspath(tlFilePath[pathIndex])
            if not os.path.exists(filePath):
                py3_common.Logging.error('路径不存在：%s' % filePath)
                messagebox.showerror('错误', '路径不存在：%s' % filePath)
                return
            if autoCd:
                index1 = cmd[:match.start()].rfind('& ')
                index2 = cmd[:match.start()].rfind('| ')
                indexStart = max(index1, index2)
                cmd0 = cmd[:indexStart+2] if indexStart > 0 else ''
                cmd1 = cmd[indexStart+2:match.start()] if indexStart > 0 else cmd[:match.start()]

                nStr = 'cd "%s" && %s && %s"%s"' % (os.path.dirname(filePath), '%dp' + str(pathIndex), cmd1, os.path.basename(filePath)) + match.group(2)
                cmd = cmd0 + nStr + cmd[match.end():]
                match = pattern.search(cmd, len(cmd0 + nStr))
                # print(cmd)
            else:
                nStr = '"%s"' % (filePath) + match.group(2)
                cmd = cmd[:match.start()] + nStr + cmd[match.end():]
                match = pattern.search(cmd, start_ + len(nStr))

        # 解析盘符
        pattern = re.compile(r'\%dp(\d+)(\s*)')
        match = pattern.search(cmd)
        # tlFilePath = getTlPath(data)
        while match:
            start_ = match.start()
            end_ = match.end()
            pathIndex = int(match.group(1))
            if not tlFilePath or len(tlFilePath) < pathIndex+1:
                py3_common.Logging.debug('not index %d in tlFilePath' % pathIndex)
                messagebox.showinfo('提示', 'not index %d in tlFilePath' % pathIndex)
                return
            # cmd = 'cd "%s" & ' % (os.path.dirname(os.path.abspath(path_))) + cmd[:match.start()] + '"%s"' % (os.path.basename(path_)) + cmd[match.end():]
            filePath = os.path.abspath(tlFilePath[pathIndex])
            if not os.path.exists(filePath):
                py3_common.Logging.error('路径不存在：%s' % filePath)
                messagebox.showerror('错误', '路径不存在：%s' % filePath)
                return
            nStr = '%s' % (os.path.splitdrive(filePath)[0]) + match.group(2)
            cmd = cmd[:match.start()] + nStr + cmd[match.end():]
            match = pattern.search(cmd, start_ + len(nStr))

        # 解析拖入
        pattern = re.compile(r'\%(\d+)')
        match = pattern.search(cmd)
        while match:
            start_ = match.start()
            end_ = match.end()
            if not tlFile or len(tlFile) <= int(match.group(1)):
                py3_common.Logging.debug('not index %d in tlFile' % int(match.group(1)))
                messagebox.showinfo('提示', 'not index %d in tlFile' % int(match.group(1)))
                return
            filePath = tlFile[int(match.group(1))]
            if not os.path.exists(filePath):
                py3_common.Logging.error('路径不存在：%s' % filePath)
                messagebox.showerror('错误', '路径不存在：%s' % filePath)
                return
            nStr = '"%s"' % (filePath)
            cmd = cmd[:start_] + nStr + cmd[end_:]
            match = pattern.search(cmd, start_ + len(nStr))

        # 解析拖入盘符
        pattern = re.compile(r'\%d(\d+)')
        match = pattern.search(cmd)
        while match:
            start_ = match.start()
            end_ = match.end()
            if not tlFile or len(tlFile) <= int(match.group(1)):
                py3_common.Logging.debug('not index %d in tlFile' % int(match.group(1)))
                messagebox.showinfo('提示', 'not index %d in tlFile' % int(match.group(1)))
                return
            filePath = tlFile[int(match.group(1))]
            if not os.path.exists(filePath):
                py3_common.Logging.error('路径不存在：%s' % filePath)
                messagebox.showerror('错误', '路径不存在：%s' % filePath)
                return
            nStr = '%s' % (os.path.splitdrive(filePath)[0])
            cmd = cmd[:start_] + nStr + cmd[end_:]
            match = pattern.search(cmd, start_ + len(nStr))

        if DEBUG:
            py3_common.Logging.debug(cmd)
        return cmd
    except Exception as e:
        py3_common.Logging.error(e)
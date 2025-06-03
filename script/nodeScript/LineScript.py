#! python3
# -*- coding: utf-8 -*-

import os, re
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter.messagebox import showerror
from .. import py3_common
from .. import GlobalValue

SCRIPT_NAME = 'LineScript'
DEBUG = True
def setDebug(debug=False):
    global DEBUG
    DEBUG = debug

# 修改界面
def createEditUi(frame, tmExUi, data, cTkObjFun, dnd=None, tmExFun=None, tmExObj=None):
    if DEBUG:
        py3_common.Logging.debug('-----%s createEditUi-----' % SCRIPT_NAME)

    # 分隔线字符输入框
    frame1 = Frame(frame)
    frame1.grid(row=0,column=0,sticky='ew')
    cTkObjFun(frame1)
    frameLineTag = Frame(frame1)
    frameLineTag.grid(row=0,column=0,sticky='w')
    cTkObjFun(frameLineTag)
    labelLineTag = Label(frameLineTag, text='分割线字符：', anchor='w')
    labelLineTag.grid(row=0,column=0,sticky='w')
    cTkObjFun(labelLineTag)

    entryLineTag = tmExObj['UndoEntry'](frameLineTag, width=10)
    py3_common.bindTkEditorRightClick(entryLineTag, frame, tkThemeHelper=tmExObj['tkThemeHelper'])
    entryLineTag.grid(row=1,column=0,sticky='w')
    tmExUi['entryLineTag'] = entryLineTag
    py3_common.setEntryText(entryLineTag, data['lineTag'] if 'lineTag' in data else '-')
    try:
        entryLineTag.clearLog()
    except Exception as e:
        pass
    cTkObjFun(entryLineTag, isForceRaw=True)

    # 字号输入框
    frameFontSize = Frame(frame1)
    frameFontSize.grid(row=0,column=1,sticky='w')
    cTkObjFun(frameFontSize)
    labelFontSize = Label(frameFontSize, text='字号：(默认%s)' % str(GlobalValue.DEFAULT_TK_FONT_SIZE), anchor='w')
    labelFontSize.grid(row=0,column=0,sticky='w')
    cTkObjFun(labelFontSize)

    entryFontSize = tmExObj['UndoEntry'](frameFontSize, width=10)
    py3_common.bindTkEditorRightClick(entryFontSize, frame, tkThemeHelper=tmExObj['tkThemeHelper'])
    entryFontSize.grid(row=1,column=0,sticky='w')
    tmExUi['entryFontSize'] = entryFontSize
    py3_common.setEntryText(entryFontSize, data['fontSize'] if 'fontSize' in data else '')
    try:
        entryFontSize.clearLog()
    except Exception as e:
        pass
    cTkObjFun(entryFontSize, isForceRaw=True)


    labelColorTitle = Label(frame, text='颜色：(右键点击还原默认颜色)', anchor='w')
    labelColorTitle.grid(row=1, column=0, sticky='w', pady=2)
    cTkObjFun(labelColorTitle)
    frameColor = Frame(frame)
    frameColor.grid(row=2, column=0, sticky='ew')
    cTkObjFun(frameColor)

    lbPadding = 2
    tempRow = 0
    tempCol = 0
    lbBgColor = tmExFun['createColorLabelBtn'](frameColor, '背景', 'bgColor', ['line', 'bgColor'])
    lbBgColor.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
    tempCol += 1
    lbFgColor = tmExFun['createColorLabelBtn'](frameColor, '文本', 'fgColor', ['line', 'fgColor'])
    lbFgColor.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')

    # for i in range(0,10):
    #     label = Label(frame, text=str(i), anchor='w')
    #     label.grid(row=2+i,column=0,sticky='w')
    #     tmExUi['label' + str(i)] = label

# 保存数据
def saveData(tmExUi, data):
    if DEBUG:
        py3_common.Logging.debug('-----%s saveData-----' % SCRIPT_NAME)
    text = py3_common.getEntryText(tmExUi['entryLineTag'])
    if not re.search(r'^\s*$', text):
        data['lineTag'] = text
    fontSize = py3_common.getEntryText(tmExUi['entryFontSize'])
    # if not fontSize or abs(int(fontSize)) == GlobalValue.DEFAULT_TK_FONT_SIZE:
    #     if 'fontSize' in data:
    #         del data['fontSize']
    # else:
    #     data['fontSize'] = fontSize
    fontSize = fontSize if fontSize else GlobalValue.DEFAULT_TK_FONT_SIZE
    py3_common.setKVInDataWithExcludeDefault(data, 'fontSize', abs(int(fontSize)), GlobalValue.DEFAULT_TK_FONT_SIZE)
    return True

# 额外的保留字段
def getTlAdvSaveKey():
    # return ['fgColor', 'fontSize']
    return GlobalValue.TMTL_TYPE_ADV_KEY['line']

# 按钮操作
def onBtnClick(data=None):
    if DEBUG:
        py3_common.Logging.debug('-----%s onBtnClick-----' % SCRIPT_NAME)
        py3_common.Logging.debug(data)

# 拖入操作
def onDrop(data=None, tlFile=None):
    if DEBUG:
        py3_common.Logging.debug('-----%s onDrop-----' % SCRIPT_NAME)
        py3_common.Logging.debug(tlFile)

def getPath(data=None, tmExUi=None):
    if DEBUG:
        py3_common.Logging.debug('-----%s getPath-----' % SCRIPT_NAME)
    return None

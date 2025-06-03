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
import time

from .. import py3_common, GlobalValue
from ..GlobalValue import *
from ..UndoRedoHelper import *


# 带撤销重做的输入框
class UndoEntry(Entry):
    """docstring for UndoEntry"""
    def __init__(self, *args, **kwargs):
        super(UndoEntry, self).__init__(*args, **kwargs)

        self.tlEventHandle = list()
        self.undoRedoHelper = UndoRedoHelper()

        self.bind('<Control-z>', self.onKeyboardCtrlZClick)
        self.bind('<Control-y>', self.onKeyboardCtrlYClick)
        self.bind('<KeyRelease>', self.onKeyRelease)
        self.bind('<<Cut>>', self.onTkEventCut)
        self.bind('<<Paste>>', self.onTkEventPaste)

        # 记录状态
        # value:string 文本框内容
        # cursor:[int, int, int?, int?] 光标位置
        # time:float 记录时间戳
        self.nowData = self.getNowStateData()

    def __del__(self):
        py3_common.Logging.info2(self.getClassName(),'__del__')

    def getClassName(self):
        return self.__class__.__name__

    # 清除记录，通常在初始化设值后调用
    def clearLog(self):
        self.undoRedoHelper.clear()
        self.nowData = self.getNowStateData()




    # -----------------------------tk事件-----------------------------
    # ctrl+z 撤销
    def onKeyboardCtrlZClick(self, event):
        py3_common.Logging.debug(self.getClassName(),'onKeyboardCtrlZClick')
        suc = self.undoRedoHelper.undo(self.nowData)
        if suc:
            # self.updateView()
            self.updateStateToView(self.nowData)

    # ctrl+y 重做
    def onKeyboardCtrlYClick(self, event):
        py3_common.Logging.debug(self.getClassName(),'onKeyboardCtrlYClick')
        suc = self.undoRedoHelper.redo(self.nowData)
        if suc:
            try:
                # self.updateView()
                self.updateStateToView(self.nowData)
            except Exception as e:
                self.onKeyboardCtrlZClick(event)
                raise e

    # 监听所有按键释放
    def onKeyRelease(self, event):
        py3_common.Logging.debug(self.getClassName(),'onKeyRelease')
        py3_common.Logging.debug3(event)

        newData = self.getNowStateData()
        py3_common.Logging.debug3(newData)

        oldData = self.nowData

        # 文本没变，不记录
        if newData['value'] == oldData['value']:
            return
        # 文字变了，离上次记录时间少于0.2，不改变时间覆盖栈顶
        if abs(newData['time'] - oldData['time']) <= 0.2:
            newData['time'] = oldData['time']
            self.undoRedoHelper.setValueWithTlKeyCoverRecord(oldData, [], newData, coverStep=-1)
            return
        # 其他情况正常记录
        self.undoRedoHelper.setValueWithTlKey(oldData, [], newData)

    def onTkEventCut(self, event):
        py3_common.Logging.debug(self.getClassName(),'onTkEventCut')
        self.after(1, lambda e=event: self.onKeyRelease(e))

    def onTkEventPaste(self, event):
        py3_common.Logging.debug(self.getClassName(),'onTkEventPaste')
        self.after(1, lambda e=event: self.onKeyRelease(e))

    # 外部代码设置值要手动记录下
    def onFunctionEditText(self):
        py3_common.Logging.debug(self.getClassName(),'onFunctionEditText')
        self.after(1, lambda e=None: self.onKeyRelease(e))




    # -----------------------------数据-----------------------------
    # 获取当前状态
    def getNowStateData(self):
        value = py3_common.getEditorText(self)
        l,c,l2,c2 = py3_common.getEditorCursorPos(self)
        nowTime = time.time()
        tempData = {
            'value':value,
            'cursor':[l,c,l2,c2],
            'time':nowTime
        }
        return tempData

    # 将数据刷到界面上
    def updateStateToView(self, data):
        py3_common.setEditorText(self, data['value'])
        l,c,l2,c2 = (data['cursor'])
        if l2 != None and c2 != None:
            py3_common.setEditorCursorPos(self, l2, c2)
        else:
            py3_common.setEditorCursorPos(self, l, c)



    # -----------------------------事件相关-----------------------------
    # 添加事件监听
    def addEventListener(self, eventType, fCallback):
        self.tlEventHandle.append(addEventListener(eventType, fCallback))

    # 移除所有事件监听
    def removeAllEventListen(self):
        removeTlEventListener(self.tlEventHandle)
        self.tlEventHandle = list()

    def initEventListen(self):
        self.removeAllEventListen()
        self.addEventListener(EventType.Event_UndoRedoHelperDataChange, self.onEvent_UndoRedoHelperDataChange)

    def onEvent_UndoRedoHelperDataChange(self, uid):
        if uid == self.undoRedoHelper.getUid():
            py3_common.Logging.debug(self.getClassName(),'onEvent_UndoRedoHelperDataChange')
            # self.setTitleWithModify(self.undoRedoHelper.hasModify() or self.isInitModify)
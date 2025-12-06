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

from .. import py3_common, GlobalValue
from ..GlobalValue import *
from ..EventProxy import *
from .BaseView import *
from ..extend.UndoEntry import UndoEntry

M_PageShowNum = 7     #一页显示多少个，要算出来太复杂，直接写死

# 列表选择复制文本界面
class ViewLineCopyString(BaseView):
    """
    列表选择复制文本界面
    参数:
    initWindow:tkObj 父容器
    tlString:list 传入字符串列表
    editor:tk.Entry|tk.Text 焦点所在输入框组件
    fCallback:function(copyStr:string, index:int) 回调函数
    isCopyStr:bool 是否复制到剪贴板，默认True
    title:string 弹窗标题
    """
    def __init__(self, initWindow, tlString, editor=None, fCallback=None, isCopyStr=True, title=None):
        if self.checkUniqueNeedClose():
            return
        super(ViewLineCopyString, self).__init__(initWindow)
        self.initWindow = initWindow
        self.tlString = tlString
        self.editor = editor
        self.fCallback = fCallback
        self.isCopyStr = isCopyStr
        # self.tlScreenNodeData = None
        self.tlConvertScreenIndex = None
        self.searchStr = ''
        self.nowSelectIndex = -1
        self.title('选择复制文本' if title == None else title)
        self.initUi()
        # if tlNodeData != None:
        #     self.updateTlNodeData(tlNodeData)

    # 是否需要锁定焦点，子类重载
    def isNeedGrab(self):
        return True

    # 是否唯一，子类重载
    def isUnique(self):
        return True

    # 弹窗位置，返回None时不设置，子类重载
    def getAnchorPos(self):
        # return {'x':0.8, 'y':0.5}
        return getViewPosAnchor(self.getClassName())
        
    def initUi(self):
        # self.resizable(width=False, height=False)
        # self.title('选择复制文本')
        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)

        self.bind('<Escape>', lambda e:self.onBtnClose())
        self.bind('<Return>', lambda e:self.onKeyboardReturnClick())
        self.bind('<Up>', lambda e,v=-1:self.selectListboxWithShift(v))
        self.bind('<Down>', lambda e,v=1:self.selectListboxWithShift(v))
        self.bind('<Home>', lambda e,v=True:self.selectListboxTopOrBottom(v))
        self.bind('<End>', lambda e,v=False:self.selectListboxTopOrBottom(v))
        self.bind('<Prior>', lambda e,v=-M_PageShowNum:self.selectListboxWithShift(v, isPageChange=True))
        self.bind('<Next>', lambda e,v=M_PageShowNum:self.selectListboxWithShift(v, isPageChange=True))
        self.bind('<Alt-c>', self.onAltCClick)
        # self.protocol("WM_DELETE_WINDOW", self.onClose)

        frameTop = Frame(self)
        frameTop.grid(row=0,column=0,sticky='nsew')
        self.tkThemeHelper.addTkObj(frameTop)
        self.frameTop = frameTop
        frameTop.rowconfigure(1,weight=1)
        frameTop.columnconfigure(0,weight=1)

        labelTitle = Label(frameTop, text='鼠标双击/Enter 复制：', anchor='w')
        labelTitle.grid(row=0,column=0,sticky='ew')
        self.tkThemeHelper.addTkObj(labelTitle)

        # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/listbox.html
        # selectmode=EXTENDED 多选模式
        # exportselection=False 允许同时在多个listbox里选中
        # activestyle='none' 去掉选中时下划线
        self.listboxLine = Listbox(frameTop, height=7, width=60, selectmode=SINGLE, exportselection=False, activestyle='none')
        # self.dnd.bindtarget(self.listboxLine, 'text/uri-list', '<Drop>', self.on_listbox_top_drop, ('%D',))
        self.listboxLine.bind('<<ListboxSelect>>', self.onListboxLineSelect)
        self.listboxLine.bind('<Double-1>', lambda e:self.onKeyboardReturnClick())
        self.listboxLine.grid(row=1,column=0,sticky='nsew')
        self.tkThemeHelper.addTkObj(self.listboxLine)

        listboxLineVsb = ttk.Scrollbar(frameTop,orient="vertical",command=self.listboxLine.yview)
        self.listboxLine.configure(yscrollcommand=listboxLineVsb.set)
        listboxLineVsb.grid(column=1, row=1, sticky='ns')

        listboxLineHsb = ttk.Scrollbar(frameTop,orient="horizontal",command=self.listboxLine.xview)
        self.listboxLine.configure(xscrollcommand=listboxLineHsb.set)
        listboxLineHsb.grid(column=0, row=2, sticky='ew')

        frameMiddle = Frame(self)
        frameMiddle.grid(row=1, column=0, sticky='nsew')
        self.tkThemeHelper.addTkObj(frameMiddle)
        frameMiddle.columnconfigure(0,weight=1)

        # 搜索输入
        callback = self.register(self.searchEntryCallback)    #输入回调
        searchEntry = UndoEntry(frameMiddle, validate='key', validatecommand=(callback, '%P'))
        searchEntry.grid(row=0, column=0, sticky='ew', pady=10)
        self.tkThemeHelper.addTkObj(searchEntry, isForceRaw=True)
        py3_common.bindTkEditorRightClick(searchEntry, self, tkThemeHelper=self.tkThemeHelper)
        self.searchEntry = searchEntry
        searchEntry.focus_set()
        # 好像有的电脑focus不到，延迟再来一次
        self.after(100, lambda: self.searchEntry.focus_set())

        # 选项
        # 区分大小写
        self.checkbuttonNoIgnorecaseVar = IntVar()
        self.checkbuttonNoIgnorecaseVar.set(1 if GlobalValue.VIEW_LINE_COPY_NO_IGNORECASE else 0)
        checkbuttonNoIgnorecase = Checkbutton(frameMiddle, text=str('区分大小写'), variable=self.checkbuttonNoIgnorecaseVar, command=lambda :self.onNoIgnorecaseVarChange(), takefocus=0)
        checkbuttonNoIgnorecase.grid(row=1, column=0, sticky='w')
        self.tkThemeHelper.addTkObj(checkbuttonNoIgnorecase)
        self.checkbuttonNoIgnorecase = checkbuttonNoIgnorecase

        # 留间距
        frameTemp = Frame(self)
        frameTemp.grid(row=2,column=0,sticky='nsew')
        self.tkThemeHelper.addTkObj(frameTemp)
        labelTemp = Label(frameTemp, text=' ')
        labelTemp.grid(row=0,column=0,sticky='nsew')
        self.tkThemeHelper.addTkObj(labelTemp)

        # 下
        frameBottom = Frame(self)
        frameBottom.grid(row=3,column=0,sticky='nsew')
        self.tkThemeHelper.addTkObj(frameBottom)
        self.frameBottom = frameBottom
        frameBottom.columnconfigure(0,weight=1)
        if True:
            buttonCancel = Button(frameBottom, text='关闭', width=10, command=self.onBtnClose, takefocus=0)
            buttonCancel.grid(row=0, column=0)
            self.tkThemeHelper.addTkObj(buttonCancel)

        self.tkThemeHelper.update()
        self.refreshListBoxLine()

    def refreshListBoxLine(self):
        listbox = self.listboxLine

        #清空
        listbox.delete(0, END)
        self.tlConvertScreenIndex = list()

        isEmpty = re.search(r'^\s*$', self.searchStr)
        pattern = None
        try:
            if GlobalValue.VIEW_LINE_COPY_NO_IGNORECASE:
                pattern = re.compile(r'%s' % self.searchStr)
            else:
                pattern = re.compile(r'%s' % self.searchStr, flags=re.I)
        except Exception as e:
            fixStr = fixReInputStr(self.searchStr)
            # py3_common.Logging.info(fixStr)
            if GlobalValue.VIEW_LINE_COPY_NO_IGNORECASE:
                pattern = re.compile(r'%s' % fixStr)
            else:
                pattern = re.compile(r'%s' % fixStr, flags=re.I)

        if self.tlString != None:
            for i in range(0,len(self.tlString)):
                text = self.tlString[i]
                canAdd = True
                # if not re.search(r'^\s*$', self.searchStr) and not re.search(r'%s' % self.searchStr.lower(), text.lower()):
                if not isEmpty and not pattern.search(text):
                    canAdd = False
                if canAdd:
                    self.tlConvertScreenIndex.append(i)       #记录
                    # listbox.insert("end", '%s%s%s' % (strLineTag, text, strLineTag))
                    listbox.insert("end", '%s' % (text))

    def onListboxLineSelect(self, event):
        # if self.tlScreenNodeData == None or self.tlConvertScreenIndex == None:
        if len(self.tlString) == 0 or self.tlConvertScreenIndex == None:
            return
        listbox = self.listboxLine
        tlIndex = list()
        for item in listbox.curselection():
            tlIndex.append(item)
        if len(tlIndex) > 0 and len(self.tlConvertScreenIndex) > tlIndex[0]:
            cIndex = self.tlConvertScreenIndex[tlIndex[0]]
            self.nowSelectIndex = cIndex

    # 关闭
    def onBtnClose(self):
        py3_common.Logging.debug(self.getClassName(),'onBtnClose')
        self.close()

    # 键盘Enter
    def onKeyboardReturnClick(self):
        py3_common.Logging.debug(self.getClassName(),'onKeyboardReturnClick')
        if self.nowSelectIndex < 0:
            self.close()
            return

        copyStr = None
        try:
            copyStr = self.tlString[self.nowSelectIndex]
            # self.clipboard_clear()
            # self.clipboard_append(copyStr)
            if self.isCopyStr:
                GlobalValue.copyStr2Clipboard(copyStr)
                py3_common.Logging.info2('复制文本：%s\tindex：%s' % (copyStr, self.nowSelectIndex))
            else:
                py3_common.Logging.info2('文本：%s\tindex：%s' % (copyStr, self.nowSelectIndex))
        except Exception as e:
            # raise e
            py3_common.Logging.warning('复制文本失败')
            py3_common.Logging.warning(e)
            messagebox.showwarning('警告','复制文本失败',parent=self)
            return

        if self.editor != None and copyStr != None:
            try:
                tlEditorClassName = ['Entry', 'Text']
                className = self.editor.winfo_class()
                if className in tlEditorClassName:
                    l,c,l2,c2 = py3_common.getEditorCursorPos(self.editor)
                    oldStr = py3_common.getEditorText(self.editor)
                    if l == None or c == None:
                        py3_common.setEditorText(self.editor, oldStr + copyStr)
                    else:
                        tlLineStr = oldStr.split('\n')
                        if l > len(tlLineStr):
                            l = len(tlLineStr)
                        if l2 == None or c2 == None:
                            lineStr = tlLineStr[l-1]
                            tlLineStr[l-1] = lineStr[:c] + copyStr + lineStr[c:]
                        else:
                            if len(tlLineStr) < l2:
                                # 处理全选
                                l2 = len(tlLineStr)
                                c2 = len(tlLineStr[l2-1])
                            lineStr1, lineStr2 = tlLineStr[l-1], tlLineStr[l2-1]
                            tlLineStr[l-1] = lineStr1[:c] + copyStr + lineStr2[c2:]
                            if l2 > l:
                                # 删除多余行
                                for i in range(l2,l,-1):
                                    del tlLineStr[i-1]
                        newStr = '\n'.join(tlLineStr)
                        py3_common.setEditorText(self.editor, newStr)
                        if className != 'Text' or not re.search(r'\n', copyStr):
                            py3_common.setEditorCursorPos(self.editor, l, c + len(copyStr))
                        else:
                            tlTempStr = copyStr.split('\n')
                            py3_common.setEditorCursorPos(self.editor, l + len(tlTempStr) - 1, len(tlTempStr[-1]))
                    self.editor.focus_set()
            except Exception as e:
                # raise e
                py3_common.Logging.warning('复制文本到输入框失败')
                py3_common.Logging.warning(e)

        if copyStr != None and self.fCallback != None:
            try:
                self.fCallback(copyStr, self.nowSelectIndex)
            except Exception as e:
                # raise e
                py3_common.Logging.warning('回调复制文本失败')
                py3_common.Logging.warning(e)

        self.close()

    def searchEntryCallback(self, text):
        self.searchStr = text
        self.refreshListBoxLine()
        return True

    def selectListboxWithShift(self, shift, isPageChange=False):
        if len(self.tlString) == 0 or self.tlConvertScreenIndex == None:
            return
        listbox = self.listboxLine
        tlIndex = list()
        for item in listbox.curselection():
            tlIndex.append(item)
        listbox.selection_clear(0, END)
        index = None
        if len(tlIndex) > 0:
            if isPageChange:
                index = min(max(tlIndex[0]+shift, 0), len(self.tlConvertScreenIndex)-1)
            else:
                index = (tlIndex[0]+shift) % len(self.tlConvertScreenIndex)
            # py3_common.Logging.debug('a', index)
            listbox.selection_set(index, index)
        else:
            index = -1 if shift > 0 else len(self.tlConvertScreenIndex)
            index = index + shift
            # py3_common.Logging.debug('b', index)
            listbox.selection_set(index, index)
        if index != None:
            totalNum = len(self.tlConvertScreenIndex)
            if isPageChange and totalNum > M_PageShowNum:
                listbox.yview_moveto(index / totalNum)
            else:
                listbox.see(index)
        self.onListboxLineSelect(None)

    def selectListboxTopOrBottom(self, isTop=True):
        totalNum = len(self.tlConvertScreenIndex)
        return self.selectListboxWithShift((-totalNum) if isTop else totalNum, isPageChange=True)

    def onNoIgnorecaseVarChange(self):
        GlobalValue.VIEW_LINE_COPY_NO_IGNORECASE = self.checkbuttonNoIgnorecaseVar.get() > 0
        self.refreshListBoxLine()

    def onAltCClick(self, event):
        v = self.checkbuttonNoIgnorecaseVar
        v.set(0 if v.get() > 0 else 1)
        self.onNoIgnorecaseVarChange()

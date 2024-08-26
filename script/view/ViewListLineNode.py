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

M_PageShowNum = 7     #一页显示多少个，要算出来太复杂，直接写死

# 搜索界面（列表展示样式）
class ViewListLineNode(BaseView):
    """
    搜索界面（列表展示样式）
    参数:
    initWindow:tkObj 父界面
    mode:ListLineNodeModeEnum 搜索模式
    tlNodeData:list 所有节点列表
    """
    def __init__(self, initWindow, mode=ListLineNodeModeEnum.P, tlNodeData=None):
        if self.checkUniqueNeedClose():
            return
        super(ViewListLineNode, self).__init__()
        self.initWindow = initWindow
        self.mode = mode
        self.tlScreenNodeData = None
        self.tlConvertScreenNodeData = None
        self.searchStr = ''
        self.nowSelectIndex = -1
        self.initUi()
        if tlNodeData != None:
            self.updateTlNodeData(tlNodeData)

    # 是否需要锁定焦点，子类重载
    def isNeedGrab(self):
        return False

    # 是否唯一，子类重载
    def isUnique(self):
        return True

    # 弹窗位置，返回None时不设置，子类重载
    def getAnchorPos(self):
        return {'x':0.8, 'y':0.5}
        
    def initUi(self):
        # self.resizable(width=False, height=False)
        tmTitle = {ListLineNodeModeEnum.P:'搜索分割线', ListLineNodeModeEnum.R:'搜索标记'}
        self.title(tmTitle[self.mode] if self.mode in tmTitle else '搜索')
        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)

        self.bind('<Escape>', lambda e:self.onBtnClose())
        self.bind('<Return>', lambda e:self.onBtnClose())
        self.bind('<Up>', lambda e,v=-1:self.selectListboxWithShift(v))
        self.bind('<Down>', lambda e,v=1:self.selectListboxWithShift(v))
        self.bind('<Home>', lambda e,v=True:self.selectListboxTopOrBottom(v))
        self.bind('<End>', lambda e,v=False:self.selectListboxTopOrBottom(v))
        self.bind('<Prior>', lambda e,v=-M_PageShowNum:self.selectListboxWithShift(v))
        self.bind('<Next>', lambda e,v=M_PageShowNum:self.selectListboxWithShift(v))
        self.bind('<Alt-c>', self.onAltCClick)
        # self.protocol("WM_DELETE_WINDOW", self.onClose)

        frameTop = Frame(self)
        frameTop.grid(row=0,column=0,sticky='nsew')
        self.tkThemeHelper.addTkObj(frameTop)
        self.frameTop = frameTop
        frameTop.rowconfigure(1,weight=1)
        frameTop.columnconfigure(0,weight=1)

        labelTitle = Label(frameTop, text='点击跳转：', anchor='w')
        labelTitle.grid(row=0,column=0,sticky='ew')
        self.tkThemeHelper.addTkObj(labelTitle)

        # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/listbox.html
        # selectmode=EXTENDED 多选模式
        # exportselection=False 允许同时在多个listbox里选中
        # activestyle='none' 去掉选中时下划线
        self.listboxLine = Listbox(frameTop, height=7, width=60, selectmode=SINGLE, exportselection=False, activestyle='none')
        # self.dnd.bindtarget(self.listboxLine, 'text/uri-list', '<Drop>', self.on_listbox_top_drop, ('%D',))
        self.listboxLine.bind('<<ListboxSelect>>', self.onListboxLineSelect)
        self.listboxLine.bind('<Double-1>', lambda e:self.onBtnClose())
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
        searchEntry = Entry(frameMiddle, validate='key', validatecommand=(callback, '%P'))
        searchEntry.grid(row=0, column=0, sticky='ew', pady=10)
        self.tkThemeHelper.addTkObj(searchEntry)
        py3_common.bindTkEditorRightClick(searchEntry, self, tkThemeHelper=self.tkThemeHelper)
        self.searchEntry = searchEntry
        searchEntry.focus_set()
        # 好像有的电脑focus不到，延迟再来一次
        self.after(100, lambda: self.searchEntry.focus_set())

        # 选项
        # 区分大小写
        self.checkbuttonNoIgnorecaseVar = IntVar()
        self.checkbuttonNoIgnorecaseVar.set(1 if GlobalValue.SEARCH_VIEW_NO_IGNORECASE else 0)
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

    def updateTlNodeData(self, tlNodeData=None):
        if tlNodeData != None:
            self.tlScreenNodeData = list()
            for i in range(0,len(tlNodeData)):
                nodeData = tlNodeData[i]
                if self.mode == ListLineNodeModeEnum.P:
                    if nodeData['nodeType'] == 'Line':
                        self.tlScreenNodeData.append({'index':i, 'nodeData':nodeData})
                elif self.mode == ListLineNodeModeEnum.R:
                    if nodeData['nodeType'] == 'Btn' and 'bookmark' in nodeData and nodeData['bookmark']:
                        self.tlScreenNodeData.append({'index':i, 'nodeData':nodeData})
                elif self.mode == ListLineNodeModeEnum.F:
                    if nodeData['nodeType'] != 'Create':
                        self.tlScreenNodeData.append({'index':i, 'nodeData':nodeData})

        self.refreshListBoxLine()

    def refreshListBoxLine(self):
        listbox = self.listboxLine

        #清空
        listbox.delete(0, END)
        self.tlConvertScreenNodeData = list()

        isEmpty = re.search(r'^\s*$', self.searchStr)
        pattern = None
        try:
            if GlobalValue.SEARCH_VIEW_NO_IGNORECASE:
                pattern = re.compile(r'%s' % self.searchStr)
            else:
                pattern = re.compile(r'%s' % self.searchStr, flags=re.I)
        except Exception as e:
            fixStr = fixReInputStr(self.searchStr)
            # py3_common.Logging.info(fixStr)
            if GlobalValue.SEARCH_VIEW_NO_IGNORECASE:
                pattern = re.compile(r'%s' % fixStr)
            else:
                pattern = re.compile(r'%s' % fixStr, flags=re.I)

        if self.tlScreenNodeData != None:
            for i in range(0,len(self.tlScreenNodeData)):
                nodeData = self.tlScreenNodeData[i]['nodeData']
                text = ''
                strLineTag = ''
                if nodeData['nodeType'] == 'Line':
                    text = nodeData['text'] if 'text' in nodeData else ''
                    strLineTag = nodeData['lineTag'] if 'lineTag' in nodeData else '-'
                elif nodeData['nodeType'] == 'Btn':
                    text = nodeData['btnText'] if 'btnText' in nodeData else ''
                canAdd = True
                # if not re.search(r'^\s*$', self.searchStr) and not re.search(r'%s' % self.searchStr.lower(), text.lower()):
                if not isEmpty and not pattern.search(text):
                    canAdd = False
                if canAdd:
                    self.tlConvertScreenNodeData.append(i)       #记录
                    listbox.insert("end", '%s%s%s' % (strLineTag, text, strLineTag))

    def onListboxLineSelect(self, event):
        if self.tlScreenNodeData == None or self.tlConvertScreenNodeData == None:
            return
        listbox = self.listboxLine
        tlIndex = list()
        for item in listbox.curselection():
            tlIndex.append(item)
        if len(tlIndex) > 0 and len(self.tlConvertScreenNodeData) > tlIndex[0]:
            cIndex = self.tlConvertScreenNodeData[tlIndex[0]]
            if len(self.tlScreenNodeData) > cIndex:
                index = self.tlScreenNodeData[cIndex]['index']
                if GlobalValue.INIT_WINDOW_GUI:
                    GlobalValue.INIT_WINDOW_GUI.jumpToIndex(index)

                # global NOW_SELECT_INDEX
                # global FORCE_SHOW_SELECT
                oldSelectIndex = GlobalValue.NOW_SELECT_INDEX
                GlobalValue.NOW_SELECT_INDEX = index
                GlobalValue.FORCE_SHOW_SELECT = True
                dispatchEvent(EventType.Event_NodeChange, index, False, True)
                if oldSelectIndex != None:
                    dispatchEvent(EventType.Event_NodeChange, oldSelectIndex, False, True)

    def onBtnClose(self):
        py3_common.Logging.debug(self.getClassName(),'onBtnClose')
        self.close()

    # def onClose(self):
    #     # global FORCE_SHOW_SELECT
    #     GlobalValue.FORCE_SHOW_SELECT = False
    #     if GlobalValue.NOW_SELECT_INDEX != None:
    #         self.mainView.refreshNodeByIndex(GlobalValue.NOW_SELECT_INDEX, False, True)

    def searchEntryCallback(self, text):
        self.searchStr = text
        self.refreshListBoxLine()
        return True

    def selectListboxWithShift(self, shift):
        if self.tlScreenNodeData == None or self.tlConvertScreenNodeData == None:
            return
        listbox = self.listboxLine
        tlIndex = list()
        for item in listbox.curselection():
            tlIndex.append(item)
        listbox.selection_clear(0, END)
        index = None
        if len(tlIndex) > 0:
            index = min(max(tlIndex[0]+shift, 0), len(self.tlConvertScreenNodeData)-1)
            # py3_common.Logging.debug('a', index)
            listbox.selection_set(index, index)
        else:
            index = -1 if shift > 0 else len(self.tlConvertScreenNodeData)
            index = index + shift
            # py3_common.Logging.debug('b', index)
            listbox.selection_set(index, index)
        if index != None:
            listbox.see(index)
        self.onListboxLineSelect(None)

    def selectListboxTopOrBottom(self, isTop=True):
        totalNum = len(self.tlConvertScreenNodeData)
        return self.selectListboxWithShift((-totalNum) if isTop else totalNum)

    def onNoIgnorecaseVarChange(self):
        GlobalValue.SEARCH_VIEW_NO_IGNORECASE = self.checkbuttonNoIgnorecaseVar.get() > 0
        self.refreshListBoxLine()

    def onAltCClick(self, event):
        v = self.checkbuttonNoIgnorecaseVar
        v.set(0 if v.get() > 0 else 1)
        self.onNoIgnorecaseVarChange()

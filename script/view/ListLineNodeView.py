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

from .. import tkVirtualListHelper, py3_common, GlobalValue
from ..GlobalValue import *
from ..EventProxy import *

# 搜索界面（列表展示样式）
class ListLineNodeView(Toplevel):
    """docstring for ListLineNodeView"""
    def __init__(self, initWindow, mainView, mode=ListLineNodeViewModeEnum.P, tlNodeData=None):
        super(ListLineNodeView, self).__init__()
        self.initWindow = initWindow
        self.mainView = mainView
        self.mode = mode
        self.tlScreenNodeData = None
        self.tlConvertScreenNodeData = None
        self.searchStr = ''
        self.initUi()
        if tlNodeData != None:
            self.updateTlNodeData(tlNodeData)

    def __del__(self):
        py3_common.Logging.info2('ListLineNodeView __del__')
        
    def initUi(self):
        # self.resizable(width=False, height=False)
        tmTitle = {ListLineNodeViewModeEnum.P:'搜索分割线', ListLineNodeViewModeEnum.R:'搜索标记'}
        self.title(tmTitle[self.mode] if self.mode in tmTitle else '搜索')
        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)
        configureTkObjectColor(self)

        self.bind('<Escape>', lambda e:self.onBtnClose())
        self.bind('<Return>', lambda e:self.onBtnClose())
        self.bind('<Up>', lambda e,v=-1:self.selectListboxWithShift(v))
        self.bind('<Down>', lambda e,v=1:self.selectListboxWithShift(v))
        # self.protocol("WM_DELETE_WINDOW", self.onClose)

        frameTop = Frame(self)
        frameTop.grid(row=0,column=0,sticky='nsew')
        configureTkObjectColor(frameTop)
        self.frameTop = frameTop
        frameTop.rowconfigure(1,weight=1)
        frameTop.columnconfigure(0,weight=1)

        labelTitle = Label(frameTop, text='点击跳转：', anchor='w')
        labelTitle.grid(row=0,column=0,sticky='ew')
        configureTkObjectColor(labelTitle)

        # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/listbox.html
        # selectmode=EXTENDED 多选模式
        # exportselection=False 允许同时在多个listbox里选中
        # activestyle='none' 去掉选中时下划线
        self.listboxLine = Listbox(frameTop, height=7, width=60, selectmode=SINGLE, exportselection=False, activestyle='none')
        # self.dnd.bindtarget(self.listboxLine, 'text/uri-list', '<Drop>', self.on_listbox_top_drop, ('%D',))
        self.listboxLine.bind('<<ListboxSelect>>', self.onListboxLineSelect)
        self.listboxLine.bind('<Double-1>', lambda e:self.onBtnClose())
        self.listboxLine.grid(row=1,column=0,sticky='nsew')
        configureTkObjectColor(self.listboxLine)

        listboxLineVsb = ttk.Scrollbar(frameTop,orient="vertical",command=self.listboxLine.yview)
        self.listboxLine.configure(yscrollcommand=listboxLineVsb.set)
        listboxLineVsb.grid(column=1, row=1, sticky='ns')

        listboxLineHsb = ttk.Scrollbar(frameTop,orient="horizontal",command=self.listboxLine.xview)
        self.listboxLine.configure(xscrollcommand=listboxLineHsb.set)
        listboxLineHsb.grid(column=0, row=2, sticky='ew')

        frameMiddle = Frame(self)
        frameMiddle.grid(row=1, column=0, sticky='nsew')
        frameMiddle.columnconfigure(0,weight=1)
        configureTkObjectColor(frameMiddle)

        # 搜索输入
        callback = self.register(self.searchEntryCallback)    #输入回调
        searchEntry = Entry(frameMiddle, validate='key', validatecommand=(callback, '%P'))
        searchEntry.grid(row=0, column=0, sticky='ew', pady=10)
        self.searchEntry = searchEntry
        searchEntry.focus_set()
        # 好像有的电脑focus不到，延迟再来一次
        self.after(100, lambda: self.searchEntry.focus_set())
        configureTkObjectColor(searchEntry)

        # 留间距
        frameTemp = Frame(self)
        frameTemp.grid(row=2,column=0,sticky='nsew')
        configureTkObjectColor(frameTemp)
        labelTemp = Label(frameTemp, text=' ')
        labelTemp.grid(row=0,column=0,sticky='nsew')
        configureTkObjectColor(labelTemp)

        # 下
        frameBottom = Frame(self)
        frameBottom.grid(row=3,column=0,sticky='nsew')
        configureTkObjectColor(frameBottom)
        self.frameBottom = frameBottom
        frameBottom.columnconfigure(0,weight=1)
        if True:
            buttonCancel = Button(frameBottom, text='关闭', width=10, command=self.onBtnClose)
            buttonCancel.grid(row=0, column=0)
            configureTkObjectColor(buttonCancel)

    def updateTlNodeData(self, tlNodeData=None):
        if tlNodeData != None:
            self.tlScreenNodeData = list()
            for i in range(0,len(tlNodeData)):
                nodeData = tlNodeData[i]
                if self.mode == ListLineNodeViewModeEnum.P:
                    if nodeData['nodeType'] == 'Line':
                        self.tlScreenNodeData.append({'index':i, 'nodeData':nodeData})
                elif self.mode == ListLineNodeViewModeEnum.R:
                    if nodeData['nodeType'] == 'Btn' and 'bookmark' in nodeData and nodeData['bookmark']:
                        self.tlScreenNodeData.append({'index':i, 'nodeData':nodeData})
                elif self.mode == ListLineNodeViewModeEnum.F:
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
            pattern = re.compile(r'%s' % self.searchStr)
        except Exception as e:
            fixStr = fixReInputStr(self.searchStr)
            # py3_common.Logging.info(fixStr)
            pattern = re.compile(r'%s' % fixStr.lower())

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
                if not isEmpty and not pattern.search(text.lower()):
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
                self.mainView.jumpToIndex(index)

                # global NOW_SELECT_INDEX
                # global FORCE_SHOW_SELECT
                oldSelectIndex = GlobalValue.NOW_SELECT_INDEX
                GlobalValue.NOW_SELECT_INDEX = index
                GlobalValue.FORCE_SHOW_SELECT = True
                dispatchEvent(EventType.Event_NodeChange, index, False, True)
                if oldSelectIndex != None:
                    dispatchEvent(EventType.Event_NodeChange, oldSelectIndex, False, True)

    def onBtnClose(self):
        # 关闭
        self.destroy()

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
            index = 0 if shift > 0 else len(self.tlConvertScreenNodeData)-1
            # py3_common.Logging.debug('b', index)
            listbox.selection_set(index, index)
        if index != None:
            listbox.see(index)
        self.onListboxLineSelect(None)
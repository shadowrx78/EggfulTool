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
from ..extend.UndoText import UndoText


class ViewTextTypeEnum:
    Text = 0    #多行文本框
    Entry = 1   #单行文本框



# 文本框界面
class ViewText(BaseView):
    """
    文本框界面
    参数:
    initWindow:tkObj 父界面
    title:string 弹窗标题
    text:string 原文本
    enable:bool 文本框能否编辑
    textComHeight:int 文本框高度，文本框类型为Text时生效，默认8
    viewTextType:ViewTextTypeEnum 文本框类型，默认ViewTextTypeEnum.Text
    tlCustomBtnData:list(dict) 自定义按钮，列表类型，单项为dict，可选
        键值对与tk.Button参数一致，大体上包含：
        text:string 按钮显示文本，必须
        command:function(viewText:ViewText) 按钮回调，必须
        width:number 按钮宽度，可选
        height:number 按钮高度，可选
        ##特殊字段
        bindKey:string 绑定快捷键名
    tlBind:list(dict) 自定义快捷键绑定
        bindKey:string 绑定快捷键名
        fCallback:function(viewText:ViewText) 绑定回调
    """
    def __init__(self, initWindow, title='', text='', enable=False, textComHeight=8, viewTextType=ViewTextTypeEnum.Text, tlCustomBtnData=None, tlBind=None):
        super(ViewText, self).__init__(initWindow)
        self.initWindow = initWindow
        self.textStr = text
        self.enable = enable
        self.textComHeight = textComHeight
        self.tlCustomBtnData = tlCustomBtnData
        self.viewTextType = viewTextType
        self.tlBind = tlBind
        self.title(title)
        self.initUi()

    # 是否需要锁定焦点，子类重载
    def isNeedGrab(self):
        return True

    def initUi(self, isUpdateTheme=True):
        # self.title('文本')
        self.resizable(width=False, height=False)
        self.minsize(500, 10)
        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)

        # self.bind('<FocusIn>', lambda e:self.grab_set())
        # self.protocol("WM_DELETE_WINDOW", self.onBtnClose)
        self.bind('<Escape>', lambda e:self.close())

        # 文本框
        frameText = Frame(self)
        frameText.grid(row=0,column=0,sticky='nsew',columnspan=1,rowspan=1)
        frameText.rowconfigure(0,weight=1)
        frameText.columnconfigure(0,weight=1)
        self.tkThemeHelper.addTkObj(frameText)
        # labelTitle = Label(frameText, text='标题：', anchor='w')
        # labelTitle.grid(row=0,column=0,sticky='ew')
        self.textCom = None
        if self.viewTextType == ViewTextTypeEnum.Entry:
            textCom = UndoEntry(frameText)
            self.textCom = textCom
        else:
            textCom = UndoText(frameText, height=self.textComHeight)
            self.textCom = textCom

            textComVsb = ttk.Scrollbar(frameText,orient="vertical",command=textCom.yview)
            textCom.configure(yscrollcommand=textComVsb.set)
            textComVsb.grid(column=1, row=0, sticky='ns')

        py3_common.setEditorText(self.textCom, self.textStr)
        try:
            self.textCom.clearLog()
        except Exception as e:
            pass
        self.textCom.grid(row=0,column=0,sticky='nsew',padx=4,ipady=10)
        self.tkThemeHelper.addTkObj(self.textCom, isForceRaw=True)
        py3_common.bindTkEditorRightClick(self.textCom, self, tkThemeHelper=self.tkThemeHelper)
        py3_common.setEditorEnable(self.textCom, self.enable)
        if self.enable:
            self.textCom.focus_set()
            # 好像有的电脑focus不到，延迟再来一次
            self.after(100, lambda: self.textCom.focus_set())
        # print(textCom['state'])


        frameTempWH = (120,10)
        frmTemp = Frame(self, height=frameTempWH[1], width=frameTempWH[0])
        frmTemp.grid(row=1, column=0)
        self.tkThemeHelper.addTkObj(frmTemp)

        frameBtn = Frame(self)
        frameBtn.grid(row=2,column=0,sticky='nsew')
        self.tkThemeHelper.addTkObj(frameBtn)
        self.frameBtn=frameBtn

        self.frmBtnRowMax = 5   #一行最大按钮数
        self.tlDefaultBtnWH = [10,1]     #按钮默认宽高
        btnNum = 0
        tlCustomBtnData = self.tlCustomBtnData
        tlBreakBindName = ['<Control-Return>', '<Alt-Return>', '<Shift-Return>', '<Control-Alt-Return>', '<Control-Shift-Return>', '<Alt-Shift-Return>', '<Control-Alt-Shift-Return>']
        # 自定义按钮
        if tlCustomBtnData != None and len(tlCustomBtnData) > 0:
            for i in range(0, min(self.frmBtnRowMax, len(tlCustomBtnData))):
                frameBtn.columnconfigure(i,weight=1)
            # newLineWidth = (self.tlDefaultBtnWH[0] + 2) * self.frmBtnRowMax - 2
            borderwidth = 1
            for i in range(0,len(tlCustomBtnData)):
                customBtnData = py3_common.deep_copy_dict(tlCustomBtnData[i])
                if 'command' in customBtnData and customBtnData['command'] != None:
                    f = customBtnData['command']
                    customBtnData['command'] = lambda fun=f:fun(self)
                if 'bindKey' in customBtnData:
                    bindKey = customBtnData['bindKey']
                    del customBtnData['bindKey']
                    if bindKey == '<Escape>':
                        self.unbind(bindKey)
                    tempFun = customBtnData['command']
                    if bindKey in tlBreakBindName:
                        self.textCom.bind(bindKey, lambda e,fun=tempFun:self.breakTextCom(fun))
                    self.bind(bindKey, lambda e,fun=tempFun:fun())
                try:
                    if not 'width' in customBtnData:
                        customBtnData['width'] = self.tlDefaultBtnWH[0]
                    if not 'height' in customBtnData:
                        customBtnData['height'] = self.tlDefaultBtnWH[1]
                    # if not 'relief' in customBtnData:
                    #     customBtnData['relief'] = GROOVE
                    if not 'takefocus' in customBtnData:
                        customBtnData['takefocus'] = 0
                    btn = Button(frameBtn, **customBtnData)
                    r,c = (math.floor(btnNum / self.frmBtnRowMax), btnNum % self.frmBtnRowMax)
                    columnspan = 1

                    if 'width' in customBtnData and customBtnData['width'] != self.tlDefaultBtnWH[0]:
                        #宽度超过一定值时自动换行
                        w = customBtnData['width']
                        btnWeights = min(math.ceil(w/(self.tlDefaultBtnWH[0] + math.floor(w/self.tlDefaultBtnWH[0])*borderwidth)), self.frmBtnRowMax)
                        if btnNum % self.frmBtnRowMax > 0 and math.floor(btnNum / self.frmBtnRowMax) < math.floor((btnNum + btnWeights) / self.frmBtnRowMax):
                            # 换行
                            btnNum = math.ceil(btnNum / self.frmBtnRowMax) * self.frmBtnRowMax
                        r,c = (math.floor(btnNum / self.frmBtnRowMax), btnNum % self.frmBtnRowMax)
                        columnspan = btnWeights
                        btnNum += btnWeights
                    else:
                        btnNum += 1

                    btn.grid(row=r, column=c, columnspan=columnspan, pady=4)
                    self.tkThemeHelper.addTkObj(btn)
                except Exception as e:
                    # raise e
                    py3_common.Logging.error_(self.getClassName(),'添加自定义按钮失败')
                    py3_common.Logging.error_(customBtnData)
                    py3_common.Logging.error_(e)

        # 自定义快捷键
        if self.tlBind != None and len(self.tlBind) > 0:
            tlBind = self.tlBind
            for i in range(0,len(tlBind)):
                bindKey = tlBind[i]['bindKey']
                fCallback = tlBind[i]['fCallback']
                if bindKey == '<Escape>':
                    self.unbind(bindKey)
                tempFun = lambda fun=fCallback:fun(self)
                if bindKey == 'WM_DELETE_WINDOW':
                    self.protocol("WM_DELETE_WINDOW", lambda fun=tempFun:fun())
                else:
                    if bindKey in tlBreakBindName:
                        self.textCom.bind(bindKey, lambda e,fun=tempFun:self.breakTextCom(fun))
                    self.bind(bindKey, lambda e,fun=tempFun:fun())

        if isUpdateTheme:
            self.tkThemeHelper.update()

    # 获取文本框字符串
    def getTextStr(self):
        textStr = py3_common.getEditorText(self.textCom)
        className = self.textCom.winfo_class()
        if className != 'Text':
            textStr = textStr.replace('\n', '')
        return textStr

    def breakTextCom(self, fun=None):
        if fun != None:
            fun()
        return 'break'
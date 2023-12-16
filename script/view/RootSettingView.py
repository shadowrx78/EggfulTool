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

# 主设置界面
class RootSettingView(Toplevel):
    """docstring for RootSettingView"""
    def __init__(self, initWindow, mainView):
        super(RootSettingView, self).__init__()
        self.initWindow = initWindow
        self.mainView = mainView
        self.tlColorBtn = list()
        self.showColor = False
        self.initUi()

    def __del__(self):
        py3_common.Logging.info2('RootSettingView __del__')

    def initUi(self):
        self.resizable(width=False, height=False)
        self.title("设置")
        # self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)

        fontName = '微软雅黑'
        fontSize = 9
        fontTemp = (fontName, fontSize, 'bold')

        self.tlConUi = list()
        self.tlConUi.append(self)

        # 透明度
        frameAlpha = Frame(self)
        frameAlpha.grid(row=0, column=0, sticky='nsew')
        self.tlConUi.append(frameAlpha)
        frameAlphaTitle = Frame(frameAlpha)
        frameAlphaTitle.grid(row=0, column=0, sticky='nsew')
        self.tlConUi.append(frameAlphaTitle)
        labelAlphaTitle = Label(frameAlphaTitle, text='透明度：', font=fontTemp, anchor='w')
        labelAlphaTitle.grid(row=0, column=0, sticky='w')
        self.tlConUi.append(labelAlphaTitle)
        labelAlpha = Label(frameAlphaTitle, text=GlobalValue.WINDOW_ALPHA, anchor='w')
        labelAlpha.grid(row=0, column=1, sticky='w')
        self.tlConUi.append(labelAlpha)
        self.labelAlpha = labelAlpha

        self.scaleAlphaVar = IntVar()
        self.scaleAlphaVar.set(GlobalValue.WINDOW_ALPHA)
        # showvalue=0隐藏数字
        scaleAlpha = Scale(frameAlpha, from_=30, to=100, length=300, orient="horizontal", variable=self.scaleAlphaVar, command=lambda e:self.onScaleAlphaChange(), showvalue=0)
        scaleAlpha.grid(row=1, column=0, sticky='e')
        # self.scaleAlpha = scaleAlpha
        self.tlConUi.append(scaleAlpha)

        # 风格
        frameStyle = Frame(self)
        frameStyle.grid(row=1, column=0, sticky='nsew', pady=10)
        self.tlConUi.append(frameStyle)
        labelStyleTitle = Label(frameStyle, text='风格', font=fontTemp, anchor='w')
        labelStyleTitle.grid(row=0, column=0, sticky='w')
        self.tlConUi.append(labelStyleTitle)
        buttonStyleDefault = Button(frameStyle, text='默认', command=lambda :self.onBtnStyleClick(StyleEnum.Default))
        buttonStyleDefault.grid(row=1, column=0, sticky='w')
        self.tlConUi.append(buttonStyleDefault)
        buttonStyleBlack = Button(frameStyle, text='黑色', command=lambda :self.onBtnStyleClick(StyleEnum.Black))
        buttonStyleBlack.grid(row=1, column=1, sticky='w', padx=2)
        self.tlConUi.append(buttonStyleBlack)

        # 选项
        frameOptions = Frame(self)
        frameOptions.grid(row=2, column=0, sticky='nsew', pady=10)
        self.tlConUi.append(frameOptions)
        labelOptionsTitle = Label(frameOptions, text='选项', font=fontTemp, anchor='w')
        labelOptionsTitle.grid(row=0, column=0, sticky='w')
        self.tlConUi.append(labelOptionsTitle)
        # 执行前询问选择框
        self.tmCheckbuttonAskExeVar = dict()
        # self.tmCheckbuttonAskExeVar.set(1 if GlobalValue.ASK_BEFORE_EXECUTING else 0)
        labelAskExe = Label(frameOptions, text='全局 执行前询问：', font=fontTemp, anchor='w')
        labelAskExe.grid(row=1, column=0, sticky='w')
        self.tlConUi.append(labelAskExe)
        frameAskExe = Frame(frameOptions)
        frameAskExe.grid(row=1, column=1, sticky='w')
        self.tlConUi.append(frameAskExe)
        if True:
            tempIndex = 0
            for i in range(0,len(GlobalValue.TL_SETTING_KEY)):
                typeStr = GlobalValue.TL_SETTING_KEY[i]
                if typeStr != 'line':
                    self.tmCheckbuttonAskExeVar[typeStr] = IntVar()
                    self.tmCheckbuttonAskExeVar[typeStr].set(1 if getOptionAskBeforeExecuting(typeStr) else 0)
                    checkbuttonAskExe = Checkbutton(frameAskExe, text=typeStr, variable=self.tmCheckbuttonAskExeVar[typeStr], command=lambda t=typeStr:self.onGlobalAskBeforeExecuting(t))
                    checkbuttonAskExe.grid(row=0, column=tempIndex, sticky='w', padx=2)
                    self.tlConUi.append(checkbuttonAskExe)
                    tempIndex += 1
        # checkbuttonAskExe = Checkbutton(frameOptions, text=str('全局 执行前询问'), variable=self.tmCheckbuttonAskExeVar, command=self.onGlobalAskBeforeExecuting)
        # checkbuttonAskExe.grid(row=1, column=0, sticky='w')
        self.tlConUi.append(checkbuttonAskExe)
        # 禁用右键编辑节点选择框
        self.checkbuttonDisableRCEditVar = IntVar()
        self.checkbuttonDisableRCEditVar.set(1 if GlobalValue.DISABLE_RCLICK_EDIT_NODE else 0)
        checkbuttonDisableRCEdit = Checkbutton(frameOptions, text=str('禁用右键编辑节点'), variable=self.checkbuttonDisableRCEditVar, command=self.onDisableRCEdit)
        checkbuttonDisableRCEdit.grid(row=2, column=0, sticky='w')
        self.tlConUi.append(checkbuttonDisableRCEdit)


        # 颜色
        frameColor = Frame(self)
        frameColor.grid(row=3, column=0, sticky='nsew', pady=10)
        self.tlConUi.append(frameColor)
        self.frameColor = frameColor
        frameColorRowIndex = 0
        lbPadding = 2
        labelColorTitle = Label(frameColor, text='颜色：(右键点击还原默认颜色)', font=fontTemp, anchor='w')
        labelColorTitle.grid(row=frameColorRowIndex, column=0, sticky='w')
        self.tlConUi.append(labelColorTitle)
        frameColorRowIndex += 1
        # 通用
        labelColorTemp = Label(frameColor, text='通用：', anchor='w')
        labelColorTemp.grid(row=frameColorRowIndex, column=0, sticky='w')
        self.tlConUi.append(labelColorTemp)
        frameColorRowIndex += 1
        if True:
            frameTemp = Frame(frameColor)
            frameTemp.grid(row=frameColorRowIndex, column=0, sticky='ew')
            self.tlConUi.append(frameTemp)
            frameColorRowIndex += 1
            tempRow = 0
            tempCol = 0
            lbTemp = self.createColorLabelBtn(frameTemp, '背景', ['common', 'bgColor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol += 1
            lbTemp = self.createColorLabelBtn(frameTemp, '前景', ['common', 'fgColor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol += 1
            lbTemp = self.createColorLabelBtn(frameTemp, '节点选中', ['common', 'selectColor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol += 1
            lbTemp = self.createColorLabelBtn(frameTemp, '画布背景', ['common', 'canvasBgColor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol += 1
            lbTemp = self.createColorLabelBtn(frameTemp, '按钮禁用文本', ['common', 'btnDisabledFgColor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol += 1
        # 输入框
        labelColorTemp = Label(frameColor, text='输入框：', anchor='w')
        labelColorTemp.grid(row=frameColorRowIndex, column=0, sticky='w')
        self.tlConUi.append(labelColorTemp)
        frameColorRowIndex += 1
        if True:
            frameTemp = Frame(frameColor)
            frameTemp.grid(row=frameColorRowIndex, column=0, sticky='ew')
            self.tlConUi.append(frameTemp)
            frameColorRowIndex += 1
            tempRow = 0
            tempCol = 0
            lbTemp = self.createColorLabelBtn(frameTemp, '背景', ['common', 'tkEntry', 'bgColor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol += 1
            lbTemp = self.createColorLabelBtn(frameTemp, '选中背景', ['common', 'tkEntry', 'selectBgColor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol += 1
            lbTemp = self.createColorLabelBtn(frameTemp, '选中前景', ['common', 'tkEntry', 'selectFgColor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol += 1
            lbTemp = self.createColorLabelBtn(frameTemp, '禁用背景', ['common', 'tkEntry', 'disabledBgColor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol += 1
            lbTemp = self.createColorLabelBtn(frameTemp, '禁用前景', ['common', 'tkEntry', 'disabledFgColor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol += 1
        # 滚动条
        labelColorTemp = Label(frameColor, text='滚动条：', anchor='w')
        labelColorTemp.grid(row=frameColorRowIndex, column=0, sticky='w')
        self.tlConUi.append(labelColorTemp)
        frameColorRowIndex += 1
        if True:
            frameTemp = Frame(frameColor)
            frameTemp.grid(row=frameColorRowIndex, column=0, sticky='ew')
            self.tlConUi.append(frameTemp)
            frameColorRowIndex += 1
            tempRow = 0
            tempCol = 0
            lbTemp = self.createColorLabelBtn(frameTemp, '槽背景', ['common', 'ttkScrollbar', 'troughcolor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol += 1
            lbTemp = self.createColorLabelBtn(frameTemp, '背景', ['common', 'ttkScrollbar', 'background', 'normal'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol += 1
            lbTemp = self.createColorLabelBtn(frameTemp, '选中背景', ['common', 'ttkScrollbar', 'background', 'active'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol += 1
            lbTemp = self.createColorLabelBtn(frameTemp, '禁用背景', ['common', 'ttkScrollbar', 'background', 'disabled'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol += 1
            lbTemp = self.createColorLabelBtn(frameTemp, '禁用箭头', ['common', 'ttkScrollbar', 'arrowcolor', 'disabled'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol += 1
        # 分割线
        labelColorTemp = Label(frameColor, text='分割线节点：', anchor='w')
        labelColorTemp.grid(row=frameColorRowIndex, column=0, sticky='w')
        self.tlConUi.append(labelColorTemp)
        frameColorRowIndex += 1
        if True:
            frameTemp = Frame(frameColor)
            frameTemp.grid(row=frameColorRowIndex, column=0, sticky='ew')
            self.tlConUi.append(frameTemp)
            frameColorRowIndex += 1
            tempRow = 0
            tempCol = 0
            lbTemp = self.createColorLabelBtn(frameTemp, '背景', ['line', 'bgColor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol += 1
            lbTemp = self.createColorLabelBtn(frameTemp, '文本', ['line', 'fgColor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol += 1
            lbTemp = self.createColorLabelBtn(frameTemp, '选中文本', ['line', 'selectFgColor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol += 1
        # 按钮节点
        labelColorTemp = Label(frameColor, text='按钮节点：', anchor='w')
        labelColorTemp.grid(row=frameColorRowIndex, column=0, sticky='w')
        self.tlConUi.append(labelColorTemp)
        frameColorRowIndex += 1
        if True:
            frameTemp = Frame(frameColor)
            frameTemp.grid(row=frameColorRowIndex, column=0, sticky='ew')
            self.tlConUi.append(frameTemp)
            frameColorRowIndex += 1
            tempRow = 0
            tempCol = 0
            spanTemp = 0
            labelTemp = Label(frameTemp, text='<通用>', anchor='w')
            labelTemp.grid(row=tempRow, column=tempCol, sticky='w')
            self.tlConUi.append(labelTemp)
            tempRow += 1
            lbTemp = self.createColorLabelBtn(frameTemp, '背景', ['btn', 'bgColor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol += 1
            lbTemp = self.createColorLabelBtn(frameTemp, '按钮背景', ['btn', 'btnBgColor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol += 1
            lbTemp = self.createColorLabelBtn(frameTemp, '按钮文本', ['btn', 'btnFgColor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol += 1
            lbTemp = self.createColorLabelBtn(frameTemp, '拖入标识背景', ['btn', 'markDropBgColor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol += 1
            lbTemp = self.createColorLabelBtn(frameTemp, '拖入标识文本', ['btn', 'markDropFgColor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol =0
            tempRow += 1
            lbTemp = self.createColorLabelBtn(frameTemp, '标记标识背景', ['btn', 'markBookmarkBgColor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol += 1
            lbTemp = self.createColorLabelBtn(frameTemp, '标记标识文本', ['btn', 'markBookmarkFgColor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol += 1
            lbTemp = self.createColorLabelBtn(frameTemp, '询问标识背景', ['btn', 'markAskExeBgColor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol += 1
            lbTemp = self.createColorLabelBtn(frameTemp, '询问标识文本', ['btn', 'markAskExeFgColor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol += 1
            lbTemp = self.createColorLabelBtn(frameTemp, '禁用类型背景', ['btn', 'typeDisableBgColor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol =0
            tempRow += 1
            lbTemp = self.createColorLabelBtn(frameTemp, '禁用类型文本', ['btn', 'typeDisableTextColor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol =0
            tempRow += 1
            labelTemp = Label(frameTemp, text='<folder>', anchor='w')
            labelTemp.grid(row=tempRow, column=tempCol, sticky='w')
            self.tlConUi.append(labelTemp)
            tempCol =0
            tempRow += 1
            lbTemp = self.createColorLabelBtn(frameTemp, '类型背景', ['folder', 'typeBgColor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol += 1
            lbTemp = self.createColorLabelBtn(frameTemp, '类型文本', ['folder', 'typeTextColor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol =0
            tempRow += 1
            labelTemp = Label(frameTemp, text='<exe>', anchor='w')
            labelTemp.grid(row=tempRow, column=tempCol, sticky='w')
            self.tlConUi.append(labelTemp)
            tempCol =0
            tempRow += 1
            lbTemp = self.createColorLabelBtn(frameTemp, '类型背景', ['exe', 'typeBgColor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol += 1
            lbTemp = self.createColorLabelBtn(frameTemp, '类型文本', ['exe', 'typeTextColor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol =0
            tempRow += 1
            labelTemp = Label(frameTemp, text='<cmd>', anchor='w')
            labelTemp.grid(row=tempRow, column=tempCol, sticky='w')
            self.tlConUi.append(labelTemp)
            tempCol =0
            tempRow += 1
            lbTemp = self.createColorLabelBtn(frameTemp, '类型背景', ['cmd', 'typeBgColor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol += 1
            lbTemp = self.createColorLabelBtn(frameTemp, '类型文本', ['cmd', 'typeTextColor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
        # 创建节点
        labelColorTemp = Label(frameColor, text='创建节点：', anchor='w')
        labelColorTemp.grid(row=frameColorRowIndex, column=0, sticky='w')
        self.tlConUi.append(labelColorTemp)
        frameColorRowIndex += 1
        if True:
            frameTemp = Frame(frameColor)
            frameTemp.grid(row=frameColorRowIndex, column=0, sticky='ew')
            self.tlConUi.append(frameTemp)
            frameColorRowIndex += 1
            tempRow = 0
            tempCol = 0
            lbTemp = self.createColorLabelBtn(frameTemp, '背景', ['create', 'bgColor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol += 1
            lbTemp = self.createColorLabelBtn(frameTemp, '前景', ['create', 'fgColor'])
            lbTemp.grid(row=tempRow, column=tempCol, padx=lbPadding, pady=lbPadding if tempRow > 0 else 0, sticky='w')
            tempCol += 1

        for i in range(0,len(self.tlConUi)):
            configureTkObjectColor(self.tlConUi[i])

        if not self.showColor:
            frameColor.grid_remove()

        # D == Shift-d
        self.bind('<Control-Alt-D>', lambda e:self.switchDebug())

    def onScaleAlphaChange(self):
        # py3_common.Logging.debug(self.scaleAlphaVar.get())
        # global WINDOW_ALPHA
        GlobalValue.WINDOW_ALPHA = self.scaleAlphaVar.get()
        self.labelAlpha.configure(text=GlobalValue.WINDOW_ALPHA)
        saveProjectSetting(False)
        self.initWindow.attributes("-alpha", GlobalValue.WINDOW_ALPHA/100.0)

    def createColorLabelBtn(self, frame, text, tlKey, width=10):
        labelBtn = Label(frame, text=text, width=width, relief='groove', borderwidth=2)
        self.updateLabelBtnColor(labelBtn, tlKey)
        labelBtn.bind('<Button-1>', lambda e,labelBtn=labelBtn,tlKey=tlKey:self.openAskColor(labelBtn, tlKey))
        def setDefaultColor(labelBtn, tlKey):
            colorTemp = getColorWithTlKey(tlKey, True)
            self.saveColor(labelBtn, tlKey, colorTemp)
        labelBtn.bind('<Button-3>', lambda e,labelBtn=labelBtn,tlKey=tlKey:setDefaultColor(labelBtn, tlKey))
        self.tlColorBtn.append([labelBtn, tlKey])
        return labelBtn

    def updateLabelBtnColor(self, labelBtn, tlKey, color=None):
        colorTemp = color
        if not colorTemp:
            colorTemp = getColorWithTlKeyAutoDefault(tlKey)
            # if not colorTemp:
            #     colorTemp = getColorWithTlKey(tlKey, True)
        if colorTemp:
            r,g,b = self.winfo_rgb(colorTemp)
            rw,gw,bw = self.winfo_rgb('white')
            rhm,ghm,bhm = 0.4,0.8,0.4   #绿色看起来最亮，亮度权重高点
            isLight = (r*rhm+g*ghm+b*bhm) > (rw*rhm+gw*ghm+bw*bhm)/3
            # py3_common.Logging.debug(colorTemp,r,g,b,rw,gw,bw,isLight)
            labelBtn.configure(bg=colorTemp, fg='black' if isLight else 'white')

    def openAskColor(self, labelBtn, tlKey):
        colorTemp = getColorWithTlKeyAutoDefault(tlKey)
        color = None
        if colorTemp:
            color_ = askcolor(title="颜色", color=colorTemp)
            if color_:
                py3_common.Logging.debug(color_)
                color = color_[1]
        else:
            color_ = askcolor(title="颜色")
            if color_:
                color = color_[1]
        # if not color:
        #     color = colorTemp if colorTemp else getColorWithTlKey(tlKey, True)
        if color:
            py3_common.Logging.debug(color)
            self.saveColor(labelBtn, tlKey, color)

    def saveColor(self, labelBtn, tlKey, color):
        # py3_common.Logging.debug2(color, self.winfo_rgb(color))
        setColorWithTlKey(tlKey, color)
        try:
            self.updateLabelBtnColor(labelBtn, tlKey)
            for i in range(0,len(self.tlConUi)):
                configureTkObjectColor(self.tlConUi[i])
        except Exception as e:
            py3_common.Logging.error(e)
            pass
        dispatchEvent(EventType.Event_SettingColorChange)
        dispatchEvent(EventType.Event_NodeChange)

    def onBtnStyleClick(self, styleType=StyleEnum.Default):
        # global TM_BTN_TYPE_COLOR
        # global STYLE_TYPE
        GlobalValue.STYLE_TYPE = styleType
        GlobalValue.TM_BTN_TYPE_COLOR = py3_common.deep_copy_dict(GlobalValue.TM_BTN_TYPE_COLOR_STYLE_DEFAULT[styleType])
        saveProjectSetting()
        try:
            for i in range(0,len(self.tlConUi)):
                configureTkObjectColor(self.tlConUi[i])
            for i in range(0,len(self.tlColorBtn)):
                self.updateLabelBtnColor(self.tlColorBtn[i][0], self.tlColorBtn[i][1])
        except Exception as e:
            py3_common.Logging.error(e)
            pass
        dispatchEvent(EventType.Event_SettingColorChange)
        dispatchEvent(EventType.Event_NodeChange)

    def switchDebug(self):
        self.showColor = not self.showColor
        if self.showColor:
            self.frameColor.grid()
        else:
            self.frameColor.grid_remove()

    # 全局执行前询问开关
    def onGlobalAskBeforeExecuting(self, typeStr):
        setOptionAskBeforeExecuting(typeStr, self.tmCheckbuttonAskExeVar[typeStr].get() > 0)
        saveProjectSetting()
        dispatchEvent(EventType.Event_SettingOptionsChange)

    # 禁用右键编辑节点开关
    def onDisableRCEdit(self):
        GlobalValue.DISABLE_RCLICK_EDIT_NODE = self.checkbuttonDisableRCEditVar.get() > 0
        saveProjectSetting()
        dispatchEvent(EventType.Event_SettingOptionsChange)
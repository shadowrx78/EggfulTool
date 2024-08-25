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



# 设置界面
class ViewRootSetting(BaseView):
    """
    设置界面
    参数:
    initWindow:tkObj 父界面
    """
    def __init__(self, initWindow):
        if self.checkUniqueNeedClose():
            return
        super(ViewRootSetting, self).__init__()
        self.initWindow = initWindow

        self.tlColorBtn = list()
        self.showColor = False
        self.isColorChange = False

        self.initUi()

    # 是否需要锁定焦点，子类重载
    def isNeedGrab(self):
        return True

    # 是否唯一，子类重载
    def isUnique(self):
        return True

    def initUi(self):
        self.title('设置')
        self.resizable(width=False, height=False)
        self.minsize(300, 10)
        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)

        # self.bind('<FocusIn>', lambda e:self.grab_set())
        self.protocol("WM_DELETE_WINDOW", self.onBtnCancel)
        self.bind('<Escape>', lambda e:self.onBtnCancel())
        self.bind('<Control-Return>', lambda e:self.onBtnConfirm())

        self.initEventListen()

        frameTop = Frame(self)
        frameTop.columnconfigure(0,weight=1)
        frameTop.grid(row=0,column=0,sticky='nsew')
        self.tkThemeHelper.addTkObj(frameTop)

        titleFont = py3_common.createTkFont(self, 13, kwargs={'weight':'bold'})
        title2Font = py3_common.createTkFont(self, 9, kwargs={'weight':'bold'})

        # 透明度
        if True:
            frameAlpha = Frame(frameTop)
            frameAlpha.grid(row=0, column=0, sticky='nsew', columnspan=1, rowspan=1)
            self.tkThemeHelper.addTkObj(frameAlpha)
            frameAlphaTitle = Frame(frameAlpha)
            frameAlphaTitle.grid(row=0, column=0, sticky='nsew')
            self.tkThemeHelper.addTkObj(frameAlphaTitle)
            labelAlphaTitle = Label(frameAlphaTitle, text='主界面透明度：', font=titleFont, anchor='w')
            labelAlphaTitle.grid(row=0, column=0, sticky='w')
            self.tkThemeHelper.addTkObj(labelAlphaTitle)
            labelAlpha = Label(frameAlphaTitle, text=GlobalValue.WINDOW_ALPHA, font=titleFont, anchor='w')
            labelAlpha.grid(row=0, column=1, sticky='w')
            self.tkThemeHelper.addTkObj(labelAlpha)
            self.labelAlpha = labelAlpha

            self.scaleAlphaVar = IntVar()
            self.scaleAlphaVar.set(GlobalValue.WINDOW_ALPHA)
            # showvalue=0隐藏数字
            scaleAlpha = Scale(frameAlpha, from_=30, to=100, length=300, orient="horizontal", variable=self.scaleAlphaVar, command=lambda e:self.onScaleAlphaChange(), showvalue=0)
            scaleAlpha.grid(row=1, column=0, sticky='e')
            # self.scaleAlpha = scaleAlpha
            self.tkThemeHelper.addTkObj(scaleAlpha)

            separatorTemp = ttk.Separator(frameAlpha)
            separatorTemp.grid(row=2,column=0,sticky='nsew',columnspan=1,rowspan=1)

        # 风格
        if True:
            frameStyle = Frame(frameTop)
            frameStyle.columnconfigure(0,weight=1)
            frameStyle.grid(row=1,column=0,sticky='nsew',columnspan=1,rowspan=1)
            self.tkThemeHelper.addTkObj(frameStyle)

            # 标题
            labelTitle = Label(frameStyle, text='风格：', anchor='w', font=titleFont)
            labelTitle.grid(row=0,column=0,sticky='nsew',columnspan=1,rowspan=1)
            self.tkThemeHelper.addTkObj(labelTitle)

            frameBtn = Frame(frameStyle)
            # frameBtn.columnconfigure(0,weight=1)
            frameBtn.grid(row=1,column=0,sticky='nsew',columnspan=1,rowspan=1)
            self.tkThemeHelper.addTkObj(frameBtn)

            padding = [2,2]
            buttonStyleDefault = Button(frameBtn, text='默认', command=lambda :self.onBtnStyleClick(StyleEnum.Default), takefocus=0)
            buttonStyleDefault.grid(row=1, column=0, sticky='w', padx=padding[0], pady=padding[1])
            self.tkThemeHelper.addTkObj(buttonStyleDefault)
            buttonStyleBlack = Button(frameBtn, text='黑色', command=lambda :self.onBtnStyleClick(StyleEnum.Black), takefocus=0)
            buttonStyleBlack.grid(row=1, column=1, sticky='w', padx=padding[0], pady=padding[1])
            self.tkThemeHelper.addTkObj(buttonStyleBlack)

            separatorTemp = ttk.Separator(frameStyle)
            separatorTemp.grid(row=2,column=0,sticky='nsew',columnspan=1,rowspan=1)

            # 单项颜色选择
            if True:
                frameColor = Frame(frameStyle)
                frameColor.grid(row=3,column=0,sticky='nsew',columnspan=1,rowspan=1)
                frameColor.columnconfigure(0,weight=1)
                self.tkThemeHelper.addTkObj(frameColor)
                self.frameColor = frameColor

                # 标题
                labelTitle = Label(frameColor, text='单项颜色（Debug）：', anchor='w', font=titleFont)
                labelTitle.grid(row=0,column=0,sticky='nsew',columnspan=1,rowspan=1)
                self.tkThemeHelper.addTkObj(labelTitle)

                tlTmColorData = [
                    {'title':'通用', 'tlColorData':[
                        ['背景', ['common', 'bgColor']],
                        ['前景', ['common', 'fgColor']],
                        ['选中背景', ['common', 'selectColor']],
                        ['选中前景', ['common', 'selectFgColor']],
                        ['画布背景', ['common', 'canvasBgColor']],
                        ['按钮禁用文本', ['common', 'btnDisabledFgColor']],
                        ['按钮文本', ['common', 'btnFgColor']],
                    ]},
                    {'title':'输入框', 'tlColorData':[
                        ['背景', ['common', 'tkEntry', 'bgColor']],
                        ['选中背景', ['common', 'tkEntry', 'selectBgColor']],
                        ['选中前景', ['common', 'tkEntry', 'selectFgColor']],
                        ['禁用背景', ['common', 'tkEntry', 'disabledBgColor']],
                        ['禁用前景', ['common', 'tkEntry', 'disabledFgColor']],
                        ['光标', ['common', 'tkEntry', 'insertbackground']],
                    ]},
                    {'title':'菜单', 'tlColorData':[
                        ['选中背景', ['common', 'tkMenu', 'selectBgColor']],
                        ['选中前景', ['common', 'tkMenu', 'selectFgColor']],
                    ]},
                    {'title':'滚动条', 'tlColorData':[
                        ['槽背景', ['common', 'ttkScrollbar', 'troughcolor']],
                        ['背景', ['common', 'ttkScrollbar', 'background', 'normal']],
                        ['选中背景', ['common', 'ttkScrollbar', 'background', 'active']],
                        ['禁用背景', ['common', 'ttkScrollbar', 'background', 'disabled']],
                        ['禁用箭头', ['common', 'ttkScrollbar', 'arrowcolor', 'disabled']],
                    ]},
                    {'title':'进度条', 'tlColorData':[
                        ['背景', ['common', 'ttkProgressbar', 'background']],
                    ]},
                    {'title':'下拉列表', 'tlColorData':[
                        ['槽背景', ['common', 'ttkCombobox', 'troughcolor']],
                        ['禁用背景', ['common', 'ttkCombobox', 'background', 'disabled']],
                        ['选中前景', ['common', 'ttkCombobox', 'foreground', 'active']],
                        ['选中禁用前景', ['common', 'ttkCombobox', 'foreground', 'disabled']],
                    ]},
                    # {'title':'表格', 'tlColorData':[
                    #     ['高亮背景', ['sheet', 'highlightBgColor']],
                    #     ['高亮前景', ['sheet', 'highlightFgColor']],
                    #     ['高亮背景2', ['sheet', 'highlightBgColor2']],
                    #     ['高亮前景2', ['sheet', 'highlightFgColor2']],
                    # ]},
                    {'title':'分割线节点', 'tlColorData':[
                        ['背景', ['line', 'bgColor']],
                        ['文本', ['line', 'fgColor']],
                        ['选中文本', ['line', 'selectFgColor']],
                    ]},
                    {'title':'按钮节点 - 通用', 'tlColorData':[
                        ['背景', ['btn', 'bgColor']],
                        ['按钮背景', ['btn', 'btnBgColor']],
                        ['按钮文本', ['btn', 'btnFgColor']],
                        ['拖入标识背景', ['btn', 'markDropBgColor']],
                        ['拖入标识文本', ['btn', 'markDropFgColor']],
                        ['标记标识背景', ['btn', 'markBookmarkBgColor']],
                        ['标记标识文本', ['btn', 'markBookmarkFgColor']],
                        ['询问标识背景', ['btn', 'markAskExeBgColor']],
                        ['询问标识文本', ['btn', 'markAskExeFgColor']],
                        ['禁用类型背景', ['btn', 'typeDisableBgColor']],
                        ['禁用类型文本', ['btn', 'typeDisableTextColor']],
                    ]},
                    {'title':'按钮节点 - folder', 'tlColorData':[
                        ['类型背景', ['folder', 'typeBgColor']],
                        ['类型文本', ['folder', 'typeTextColor']],
                    ]},
                    {'title':'按钮节点 - exe', 'tlColorData':[
                        ['类型背景', ['exe', 'typeBgColor']],
                        ['类型文本', ['exe', 'typeTextColor']],
                    ]},
                    {'title':'按钮节点 - cmd', 'tlColorData':[
                        ['类型背景', ['cmd', 'typeBgColor']],
                        ['类型文本', ['cmd', 'typeTextColor']],
                    ]},
                    {'title':'创建节点', 'tlColorData':[
                        ['背景', ['create', 'bgColor']],
                        ['前景', ['create', 'fgColor']],
                    ]},
                ]

                maxCol = 8
                padding = [4,1]
                realMaxCol = -1
                for x in range(0,len(tlTmColorData)):
                    realMaxCol = min(max(realMaxCol, len(tlTmColorData[x]['tlColorData'])), maxCol)

                def getColorBtnGridKwargs(num, maxCol=maxCol, padx=padding[0], pady=padding[1]):
                    tmGridArgs = dict()
                    tmGridArgs['row'] = math.floor(num/maxCol)
                    tmGridArgs['column'] = num % maxCol
                    tmGridArgs['padx'] = padx
                    # tmGridArgs['pady'] = pady if tmGridArgs['row'] > 0 else 0
                    tmGridArgs['pady'] = pady
                    return tmGridArgs

                rIndex = 1
                # 颜色按钮
                for x in range(0,len(tlTmColorData)):
                    tmColorData = tlTmColorData[x]
                    frameColorTemp = Frame(frameColor)
                    frameColorTemp.grid(row=x+1,column=0,sticky='nsew',columnspan=1,rowspan=1)
                    rIndex = x+1
                    # for i in range(0,realMaxCol):
                    #     frameColorTemp.columnconfigure(i,weight=1)
                    self.tkThemeHelper.addTkObj(frameColorTemp)
                    # 标题
                    labelTitleTemp = Label(frameColorTemp, text=tmColorData['title'] + '：', anchor='w', font=title2Font)
                    labelTitleTemp.grid(row=0,column=0,sticky='nsew',columnspan=1,rowspan=1)
                    self.tkThemeHelper.addTkObj(labelTitleTemp)

                    frameTemp = Frame(frameColorTemp)
                    frameTemp.grid(row=1,column=0,sticky='nsew',columnspan=1,rowspan=1)
                    self.tkThemeHelper.addTkObj(frameTemp)

                    for i in range(0,len(tmColorData['tlColorData'])):
                        data = tmColorData['tlColorData'][i]
                        lbTemp = self.createColorLabelBtn(frameTemp, data[0], data[1])
                        lbTemp.grid(sticky='w', **getColorBtnGridKwargs(i))

                separatorTemp = ttk.Separator(frameColor)
                separatorTemp.grid(row=rIndex+1,column=0,sticky='nsew',columnspan=1,rowspan=1)

        # 选项
        if True:
            frameOptions = Frame(frameTop)
            frameOptions.columnconfigure(0,weight=1)
            frameOptions.grid(row=2, column=0, sticky='nsew', columnspan=1, rowspan=1)
            self.tkThemeHelper.addTkObj(frameOptions)
            labelOptionsTitle = Label(frameOptions, text='选项', font=titleFont, anchor='w')
            labelOptionsTitle.grid(row=0, column=0, sticky='w')
            self.tkThemeHelper.addTkObj(labelOptionsTitle)
            # 执行前询问选择框
            self.tmCheckbuttonAskExeVar = dict()
            # self.tmCheckbuttonAskExeVar.set(1 if GlobalValue.ASK_BEFORE_EXECUTING else 0)
            frameAskExe = Frame(frameOptions)
            frameAskExe.grid(row=1, column=0, sticky='w')
            self.tkThemeHelper.addTkObj(frameAskExe)
            labelAskExe = Label(frameAskExe, text='全局 执行前询问：', anchor='w')
            labelAskExe.grid(row=0, column=0, sticky='w')
            self.tkThemeHelper.addTkObj(labelAskExe)
            frameAskExeCBtn = Frame(frameAskExe)
            frameAskExeCBtn.grid(row=0, column=1, sticky='w')
            self.tkThemeHelper.addTkObj(frameAskExeCBtn)
            if True:
                tempIndex = 0
                for i in range(0,len(GlobalValue.TL_SETTING_KEY)):
                    typeStr = GlobalValue.TL_SETTING_KEY[i]
                    if typeStr != 'line':
                        self.tmCheckbuttonAskExeVar[typeStr] = IntVar()
                        self.tmCheckbuttonAskExeVar[typeStr].set(1 if getOptionAskBeforeExecuting(typeStr) else 0)
                        checkbuttonAskExe = Checkbutton(frameAskExeCBtn, text=typeStr, variable=self.tmCheckbuttonAskExeVar[typeStr], takefocus=0)
                        checkbuttonAskExe.grid(row=0, column=tempIndex, sticky='w', padx=2)
                        self.tkThemeHelper.addTkObj(checkbuttonAskExe)
                        tempIndex += 1
            # checkbuttonAskExe = Checkbutton(frameOptions, text=str('全局 执行前询问'), variable=self.tmCheckbuttonAskExeVar, command=self.onGlobalAskBeforeExecuting)
            # checkbuttonAskExe.grid(row=1, column=0, sticky='w')
            self.tkThemeHelper.addTkObj(checkbuttonAskExe)
            # 禁用右键编辑节点选择框
            self.checkbuttonDisableRCEditVar = IntVar()
            self.checkbuttonDisableRCEditVar.set(1 if GlobalValue.DISABLE_RCLICK_EDIT_NODE else 0)
            checkbuttonDisableRCEdit = Checkbutton(frameOptions, text=str('禁用右键编辑节点'), variable=self.checkbuttonDisableRCEditVar, takefocus=0)
            checkbuttonDisableRCEdit.grid(row=2, column=0, sticky='w')
            self.tkThemeHelper.addTkObj(checkbuttonDisableRCEdit)

            separatorTemp = ttk.Separator(frameOptions)
            separatorTemp.grid(row=3,column=0,sticky='nsew',columnspan=1,rowspan=1)



        frameBottom = Frame(self)
        frameBottom.rowconfigure(1,weight=1)
        frameBottom.columnconfigure(0,weight=1)
        frameBottom.columnconfigure(1,weight=1)
        frameBottom.grid(row=1,column=0,sticky='nsew')
        self.tkThemeHelper.addTkObj(frameBottom)

        frameTempWH = (120,10)
        frmTemp = Frame(frameBottom, height=frameTempWH[1], width=frameTempWH[0])
        frmTemp.grid(row=0, column=0, columnspan=2, rowspan=1)
        self.tkThemeHelper.addTkObj(frmTemp)

        # 确定取消按钮
        if True:
            buttonConfirm = Button(frameBottom, text='确定', width=10, command=self.onBtnConfirm, takefocus=0)
            buttonConfirm.grid(row=1, column=0)
            self.tkThemeHelper.addTkObj(buttonConfirm)
            buttonCancel = Button(frameBottom, text='取消', width=10, command=self.onBtnCancel, takefocus=0)
            buttonCancel.grid(row=1, column=1)
            self.tkThemeHelper.addTkObj(buttonCancel)

        if not self.showColor:
            self.frameColor.grid_remove()
        self.bind('<Control-Alt-Shift-D>', lambda e:self.switchDebug())

        self.tkThemeHelper.update()

    def initEventListen(self):
        self.removeAllEventListen()
        self.addEventListener(EventType.Event_SettingColorChange, self.onEvent_SettingColorChange)




    # -----------------------------按钮响应-----------------------------
    def onScaleAlphaChange(self):
        # py3_common.Logging.debug(self.scaleAlphaVar.get())
        # global WINDOW_ALPHA
        # GlobalValue.WINDOW_ALPHA = self.scaleAlphaVar.get()
        alpha = self.scaleAlphaVar.get()
        self.labelAlpha.configure(text=alpha)
        # saveProjectSetting(False)
        # GlobalValue.INIT_WINDOW.attributes("-alpha", alpha/100.0)
        setInitWindowAlpha(alpha)

    # 确定修改
    def onBtnConfirm(self):
        py3_common.Logging.debug(self.getClassName(),'onBtnConfirm')

        # 透明度
        GlobalValue.WINDOW_ALPHA = self.scaleAlphaVar.get()
        # 全局执行前询问开关
        for i in range(0,len(GlobalValue.TL_SETTING_KEY)):
            typeStr = GlobalValue.TL_SETTING_KEY[i]
            if typeStr != 'line':
                setOptionAskBeforeExecuting(typeStr, self.tmCheckbuttonAskExeVar[typeStr].get() > 0)
        # 禁用右键编辑节点开关
        GlobalValue.DISABLE_RCLICK_EDIT_NODE = self.checkbuttonDisableRCEditVar.get() > 0

        # 保存
        saveProjectSetting()
        dispatchEvent(EventType.Event_SettingOptionsChange)

        self.close()

    # 取消
    def onBtnCancel(self):
        py3_common.Logging.debug(self.getClassName(),'onBtnCancel')
        isColorChange = self.isColorChange

        # 关闭
        self.close()

        # 透明度
        alpha = self.scaleAlphaVar.get()
        if alpha != GlobalValue.WINDOW_ALPHA:
            setInitWindowAlpha()

        if isColorChange:
            refreshProjectSetting()
            dispatchEvent(EventType.Event_SettingColorChange)

    # 风格
    def onBtnStyleClick(self, styleType=StyleEnum.Default):
        py3_common.Logging.debug(self.getClassName(),'onBtnStyleClick', styleType)
        GlobalValue.STYLE_TYPE = styleType
        GlobalValue.TM_BTN_TYPE_COLOR = py3_common.deep_copy_dict(GlobalValue.TM_BTN_TYPE_COLOR_STYLE_DEFAULT[styleType])
        # saveProjectSetting()
        dispatchEvent(EventType.Event_SettingColorChange)




    # -----------------------------颜色选择相关-----------------------------
    # 创建颜色选择按钮
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
            color_ = askcolor(title="颜色", color=colorTemp, parent=self)
            if color_:
                py3_common.Logging.debug(color_)
                color = color_[1]
        else:
            color_ = askcolor(title="颜色", parent=self)
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
            self.tkThemeHelper.update()
        except Exception as e:
            py3_common.Logging.error(e)
            pass
        dispatchEvent(EventType.Event_SettingColorChange)

    def switchDebug(self):
        self.showColor = not self.showColor
        if self.showColor:
            self.frameColor.grid()
        else:
            self.frameColor.grid_remove()




    # -----------------------------事件响应-----------------------------
    def onEvent_SettingColorChange(self):
        self.isColorChange = True
        for i in range(0,len(self.tlColorBtn)):
            self.updateLabelBtnColor(self.tlColorBtn[i][0], self.tlColorBtn[i][1])
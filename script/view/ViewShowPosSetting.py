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



TM_POS_BTN_STR = {}
if True:
    TM_POS_BTN_STR[ViewPosEnum.LeftDown] = '↙'
    TM_POS_BTN_STR[ViewPosEnum.Down] = '↓'
    TM_POS_BTN_STR[ViewPosEnum.RightDown] = '↘'
    TM_POS_BTN_STR[ViewPosEnum.Left] = '←'
    TM_POS_BTN_STR[ViewPosEnum.Center] = '◉'
    TM_POS_BTN_STR[ViewPosEnum.Right] = '→'
    TM_POS_BTN_STR[ViewPosEnum.LeftUp] = '↖'
    TM_POS_BTN_STR[ViewPosEnum.Up] = '↑'
    TM_POS_BTN_STR[ViewPosEnum.RightUp] = '↗'

# 界面位置设置界面
class ViewShowPosSetting(BaseView):
    """
    界面位置设置界面
    参数:
    initWindow:tkObj 父界面
    key:any 用于判断的标记，通过事件返回
    oldValue?:ViewPosEnum 旧值，位置枚举
    titleStr?:string 界面标题
    """
    def __init__(self, initWindow, key, oldValue=None, titleStr=None):
        if self.checkUniqueNeedClose():
            return
        super(ViewShowPosSetting, self).__init__()
        self.initWindow = initWindow

        self.key = key
        self.oldValue = oldValue or GlobalValue.ViewPosEnum.Center
        self.value = self.oldValue
        self.titleStr = titleStr or '设置界面弹出位置'
        self.tlPosBtnData = list()

        self.initUi()

    # 是否需要锁定焦点，子类重载
    def isNeedGrab(self):
        return True

    # 是否唯一，子类重载
    def isUnique(self):
        return True

    def initUi(self):
        self.title(self.titleStr)
        self.resizable(width=False, height=False)
        self.minsize(200, 200)
        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)

        # self.bind('<FocusIn>', lambda e:self.grab_set())
        self.protocol("WM_DELETE_WINDOW", self.onBtnCancel)
        self.bind('<Escape>', lambda e:self.onBtnCancel())
        self.bind('<Control-Return>', lambda e:self.onBtnConfirm())

        # self.initEventListen()

        frameTop = Frame(self)
        frameTop.columnconfigure(0,weight=1)
        frameTop.grid(row=0,column=0,sticky='nsew')
        self.tkThemeHelper.addTkObj(frameTop)


        # 位置按钮
        if True:
            frameBtn = Frame(frameTop)
            frameBtn.grid(row=0,column=0,sticky='',pady=20)
            self.tkThemeHelper.addTkObj(frameBtn)

            tlTlPosBtnValue = [
                [GlobalValue.ViewPosEnum.LeftUp, GlobalValue.ViewPosEnum.Up, GlobalValue.ViewPosEnum.RightUp],
                [GlobalValue.ViewPosEnum.Left, GlobalValue.ViewPosEnum.Center, GlobalValue.ViewPosEnum.Right],
                [GlobalValue.ViewPosEnum.LeftDown, GlobalValue.ViewPosEnum.Down, GlobalValue.ViewPosEnum.RightDown],
            ]

            maxCol = -1
            maxRow = len(tlTlPosBtnValue)
            if maxRow >= 0:
                for i in range(0,maxRow):
                    frameBtn.rowconfigure(i,weight=1)
                    maxCol = max(maxCol, len(tlTlPosBtnValue[i]))
            if maxCol >= 0:
                for i in range(0,maxCol):
                    frameBtn.columnconfigure(i,weight=1)

            for i in range(0,len(tlTlPosBtnValue)):
                tlPosBtnValue = tlTlPosBtnValue[i]
                for j in range(0,len(tlPosBtnValue)):
                    frameTemp = Frame(frameBtn)
                    frameTemp.grid(row=i,column=j,sticky='nsew')
                    self.tkThemeHelper.addTkObj(frameTemp)
                    self.createPosBtn(frameTemp, tlPosBtnValue[j])



        frameBottom = Frame(self)
        frameBottom.rowconfigure(1,weight=1)
        frameBottom.columnconfigure(0,weight=1)
        frameBottom.columnconfigure(1,weight=1)
        frameBottom.grid(row=1,column=0,sticky='nsew')
        self.tkThemeHelper.addTkObj(frameBottom)

        # frameTempWH = (120,10)
        # frmTemp = Frame(frameBottom, height=frameTempWH[1], width=frameTempWH[0])
        # frmTemp.grid(row=0, column=0, columnspan=2, rowspan=1)
        # self.tkThemeHelper.addTkObj(frmTemp)

        # 确定取消按钮
        if True:
            buttonConfirm = Button(frameBottom, text='确定', width=10, command=self.onBtnConfirm, takefocus=0)
            buttonConfirm.grid(row=1, column=0)
            self.tkThemeHelper.addTkObj(buttonConfirm)
            buttonCancel = Button(frameBottom, text='取消', width=10, command=self.onBtnCancel, takefocus=0)
            buttonCancel.grid(row=1, column=1)
            self.tkThemeHelper.addTkObj(buttonCancel)

        self.tkThemeHelper.update()
        self.updateAllPosBtn()

    # def initEventListen(self):
    #     self.removeAllEventListen()
    #     self.addEventListener(EventType.Event_SettingColorChange, self.onEvent_SettingColorChange)




    # -----------------------------按钮响应-----------------------------
    # 确定修改
    def onBtnConfirm(self):
        py3_common.Logging.debug(self.getClassName(),'onBtnConfirm')

        dispatchEvent(EventType.Event_SettingViewShowPosSettingConfirm, self.key, self.value)

        self.close()

    # 取消
    def onBtnCancel(self):
        py3_common.Logging.debug(self.getClassName(),'onBtnCancel')

        # 关闭
        self.close()




    # -----------------------------位置按钮相关-----------------------------
    # 创建位置按钮
    def createPosBtn(self, frame, viewPosEnum):
        borderwidth=2
        btnSize={'width':40, 'height':40}
        frameBase = Frame(frame, relief='sunken', bg='black', width=btnSize['width']+borderwidth*2, height=btnSize['height']+borderwidth*2)
        frameBase.grid_propagate(False)
        frameBase.pack(expand=True)
        frameBase.rowconfigure(0,weight=1)
        frameBase.columnconfigure(0,weight=1)
        # frameBase.grid(row=0, column=0, sticky='nsew')
        self.tkThemeHelper.addTkObj(frameBase)
        frameBtn = Frame(frameBase, relief='sunken', bg='black', width=btnSize['width'], height=btnSize['height'])
        frameBtn.grid_propagate(False)
        # frameBtn.pack(expand=False)
        frameBtn.grid(row=0, column=0, sticky='')
        frameBtn.rowconfigure(0,weight=1)
        frameBtn.columnconfigure(0,weight=1)
        self.tkThemeHelper.addTkObj(frameBtn)

        button = Button(frameBtn, text=self.getPosBtnText(viewPosEnum), command=lambda v=viewPosEnum:self.onPosBtnClick(v), takefocus=0)
        button.grid(row=0,column=0,sticky='nsew')

        self.tlPosBtnData.append([button, viewPosEnum, frameBtn])
        return button

    def getPosBtnText(self, viewPosEnum):
        return TM_POS_BTN_STR[viewPosEnum] if viewPosEnum in TM_POS_BTN_STR else ''

    def onPosBtnClick(self, viewPosEnum):
        if viewPosEnum == self.value:
            return
        self.value = viewPosEnum
        self.updateAllPosBtn()

    def updateAllPosBtn(self):
        # 选中按钮变颜色
        fc_ = getColorWithTlKeyAutoDefault
        tmBtnHighLightParams = {
            'bg':fc_(['common', 'btnFgColor']),
            'fg':fc_(['common', 'bgColor']),
            'activebackground':fc_(['common', 'btnFgColor']),
            'activeforeground':fc_(['common', 'bgColor']),
            'disabledforeground':fc_(['common', 'btnDisabledFgColor'])
        }

        for i in range(0,len(self.tlPosBtnData)):
            data = self.tlPosBtnData[i]
            btn = data[0]
            value = data[1]
            if value == self.value:
                btn.configure(**tmBtnHighLightParams)
            else:
                configureTkObjectColor(btn)
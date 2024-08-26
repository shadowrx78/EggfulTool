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

# 按钮节点
class BtnNode(tkVirtualListHelper.BaseNode):
    """
    按钮节点
    参数:
    args:
        nodeType:string 节点类型标记,默认'Base'
        bgColor:string 节点背景颜色
        btnText:string 按钮上显示文本
        width:int 宽
        height:int 高
        typeStr:string 按钮类型
        useDrop:bool 是否启用拖入
        其他参数由对应脚本定义
    """
    def __init__(self, initWindow, args=dict(), autoInit=True):
        self.bingDrop = False
        super(BtnNode, self).__init__(initWindow, args, autoInit)
        # self.initWindow = initWindow
        # self.args = args

        # if autoInit:
        #     self.initUi()

    def __del__(self):
        py3_common.Logging.info2('BtnNode __del__')

    def initUi(self):
        super(BtnNode, self).initUi()

        args = self.args

        self.rowconfigure(1,weight=1)
        self.columnconfigure(0,weight=1)

        # width = args['width'] if 'width' in args else GlobalValue.FRAME_DEFAULT_WIDTH
        # height = args['height'] if 'height' in args else GlobalValue.FRAME_DEFAULT_HEIGHT
        # self.setContentSize(width=width, height=height)

        # bgColor = args['bgColor'] if 'bgColor' in args else GlobalValue.BG_COLOR
        # self.configure(bg=bgColor)

        self.frameType = Frame(self)
        self.frameType.grid(row=0,column=0,sticky='ew')
        self.frameType.columnconfigure(0,weight=1)
        self.labelType = Label(self.frameType, text='', anchor='w')
        self.labelType.grid(row=0,column=0,sticky='ew')
        self.labelDrop = Label(self.frameType, text='D', anchor='e')
        self.labelDrop.grid(row=0,column=1,sticky='e')
        self.labelDrop.grid_remove()
        self.labelBookmark = Label(self.frameType, text='M', anchor='e')
        self.labelBookmark.grid(row=0,column=2,sticky='e')
        self.labelBookmark.grid_remove()
        self.labelAskExe = Label(self.frameType, text='A', anchor='e')
        self.labelAskExe.grid(row=0,column=3,sticky='e')
        self.labelAskExe.grid_remove()

        self.frame1 = Frame(self, relief='sunken')
        self.frame1.grid(row=1,column=0,sticky='nsew')
        # self.frame1.grid_propagate(False)
        # self.frame1.rowconfigure(0,weight=1)
        # self.frame1.columnconfigure(0,weight=1)

        # self.frameBtn = Frame(self.frame1, relief='sunken', bg='black', width=width-20, height=height-40)
        self.frameBtn = Frame(self.frame1, relief='sunken', bg='black')
        self.frameBtn.grid_propagate(False)
        # self.frameBtn.grid(row=0,column=0,sticky='nsew')
        self.frameBtn.pack(expand=True)
        self.frameBtn.rowconfigure(0,weight=1)
        self.frameBtn.columnconfigure(0,weight=1)

        # btnText = args['btnText'] if 'btnText' in args else ''
        # print(self.frame1.winfo_width(), self.frame1.winfo_height())
        # self.button = Button(self.frame1, image=pixelVirtual, text=btnText, width=self.frame1.winfo_width()-20, height=self.frame1.winfo_height()-20)
        # self.button = Button(self.frame1, image=pixelVirtual, text=btnText, width=width-20, height=height-40)
        self.button = Button(self.frameBtn, text='', command=self.onBtnClick, takefocus=0)
        self.button.grid(row=0,column=0,sticky='nsew')

        self.button.bind('<Button-3>', self.onBtnRightClick)
        self.button.bind('<FocusIn>', lambda e:GlobalValue.INIT_WINDOW.focus_force())
        self.labelType.bind('<Button-3>', self.onBtnRightClick)
        self.frame1.bind('<Button-3>', self.onBtnRightClick)
        self.frameBtn.bind('<Button-3>', self.onBtnRightClick)

        self.updateArgs(args)

    def updateArgs(self, args=dict()):
        super(BtnNode, self).updateArgs(args)

        dw, dh = self.getDefaultSize()
        width = args['width'] if 'width' in args else dw
        height = args['height'] if 'height' in args else dh
        self.setContentSize(width=width, height=height)

        fc_ = getColorWithTlKeyAutoDefault
        self.labelDrop.configure(bg=fc_(['btn', 'markDropBgColor']), fg=fc_(['btn', 'markDropFgColor']))
        self.labelBookmark.configure(bg=fc_(['btn', 'markBookmarkBgColor']), fg=fc_(['btn', 'markBookmarkFgColor']))
        self.labelAskExe.configure(bg=fc_(['btn', 'markAskExeBgColor']), fg=fc_(['btn', 'markAskExeFgColor']))

        bgColor = fc_(['btn', 'bgColor'])
        self.configure(bg=bgColor)

        isDisable = 'disable' in args and args['disable']
        self.labelType.configure(text=str(args['typeStr']), fg=self._getPartColor('typeTextColor') if not isDisable else fc_(['btn', 'typeDisableTextColor']), bg=self._getPartColor('typeBgColor') if not isDisable else fc_(['btn', 'typeDisableBgColor']))
        self.labelType.grid()
        if 'useDrop' in args and args['useDrop']:
            self.labelDrop.grid()
            # 添加拖入事件
            if not self.bingDrop:
                self.bingDrop = True
                args['dnd'].bindtarget(self.button, 'text/uri-list', '<Drop>', self.onDrop, ('%D',))
        else:
            self.labelDrop.grid_remove()
            # 清除拖入事件
            if self.bingDrop:
                self.bingDrop = False
                args['dnd'].cleartarget(self.button)
        if 'bookmark' in args and args['bookmark']:
            self.labelBookmark.grid()
        else:
            self.labelBookmark.grid_remove()
        if 'askExeMark' in args and args['askExeMark']:
            self.labelAskExe.grid()
        else:
            self.labelAskExe.grid_remove()

        self.frame1.configure(bg=bgColor)
        self.frame1.grid()
        # self.frame1.grid_propagate(False)
        # self.frame1.rowconfigure(0,weight=1)
        # self.frame1.columnconfigure(0,weight=1)

        self.frameBtn.configure(width=width-20, height=height-40, bg=bgColor)
        # self.frameBtn.grid_propagate(False)
        # self.frameBtn.grid(row=0,column=0,sticky='nsew')
        self.frameBtn.pack(expand=True)
        # self.frameBtn.rowconfigure(0,weight=1)
        # self.frameBtn.columnconfigure(0,weight=1)

        btnText = args['btnText'] if 'btnText' in args else ''
        # print(self.frame1.winfo_width(), self.frame1.winfo_height())
        # self.button = Button(self.frame1, image=pixelVirtual, text=btnText, width=self.frame1.winfo_width()-20, height=self.frame1.winfo_height()-20)
        # self.button = Button(self.frame1, image=pixelVirtual, text=btnText, width=width-20, height=height-40)

        # pilImage = Image.open('img_maincontrol_icon_beibao001_word.png')
        # pilImage = pilImage.convert('RGBA')
        # self.imageTk = getTkImage(pilImage, 16)
        self.button.configure(text=btnText, bg=fc_(['btn', 'btnBgColor']), fg=fc_(['btn', 'btnFgColor']),
                                activebackground=fc_(['btn', 'btnBgColor']), activeforeground=fc_(['btn', 'btnFgColor'])
                                )
                                # , image=self.imageTk, compound= LEFT)
        self.button.grid()


    def _getPartColor(self, key):
        args = self.args
        # tmDefaultColor = GlobalValue.TM_BTN_TYPE_COLOR[args['typeStr']] if args['typeStr'] in GlobalValue.TM_BTN_TYPE_COLOR else None
        return args[key] if key in args else (getColorWithTlKeyAutoDefault([args['typeStr'], key]) or GlobalValue.BG_COLOR)

    def onConfigure(self, event):
        super(BtnNode, self).onConfigure(event)
        # if hasattr(self, 'label'):
        #     # 重新设置label位置
        #     self.label.grid(row=0,column=0,sticky='nsew')
        pass

    # 获取默认大小
    def getDefaultSize(self):
        defaultSize = GlobalValue.TM_NODE_TYPE[self.getType()]['defaultSize']
        return defaultSize['width'], defaultSize['height']


    def changeBg(self, bg=None):
        if not bg:
            bg = GlobalValue.BG_COLOR
        self.configure(bg=bg)
        self.frame1.configure(bg=bg)

    def setExData(self, exData, update=True):
        super(BtnNode, self).setExData(exData, update)
        args = self.args
        bgColor = getColorWithTlKeyAutoDefault(['btn', 'bgColor'])
        if (GlobalValue.UI_MODE == UiModeEnum.Edit or GlobalValue.FORCE_SHOW_SELECT) and (self.getExData('index') != None and self.getExData('index') == GlobalValue.NOW_SELECT_INDEX):
            bgColor = getColorWithTlKeyAutoDefault(['common', 'selectColor'])
        self.changeBg(bg=bgColor)

    def onDrop(self, files=''):
        if not self.bingDrop:
            return
        if GlobalValue.UI_MODE == UiModeEnum.Normal:
            tlFile = py3_common.parseDndFiles(files)
            py3_common.Logging.debug(tlFile)
            try:
                args = self.args
                if 'disable' in args and args['disable']:
                    return
                askExeMark = 'askExeMark' in args and args['askExeMark']
                globalAskExe = getOptionAskBeforeExecuting(args['typeStr'])
                if (not globalAskExe and askExeMark) or (globalAskExe and not askExeMark):
                    btnText = args['btnText'] if 'btnText' in args else ''
                    btnText = btnText.replace('\n', '')
                    value = messagebox.askokcancel('确认', '是否执行%s？' % btnText)
                    if not value:
                        return
                script = getImportModule(getModuleNameWithTypeStr(args['typeStr']))
                # 多线程调用，防止卡死界面
                if GlobalValue.ROOT_THREAD_POOL_EXECUTOR:
                    thread = GlobalValue.ROOT_THREAD_POOL_EXECUTOR.submit(script.onDrop, args, tlFile)
                else:
                    script.onDrop(args, tlFile)
            except Exception as e:
                py3_common.Logging.error(e)
        # self.after(1, lambda: GlobalValue.INIT_WINDOW.focus_force())

    def onBtnClick(self):
        if GlobalValue.UI_MODE == UiModeEnum.Normal:
            try:
                args = self.args
                if 'disable' in args and args['disable']:
                    return
                askExeMark = 'askExeMark' in args and args['askExeMark']
                globalAskExe = getOptionAskBeforeExecuting(args['typeStr'])
                if (not globalAskExe and askExeMark) or (globalAskExe and not askExeMark):
                    btnText = args['btnText'] if 'btnText' in args else ''
                    btnText = btnText.replace('\n', '')
                    value = messagebox.askokcancel('确认', '是否执行%s？' % btnText)
                    if not value:
                        return
                script = getImportModule(getModuleNameWithTypeStr(args['typeStr']))
                # 多线程调用，防止卡死界面
                if GlobalValue.ROOT_THREAD_POOL_EXECUTOR:
                    thread = GlobalValue.ROOT_THREAD_POOL_EXECUTOR.submit(script.onBtnClick, args)
                else:
                    script.onBtnClick(args)
            except Exception as e:
                py3_common.Logging.error(e)
        elif GlobalValue.UI_MODE == UiModeEnum.Edit:
            try:
                args = self.args
                args['mainView'].openViewNodeSetting(self.getExData('index'), args)
            except Exception as e:
                py3_common.Logging.error(e)

    def onBtnRightClick(self, event):
        py3_common.Logging.info('-----BtnNode onBtnRightClick-----')
        if GlobalValue.UI_MODE == UiModeEnum.Normal:
            if GlobalValue.DISABLE_RCLICK_EDIT_NODE:
                return
            try:
                args = self.args
                args['mainView'].openViewNodeSetting(self.getExData('index'), args)
            except Exception as e:
                py3_common.Logging.error(e)
        elif GlobalValue.UI_MODE == UiModeEnum.Edit:
            args = self.args
            args['mainView'].selectEditItem(self.getExData('index'))
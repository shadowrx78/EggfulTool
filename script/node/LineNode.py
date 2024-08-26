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

# 分割线节点
class LineNode(tkVirtualListHelper.BaseNode):
    """docstring for LineNode"""
    def __init__(self, initWindow, args=None, autoInit=True):
        # self.widthShift = 0
        # self.heightShift = 0
        super(LineNode, self).__init__(initWindow, args, autoInit)

    def __del__(self):
        py3_common.Logging.info2('LineNode __del__')

    def initUi(self):
        super(LineNode, self).initUi()
        # self.configure(relief='solid', bd=1)

        args = self.args
        # 为了居中要设置权重 横纵都要
        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=1)

        # height = args['height'] if 'height' in args else 20
        # self.refreshSize(height=height)

        # strLine = ''
        # for x in range(0,400):
        #     strLine = strLine + '-'
        # text = args['text'] if 'text' in args else ''
        label = Label(self, text='', anchor='center')
        label.grid(row=0,column=0,sticky='nsew')
        self.label = label
        self.labelBgColor = label['bg']
        self.labelFgColor = label['fg']

        self.label.bind('<Button-1>', self.onLeftClick)
        self.label.bind('<Button-3>', self.onRightClick)

        self.updateArgs(args)

    def updateArgs(self, args=None):
        if args == None:
            args = dict()
        super(LineNode, self).updateArgs(args)

        if 'height' in args:
            self.refreshSize(height=args['height'])
        else:
            dw, dh = self.getDefaultSize()
            self.refreshSize(height=dh)

        bgColor = args['bgColor'] if 'bgColor' in args else getColorWithTlKeyAutoDefault(['line', 'bgColor'])
        # print("bgColor", bgColor)
        # self.changeBg(bgColor)
        self.labelBgColor = bgColor
        fgColor = args['fgColor'] if 'fgColor' in args else getColorWithTlKeyAutoDefault(['line', 'fgColor'])
        self.labelFgColor = fgColor
        self.label.configure(bg=bgColor, fg=fgColor)

        strLineTag = args['lineTag'] if 'lineTag' in args else '-'
        strLine = ''
        for x in range(0,400):
            strLine = strLine + strLineTag
        text = args['text'] if 'text' in args else ''
        text = text.replace('\n', '')

        tkFontActual = font.nametofont("TkDefaultFont").actual()
        fontSize = args['fontSize'] if 'fontSize' in args else GlobalValue.DEFAULT_TK_FONT_SIZE
        localFont = font.Font(self, size=fontSize)
        if 'weight' in tkFontActual:
            localFont.configure(weight=tkFontActual['weight'])
        if 'family' in tkFontActual:
            localFont.configure(family=tkFontActual['family'])
        if 'slant' in tkFontActual:
            localFont.configure(slant=tkFontActual['slant'])
        if 'underline' in tkFontActual:
            localFont.configure(underline=tkFontActual['underline'])
        if 'overstrike' in tkFontActual:
            localFont.configure(overstrike=tkFontActual['overstrike'])
        # self.label.configure(text=strLine + text + strLine, fg=fgColor, font=('TkDefaultFont', args['fontSize'] if 'fontSize' in args else GlobalValue.DEFAULT_TK_FONT_SIZE))
        # self.label.configure(text=strLine + text + strLine, fg=fgColor)
        self.label.configure(text=strLine + text + strLine, fg=fgColor, font=localFont)
        self.label.grid(row=0,column=0,sticky='nsew')

    def onConfigure(self, event):
        super(LineNode, self).onConfigure(event)
        if hasattr(self, 'label'):
            # 重新设置label位置
            self.label.grid(row=0,column=0,sticky='nsew')

    # 获取默认大小
    def getDefaultSize(self):
        defaultSize = GlobalValue.TM_NODE_TYPE[self.getType()]['defaultSize']
        return defaultSize['width'], defaultSize['height']

    def refreshSize(self, width=None, height=None):
        # if width == None and height == None:
        #     return
        w, h = self.getContentSize()
        if width == None:
            width = self.initWindow.winfo_width()
        if height == None:
            height = h
        if width != w or height != h:
            self.setContentSize(width, height)

    def changeBg(self, bg=None):
        if not bg:
            bg = GlobalValue.BG_COLOR
        # self.configure(bg=bg)
        self.label.configure(bg=bg)

    def onLeftClick(self, event):
        py3_common.Logging.info('-----LineNode onLeftClick-----')
        if GlobalValue.UI_MODE == UiModeEnum.Edit:
            try:
                args = self.args
                args['mainView'].openViewNodeSetting(self.getExData('index'), args)
            except Exception as e:
                py3_common.Logging.error(e)

    def onRightClick(self, event):
        py3_common.Logging.info('-----LineNode onRightClick-----')
        if GlobalValue.UI_MODE == UiModeEnum.Normal:
            try:
                args = self.args
                args['mainView'].openViewNodeSetting(self.getExData('index'), args)
            except Exception as e:
                py3_common.Logging.error(e)
        elif GlobalValue.UI_MODE == UiModeEnum.Edit:
            args = self.args
            args['mainView'].selectEditItem(self.getExData('index'))

    def setExData(self, exData, update=True):
        super(LineNode, self).setExData(exData, update)
        args = self.args
        bgColor = self.labelBgColor
        fgColor = self.labelFgColor
        # py3_common.Logging.debug2(GlobalValue.UI_MODE == UiModeEnum.Edit, GlobalValue.FORCE_SHOW_SELECT, self.getExData('index'), GlobalValue.NOW_SELECT_INDEX, self.getExData('index') == GlobalValue.NOW_SELECT_INDEX, args['text'] if 'text' in args else '---')
        if (GlobalValue.UI_MODE == UiModeEnum.Edit or GlobalValue.FORCE_SHOW_SELECT) and self.getExData('index') == GlobalValue.NOW_SELECT_INDEX:
            bgColor = getColorWithTlKeyAutoDefault(['common', 'selectColor'])
            fgColor = getColorWithTlKeyAutoDefault(['line', 'selectFgColor'])
        self.label.configure(bg=bgColor, fg=fgColor)
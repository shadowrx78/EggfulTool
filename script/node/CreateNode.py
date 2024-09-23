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

# 新建节点
class CreateNode(tkVirtualListHelper.BaseNode):
    """docstring for CreateNode"""
    def __init__(self, initWindow, args=dict(), autoInit=True):
        super(CreateNode, self).__init__(initWindow, args, autoInit)

    def __del__(self):
        py3_common.Logging.info2('CreateNode __del__')

    def initUi(self):
        super(CreateNode, self).initUi()

        args = self.args
        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=1)

        fontName = '微软雅黑'
        fontSize = 48
        label = Label(self, text='+', font=(fontName, fontSize), anchor='center')
        label.grid(row=0,column=0,sticky='nsew')
        self.label = label

        self.label.bind('<Button-1>', self.onLeftClick)

        self.updateArgs(args)

    def updateArgs(self, args=dict()):
        super(CreateNode, self).updateArgs(args)

        dw, dh = self.getDefaultSize()
        width = args['width'] if 'width' in args else dw
        height = args['height'] if 'height' in args else dh
        self.setContentSize(width=width, height=height)

        self.label.grid()
        self.label.configure(fg=getColorWithTlKeyAutoDefault(['create', 'fgColor']), bg=getColorWithTlKeyAutoDefault(['create', 'bgColor']))

    def onConfigure(self, event):
        super(CreateNode, self).onConfigure(event)
        self.label.grid(row=0,column=0,sticky='nsew')

    # 获取默认大小
    def getDefaultSize(self):
        defaultSize = GlobalValue.TM_NODE_TYPE[self.getType()]['defaultSize']
        return defaultSize['width'], defaultSize['height']

    def onLeftClick(self, event):
        py3_common.Logging.info('-----CreateNode onLeftClick-----')
        try:
            args = self.args
            # script = getImportModule(getModuleNameWithTypeStr(args['typeStr']))
            # path_ = script.getPath(args)
            # if path_ and os.path.exists(path_):
            #     # dirPath = os.path.dirname(os.path.abspath(path_))
            #     result = py3_common.popen('explorer /select,"'+ os.path.abspath(path_) + '"')
            #     # py3_common.Logging.info(result)
            GlobalValue.INIT_WINDOW_GUI.openViewNodeSetting(self.getExData('index'))
        except Exception as e:
            py3_common.Logging.error(e)
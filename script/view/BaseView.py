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
import uuid

# import ccbparser
# import plistlib

from .. import py3_common, GlobalValue
from ..GlobalValue import *
# from ..EventProxy import *
from ..TkThemeHelper import *


# 弹窗基类
class BaseView(Toplevel):
    """docstring for BaseView"""
    def __init__(self, *args, **kwargs):
        self._markParentFocusWidget()
        if self.checkUniqueNeedClose():
            return
        super(BaseView, self).__init__(*args, **kwargs)
        py3_common.Logging.info2(self.getClassName(),'__init__')
        # 覆盖自带关闭按钮
        self.protocol("WM_DELETE_WINDOW", self.close)

        setWindowIcon(self)

        self.tkThemeHelper = TkThemeHelper()
        self.tkThemeHelper.addTkObj(self, isForceRaw=True)

        self.titleStr = None
        self.tlEventHandle = list()

        self.oldFocusWidget = None

        self.uid = str(uuid.uuid4())    #唯一标识符
        self._tmViewUid = dict()

        self.bind('<FocusIn>', self.onFocusIn)

        self.onShow()
        # self.after(1, lambda: self.onShow())

    def __del__(self):
        py3_common.Logging.info2(self.getClassName(),'__del__')

    def getClassName(self):
        return self.__class__.__name__

    # 是否需要锁定焦点，子类重载
    def isNeedGrab(self):
        return False

    # 是否唯一，子类重载
    def isUnique(self):
        return False

    def checkUniqueNeedClose(self):
        if not self.isUnique():
            return False
        return hasSameClassView(self)

    # 弹窗位置，返回None时不设置，子类重载
    def getAnchorPos(self):
        # return None
        return {'x':0.5, 'y':0.5}

    # 弹出窗口响应
    def onShow(self):
        self.after(1, lambda: self.focus_force())

        anchorPos = self.getAnchorPos()
        if anchorPos != None:
            try:
                self.after(1, lambda a=anchorPos: tkCenter(self, anchorPos=a))
                # tkCenter(self, anchorPos=anchorPos)
            except Exception as e:
                # raise e
                py3_common.Logging.warning(self.getClassName(),'设置弹窗位置失败')
                py3_common.Logging.warning(e)

        dispatchEvent(EventType.Event_ViewShow, self)
        if self.isNeedGrab():
            # # 锁定焦点
            # self.grab_set()
            dispatchEvent(EventType.Event_ViewNeedGrabShow, self)

    # 关闭窗口
    def close(self):
        self.removeAllEventListen()
        # 关闭
        self.tkThemeHelper.close()
        self.destroy()
        dispatchEvent(EventType.Event_ViewClose, self)
        if self.isNeedGrab():
            dispatchEvent(EventType.Event_ViewNeedGrabClose, self)

    # 响应焦点事件
    def onFocusIn(self, event):
        # py3_common.Logging.debug(self.getClassName(),'onFocusIn')
        dispatchEvent(EventType.Event_ViewFocusIn, self)

    # 标题加•表示有修改
    def setTitleWithModify(self, isModify):
        if self.titleStr == None:
            self.titleStr = str(self.title())
        self.title(self.titleStr + (' •' if isModify else ''))

    def _markParentFocusWidget(self):
        parent = GlobalValue.INIT_WINDOW_GUI
        if GlobalValue.VIEW_STACK != None and len(GlobalValue.VIEW_STACK) > 0:
            parent = GlobalValue.VIEW_STACK[-1]
        try:
            parent.markOldFocusWidget()
        except Exception as e:
            raise e

    def markOldFocusWidget(self):
        widget = None
        try:
            widget = self.focus_get()
        except Exception as e:
            raise e
        if widget != None:
            self.oldFocusWidget = widget

    def reFocusOldFocusWidget(self):
        if self.oldFocusWidget:
            self.oldFocusWidget.focus_set()
            # self.oldFocusWidget = None


    # -----------------------------事件相关-----------------------------
    # 添加事件监听
    def addEventListener(self, eventType, fCallback):
        self.tlEventHandle.append(addEventListener(eventType, fCallback))

    # 移除所有事件监听
    def removeAllEventListen(self):
        removeTlEventListener(self.tlEventHandle)
        self.tlEventHandle = list()


    # -----------------------------界面标识相关-----------------------------
    # 获取唯一标识
    def getUid(self):
        return self.uid

    # 记录子界面uid
    def markViewUid(self, view):
        self._tmViewUid[view.getClassName()] = view.getUid()

    # 根据uid判断界面是否为子界面
    def isViewUidInMark(self, view):
        return self.isViewUidInMarkWithClassName(view.getClassName(), view.getUid())

    def isViewUidInMarkWithClassName(self, className, uid):
        return className in self._tmViewUid and self._tmViewUid[className] == uid
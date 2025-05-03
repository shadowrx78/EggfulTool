#! python3
# -*- coding: utf-8 -*-

from . import py3_common
from . import GlobalValue
from .GlobalValue import *
import traceback
import inspect
import weakref


# tk风格组件
class TkThemeHelper(object):
    """
    tk风格组件
    """
    def __init__(self):
        super(TkThemeHelper, self).__init__()
        self.tlEventHandle = list()
        # 坑比PanedWindow 2钟类名获取方式大小写不一样
        self.tlRawTkObjName = ['Entry', 'Text', 'Label', 'Frame',
        'Radiobutton', 'Button', 'Canvas', 'Checkbutton', 'Scale', 'Listbox', 'Menu', 'Toplevel', 'PanedWindow']
        # 改成弱引用
        self.tlTkObj = weakref.WeakSet()
        self.tlTkExObj = weakref.WeakSet()
        self.debugLevel = 0
        self.initEventListen()

    def getClassName(self):
        return self.__class__.__name__

    # 初始化事件监听
    def initEventListen(self):
        self.removeAllEventListen()
        self.tlEventHandle.append(addEventListener(EventType.Event_SettingColorChange, self.onEvent_SettingColorChange))

    # 移除事件监听
    def removeAllEventListen(self):
        removeTlEventListener(self.tlEventHandle)
        self.tlEventHandle = list()

    def onEvent_SettingColorChange(self):
        self.update()

    # 添加tk对象
    def addTkObj(self, tkObj, isForceRaw=False):
        className = tkObj.__class__.__name__
        if self.debugLevel > 0:
            py3_common.Logging.debug('-----------addTkObj')
            py3_common.Logging.debug(className, tkObj)
            if self.debugLevel > 1:
                stack = inspect.stack()
                # 获取调用者的信息
                callerInfo = inspect.getframeinfo(stack[1][0])
                py3_common.Logging.info(callerInfo)
                del stack
        if className in self.tlRawTkObjName or isForceRaw:
            self.tlTkObj.add(tkObj)
        else:
            self.tlTkExObj.add(tkObj)

    # 移除tk对象
    def removeTkObj(self, tkObj):
        if self.debugLevel > 0:
            py3_common.Logging.debug('-----------removeTkObj')
            py3_common.Logging.debug(tkObj)
            if self.debugLevel > 1:
                stack = inspect.stack()
                # 获取调用者的信息
                callerInfo = inspect.getframeinfo(stack[1][0])
                py3_common.Logging.info(callerInfo)
                del stack
        try:
            self.tlTkObj.remove(tkObj)
        except Exception as e:
            # raise e
            pass
        try:
            self.tlTkExObj.remove(tkObj)
        except Exception as e:
            # raise e
            pass

    # 刷新
    def update(self):
        for tkObj in self.tlTkObj:
            try:
                configureTkObjectColor(tkObj)
            except Exception as e:
                # raise e
                py3_common.Logging.error(e, isShowMessageBox=False)
        for tkObj in self.tlTkExObj:
            try:
                configureExTkObjectColor(tkObj)
            except Exception as e:
                # raise e
                py3_common.Logging.error(e, isShowMessageBox=False)

    # 关闭
    def close(self):
        self.tlTkObj.clear()
        self.tlTkExObj.clear()
        self.removeAllEventListen()


    # -----------------------------测试-----------------------------
    def setDebugLevel(self, debugLevel):
        self.debugLevel = debugLevel
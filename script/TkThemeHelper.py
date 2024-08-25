#! python3
# -*- coding: utf-8 -*-

from . import py3_common
from . import GlobalValue
from .GlobalValue import *


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
        self.tlTkObj = set()
        self.tlTkExObj = set()
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
        if className in self.tlRawTkObjName or isForceRaw:
            self.tlTkObj.add(tkObj)
        else:
            self.tlTkExObj.add(tkObj)

    # 移除tk对象
    def removeTkObj(self, tkObj):
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
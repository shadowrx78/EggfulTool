#! python3
# -*- coding: utf-8 -*-

import uuid
from . import py3_common


# 事件类型枚举
class EventType:
    Event_SettingColorChange = 'Event_SettingColorChange'
    Event_SettingOptionsChange = 'Event_SettingOptionsChange'
    Event_SettingViewShowPosSettingConfirm = 'Event_SettingViewShowPosSettingConfirm'
    Event_SettingTlCommonStringChange = 'Event_SettingTlCommonStringChange'

    Event_ViewShow = 'Event_ViewShow'
    Event_ViewClose = 'Event_ViewClose'
    Event_ViewFocusIn = 'Event_ViewFocusIn'
    Event_ViewNeedGrabShow = 'Event_ViewNeedGrabShow'
    Event_ViewNeedGrabClose = 'Event_ViewNeedGrabClose'

    # 节点相关
    Event_NodeChange = 'Event_NodeChange'
    Event_NodeChangeByIndexKey = 'Event_NodeChangeByIndexKey'

    # 主界面相关
    Event_MainGuiTmNowDataBackupMark = 'Event_MainGuiTmNowDataBackupMark'
    Event_MainGuiTmNowDataBackupSave = 'Event_MainGuiTmNowDataBackupSave'
    Event_MainGuiTmNowDataBackupAbandon = 'Event_MainGuiTmNowDataBackupAbandon'
    Event_MainGuiSaveSingleNodeData = 'Event_MainGuiSaveSingleNodeData'
    Event_MainGuiSaveSingleNodeDataByIndexKey = 'Event_MainGuiSaveSingleNodeDataByIndexKey'
    Event_MainGuiMoveNode = 'Event_MainGuiMoveNode'
    Event_MainGuiMoveNodeByIndexKey = 'Event_MainGuiMoveNodeByIndexKey'
    Event_MainGuiNodeIndexChange = 'Event_MainGuiNodeIndexChange'

    # 撤销重做插件
    Event_UndoRedoHelperUndo = 'Event_UndoRedoHelperUndo'
    Event_UndoRedoHelperRedo = 'Event_UndoRedoHelperRedo'
    Event_UndoRedoHelperRecordOper = 'Event_UndoRedoHelperRecordOper'
    Event_UndoRedoHelperDataChange = 'Event_UndoRedoHelperDataChange'


# 事件代理
class EventProxy(object):
    """docstring for EventProxy"""
    def __init__(self, isDebug=False, isShowArgs=True):
        super(EventProxy, self).__init__()
        self.isDebug = isDebug
        self.isShowArgs = isShowArgs
        self.tmTmEventListener = dict()

    def getClassName(self):
        return self.__class__.__name__

    def setIsDebug(self, isDebug):
        self.isDebug = isDebug
        
    # 添加事件监听
    def addEventListener(self, eventType, fCallback):
        tmTmEventListener = self.tmTmEventListener
        if not eventType in tmTmEventListener:
            tmTmEventListener[eventType] = dict()
        tmEventListener = tmTmEventListener[eventType]

        key = str(eventType) + '_' + str(uuid.uuid4())
        while key in tmEventListener:
            key = str(eventType) + '_' + str(uuid.uuid4())
        tmEventListener[key] = fCallback

        handle = {'eventType':eventType, 'key':key}
        return handle


    # 移除事件监听
    def removeEventListener(self, handle):
        if handle == None or not isinstance(handle, dict) or not 'eventType' in handle or not 'key' in handle:
            return False
        tmTmEventListener = self.tmTmEventListener
        if not handle['eventType'] in tmTmEventListener:
            return False
        tmEventListener = tmTmEventListener[handle['eventType']]
        if not handle['key'] in tmEventListener:
            return False
        del tmEventListener[handle['key']]
        return True


    # 移除多个事件监听
    def removeTlEventListener(self, tlHandle):
        if tlHandle == None or not isinstance(tlHandle, list) or len(tlHandle) <= 0:
            return
        for i in range(0,len(tlHandle)):
            self.removeEventListener(tlHandle[i])


    # 派发事件
    def dispatchEvent(self, eventType, *args):
        if self.isDebug:
            py3_common.Logging.debug2(self.getClassName(),'dispatchEvent:', eventType, args if self.isShowArgs else '')
        tmTmEventListener = self.tmTmEventListener
        if not eventType in tmTmEventListener:
            return
        tmEventListener = tmTmEventListener[eventType]
        tlErrorHandle = list()
        for key in tmEventListener:
            try:
                tmEventListener[key](*args)
            except Exception as e:
                # raise e
                if self.isDebug:
                    py3_common.Logging.error(e)
                tlErrorHandle.append({'eventType':eventType, 'key':key})
        # 报错的清理掉
        self.removeTlEventListener(tlErrorHandle)
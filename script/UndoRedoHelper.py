#! python3
# -*- coding: utf-8 -*-

import uuid
from . import py3_common
from . import GlobalValue
from .GlobalValue import *
from .EventProxy import *

# 撤销重做组件
class UndoRedoHelper(object):
    """
    撤销重做组件
    参数:
    maxRecordLength:int 最大记录长度，默认-1表示不限制
    """
    def __init__(self, maxRecordLength=-1):
        super(UndoRedoHelper, self).__init__()
        self.tlOperRecord = list()  #记录操作日志
        self.maxRecordLength = maxRecordLength  #记录最大长度
        self.recordPointer = -1  #当前记录指针
        self.savePointer = -1   #上次保存指针
        self.uid = str(uuid.uuid4())    #唯一标识符

    def getClassName(self):
        return self.__class__.__name__

    # 操作枚举
    OperAdd = 'A'
    OperDelete = 'D'
    OperModify = 'M'

    """
    记录操作
    参数:
    oper:string 操作，对应操作枚举
    tlKey:list 修改的字段在数据内地址，空列表表示修改整个数据
    newValue:any 修改后的值
    oldValue:any 修改前的值
    """
    def recordOper(self, oper, tlKey, newValue=None, oldValue=None):
        recordData = dict()
        recordData['oper'] = oper
        recordData['tlKey'] = tlKey
        if newValue != None:
            recordData['newValue'] = py3_common.deep_copy_dict(newValue, isIgnoreType=True)
        if oldValue != None:
            recordData['oldValue'] = py3_common.deep_copy_dict(oldValue, isIgnoreType=True)

        # 指针不在末尾，删除指针后所有记录
        if len(self.tlOperRecord) > self.recordPointer+1:
            del self.tlOperRecord[self.recordPointer+1:]

        # 新记录放进队尾
        self.tlOperRecord.append(recordData)

        # 长度超过限制，从队头删除
        if self.maxRecordLength > 0 and len(self.tlOperRecord) > self.maxRecordLength:
            delNum = len(self.tlOperRecord) - self.maxRecordLength
            del self.tlOperRecord[0:delNum]

        # 设置指针到队尾
        self.recordPointer = len(self.tlOperRecord)-1
        if self.savePointer >= 0 and self.recordPointer <= self.savePointer:
            # 有保存指针&当前指针<=保存指针，表示做了无法恢复到上次保存的修改，重置保存指针
            self.savePointer = -1
        dispatchEvent(EventType.Event_UndoRedoHelperRecordOper, self.uid)
        dispatchEvent(EventType.Event_UndoRedoHelperDataChange, self.uid)
        py3_common.Logging.debug3('----------recordOper',recordData if GlobalValue.IS_EVENTPROXY_SHOW_ARGS else '', self.recordPointer)

    """
    撤销
    参数:
    nowData:dict|list 当前数据，函数会直接修改这个数据
    返回:
    suc:bool 操作是否成功
    """
    def undo(self, nowData):
        if self.recordPointer < 0 or len(self.tlOperRecord) == 0:
            return False
        try:
            recordData = py3_common.deep_copy_dict(self.tlOperRecord[self.recordPointer])
            py3_common.Logging.debug3('----------undo',recordData if GlobalValue.IS_EVENTPROXY_SHOW_ARGS else '', self.recordPointer)
            if recordData['oper'] == self.OperAdd:
                # 删除
                py3_common.setValueWithTlKey(nowData, recordData['tlKey'], None, isDel=True, isInsert=False)
            elif recordData['oper'] == self.OperDelete:
                # 添加
                py3_common.setValueWithTlKey(nowData, recordData['tlKey'], recordData['oldValue'], isDel=False, isInsert=True)
            elif recordData['oper'] == self.OperModify:
                # 改回旧值
                py3_common.setValueWithTlKey(nowData, recordData['tlKey'], recordData['oldValue'], isDel=False, isInsert=False)
            self.recordPointer -= 1
            dispatchEvent(EventType.Event_UndoRedoHelperUndo, self.uid)
            dispatchEvent(EventType.Event_UndoRedoHelperDataChange, self.uid)
            return True
        except Exception as e:
            # raise e
            py3_common.Logging.error(e, isShowMessageBox=False)
            return False

    """
    重做
    参数:
    nowData:dict|list 当前数据，函数会直接修改这个数据
    返回:
    suc:bool 操作是否成功
    """
    def redo(self, nowData):
        if self.recordPointer >= len(self.tlOperRecord)-1 or len(self.tlOperRecord) == 0:
            return False
        try:
            recordData = py3_common.deep_copy_dict(self.tlOperRecord[self.recordPointer+1])
            py3_common.Logging.debug3('----------redo',recordData if GlobalValue.IS_EVENTPROXY_SHOW_ARGS else '', self.recordPointer)
            if recordData['oper'] == self.OperAdd:
                # 添加
                py3_common.setValueWithTlKey(nowData, recordData['tlKey'], recordData['newValue'], isDel=False, isInsert=True)
            elif recordData['oper'] == self.OperDelete:
                # 删除
                py3_common.setValueWithTlKey(nowData, recordData['tlKey'], None, isDel=True, isInsert=False)
            elif recordData['oper'] == self.OperModify:
                # 改成新值
                py3_common.setValueWithTlKey(nowData, recordData['tlKey'], recordData['newValue'], isDel=False, isInsert=False)
            self.recordPointer += 1
            dispatchEvent(EventType.Event_UndoRedoHelperRedo, self.uid)
            dispatchEvent(EventType.Event_UndoRedoHelperDataChange, self.uid)
            return True
        except Exception as e:
            # raise e
            py3_common.Logging.error(e, isShowMessageBox=False)
            return False

    # 清除所有记录
    def clear(self):
        self.tlOperRecord = list()
        self.recordPointer = -1
        self.savePointer = -1

    # 设置数据
    def setValueWithTlKey(self, nowData, tlKey, value, isDel=False, isInsert=False):
        oldValue, suc = py3_common.getValueWithTlKey(nowData, tlKey)
        if len(tlKey) == 0 and suc:
            oldValue = py3_common.deep_copy_dict(oldValue, isOrdered=False)
        py3_common.setValueWithTlKey(nowData, tlKey, value, isDel=isDel, isInsert=isInsert)
        if isDel:
            self.recordOper(UndoRedoHelper.OperDelete, tlKey, oldValue=oldValue)
        else:
            if suc and not isInsert:
                self.recordOper(UndoRedoHelper.OperModify, tlKey, newValue=value, oldValue=oldValue)
            else:
                self.recordOper(UndoRedoHelper.OperAdd, tlKey, newValue=value)

    # 是否有改动
    def hasModify(self):
        if self.savePointer < 0:
            return len(self.tlOperRecord) > 0 and self.recordPointer >= 0
        else:
            return len(self.tlOperRecord) > 0 and self.recordPointer != self.savePointer

    # 标记保存操作
    def markSave(self):
        self.savePointer = self.recordPointer
        dispatchEvent(EventType.Event_UndoRedoHelperDataChange, self.uid)

    # 获取唯一标识
    def getUid(self):
        return self.uid
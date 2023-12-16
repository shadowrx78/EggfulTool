#! python3
# -*- coding: utf-8 -*-

from .. import py3_common

SCRIPT_NAME = 'BaseScript'
DEBUG = True
def setDebug(debug=False):
    global DEBUG
    DEBUG = debug

# 修改界面
def createEditUi(frame, tmExUi, data, cTkObjFun, dnd=None, tmExFun=None):
    if DEBUG:
        py3_common.Logging.debug('-----%s createEditUi-----' % SCRIPT_NAME)
    if data == None:
        data = dict()

# 保存数据
def saveData(tmExUi, data):
    if DEBUG:
        py3_common.Logging.debug('-----%s saveData-----' % SCRIPT_NAME)

# 额外的保留字段
def getTlAdvSaveKey():
    return []

# 按钮操作
def onBtnClick(data=None):
    if DEBUG:
        py3_common.Logging.debug('-----%s onBtnClick-----' % SCRIPT_NAME)
        py3_common.Logging.debug(data)

# 拖入操作
def onDrop(data=None, tlFile=None):
    if DEBUG:
        py3_common.Logging.debug('-----%s onDrop-----' % SCRIPT_NAME)
        py3_common.Logging.debug(tlFile)

def getPath(data=None):
    if DEBUG:
        py3_common.Logging.debug('-----%s getPath-----' % SCRIPT_NAME)
    return None
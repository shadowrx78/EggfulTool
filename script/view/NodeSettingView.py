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
from ..EventProxy import *

# 节点设置界面
class NodeSettingView(Toplevel):
    """docstring for NodeSettingView"""
    def __init__(self, initWindow, mainView, index, data=None):
        super(NodeSettingView, self).__init__(initWindow)
        self.initWindow = initWindow
        self.mainView = mainView
        self.index = index
        self.data = data
        self.tempData = py3_common.deep_copy_dict(data) if data else dict()
        self.tmExUi = dict()
        self.tmExFun = None
        self.initUi()

    def __del__(self):
        py3_common.Logging.info2('NodeSettingView __del__')

    def initUi(self):
        self.resizable(width=False, height=False)
        self.title("修改" if self.data else "新建")
        self.rowconfigure(1,weight=1)
        configureTkObjectColor(self)

        self.bind('<Escape>', lambda e:self.onBtnCancel())
        self.bind('<Alt-c>', lambda e:self.copyNodeConfig())
        self.bind('<Alt-v>', lambda e:self.pasteNodeConfig())
        self.bind('<Alt-s>', lambda e:self.testSaveExeIcon())

        self.dnd = TkDnD(self)

        # 上
        frameTop = Frame(self)
        frameTop.grid(row=0,column=0,sticky='nsew')
        self.frameTop = frameTop
        configureTkObjectColor(frameTop)
        # frameTop.grid(row=0,column=0)
        # frameTop.columnconfigure(0,weight=1)
        # frameTop.columnconfigure(1,weight=1)
        if True:
            # 选择类型
            typeCombobox = ttk.Combobox(frameTop, state='readonly')
            # typeCombobox['values'] = GlobalValue.TL_SETTING_KEY
            # typeCombobox.current(0)
            typeCombobox.bind("<<ComboboxSelected>>",lambda a:self.onTypeComboboxSelect())
            if platform == "linux" or platform == "linux2":
                typeCombobox.unbind_class("TCombobox", "<Button-4>")
                typeCombobox.unbind_class("TCombobox", "<Button-5>")
            else:
                typeCombobox.unbind_class("TCombobox", "<MouseWheel>")
            typeCombobox.grid(row=0,column=0,sticky='w')
            self.typeCombobox = typeCombobox
            configureTkObjectColor(typeCombobox)

            # 启用拖入选中框
            self.checkbuttonDropVar = IntVar()
            self.checkbuttonDropVar.set(0)
            checkbuttonDrop = Checkbutton(frameTop, text=str('启用拖入'), variable=self.checkbuttonDropVar, command=lambda v=self.checkbuttonDropVar:True)
            # checkbuttonDrop.grid(row=0, column=1, padx=10)
            checkbuttonDrop.grid(row=1, column=0, sticky='w')
            self.checkbuttonDrop = checkbuttonDrop
            configureTkObjectColor(checkbuttonDrop)

            # 上下箭头
            frameUpDownBtn = Frame(frameTop)
            frameUpDownBtn.grid(row=0, column=2, sticky='e')
            configureTkObjectColor(frameUpDownBtn)
            buttonUp = Button(frameUpDownBtn, text='▲', width=4, command=lambda a=-1:self.onBtnUpDownClick(a))
            buttonUp.grid(row=0, column=0)
            buttonDown = Button(frameUpDownBtn, text='▼', width=4, command=lambda a=1:self.onBtnUpDownClick(a))
            buttonDown.grid(row=0, column=1)
            self.buttonUp = buttonUp
            self.buttonDown = buttonDown
            configureTkObjectColor(buttonUp)
            configureTkObjectColor(buttonDown)

            # 大小
            frameWH = Frame(frameTop)
            # frameWH.grid(row=1,column=0,sticky='ew')
            frameWH.grid(row=0,column=1,sticky='w',columnspan=1)
            configureTkObjectColor(frameWH)
            labelW = Label(frameWH, text='W', anchor='w')
            labelW.grid(row=0,column=0)
            configureTkObjectColor(labelW)
            entryW = Entry(frameWH, width=4)
            py3_common.bindTkEditorRightClick(entryW, self)
            entryW.grid(row=0,column=1)
            configureTkObjectColor(entryW)
            labelH = Label(frameWH, text='H', anchor='w')
            labelH.grid(row=0,column=2)
            configureTkObjectColor(labelH)
            entryH = Entry(frameWH, width=4)
            py3_common.bindTkEditorRightClick(entryH, self)
            entryH.grid(row=0,column=3)
            configureTkObjectColor(entryH)
            self.entryW = entryW
            self.entryH = entryH

            # 打开所在位置按钮
            buttonOpenDir = Button(frameTop, text='打开所在位置', command=self.onBtnOpenDirClick)
            buttonOpenDir.grid(row=1,column=1,sticky='w')
            self.buttonOpenDir = buttonOpenDir
            configureTkObjectColor(buttonOpenDir)

            # 删除节点按钮
            buttonDel = Button(frameTop, text='删除节点', command=self.onBtnDel)
            buttonDel.grid(row=1,column=2,sticky='e')
            self.buttonDel = buttonDel
            configureTkObjectColor(buttonDel)

            # 标记选中框
            self.checkbuttonBookmarkVar = IntVar()
            self.checkbuttonBookmarkVar.set(0)
            checkbuttonBookmark = Checkbutton(frameTop, text=str('标记'), variable=self.checkbuttonBookmarkVar, command=lambda v=self.checkbuttonBookmarkVar:True)
            checkbuttonBookmark.grid(row=2, column=0, sticky='w')
            self.checkbuttonBookmark = checkbuttonBookmark
            configureTkObjectColor(checkbuttonBookmark)

            # 执行前询问选择框
            frameAskExe = Frame(frameTop)
            frameAskExe.grid(row=2, column=1, sticky='w')
            configureTkObjectColor(frameAskExe)
            self.checkbuttonAskExeVar = IntVar()
            self.checkbuttonAskExeVar.set(0)
            checkbuttonAskExe = Checkbutton(frameAskExe, text=str('执行前询问'), variable=self.checkbuttonAskExeVar, command=lambda v=self.checkbuttonAskExeVar:True)
            checkbuttonAskExe.grid(row=0, column=0, sticky='w')
            self.checkbuttonAskExe = checkbuttonAskExe
            configureTkObjectColor(checkbuttonAskExe)
            # 执行前询问说明按钮
            btnTipsAskExe = Button(frameAskExe, text='!', width=3, command=self.onBtnTipsAskExeClick)
            btnTipsAskExe.grid(row=0,column=1)
            configureTkObjectColor(btnTipsAskExe)

            # 禁用选中框
            self.checkbuttonDisableVar = IntVar()
            self.checkbuttonDisableVar.set(0)
            checkbuttonDisable = Checkbutton(frameTop, text=str('禁用'), variable=self.checkbuttonDisableVar, command=lambda v=self.checkbuttonDisableVar:True)
            checkbuttonDisable.grid(row=2, column=2, sticky='e')
            self.checkbuttonDisable = checkbuttonDisable
            configureTkObjectColor(checkbuttonDisable)

            # 标题
            frameTitle = Frame(frameTop)
            frameTitle.grid(row=3,column=0,columnspan=3,rowspan=1)
            configureTkObjectColor(frameTitle)
            frameTitle.rowconfigure(1,weight=1)
            frameTitle.columnconfigure(0,weight=1)
            labelTitle = Label(frameTitle, text='标题：', anchor='w')
            labelTitle.grid(row=0,column=0,sticky='ew')
            configureTkObjectColor(labelTitle)
            textTitle = Text(frameTitle, height=4)
            py3_common.bindTkEditorRightClick(textTitle, self)
            textTitle.grid(row=1,column=0,sticky='nsew')
            self.textTitle = textTitle
            configureTkObjectColor(textTitle)

            textTitleVsb = ttk.Scrollbar(frameTitle,orient="vertical",command=textTitle.yview)
            textTitle.configure(yscrollcommand=textTitleVsb.set)
            textTitleVsb.grid(column=1, row=1, sticky='ns')

        # # 中
        # frameMiddle = Frame(frameRoot)
        # frameMiddle.grid(row=1,column=0,sticky='nsew')
        # # frameMiddle.grid(row=1,column=0)
        # self.frameMiddle = frameMiddle
        # # 为了自动变大小
        # frameTemp = Frame(frameMiddle)
        # frameTemp.grid(row=0,column=0,sticky='nsew')
        self.frameMiddle = None

        # 留间距
        frameTemp = Frame(self)
        frameTemp.grid(row=2,column=0,sticky='nsew')
        configureTkObjectColor(frameTemp)
        labelTemp = Label(frameTemp, text=' ')
        labelTemp.grid(row=0,column=0,sticky='nsew')
        configureTkObjectColor(labelTemp)

        # 下
        frameBottom = Frame(self)
        frameBottom.grid(row=3,column=0,sticky='nsew')
        self.frameBottom = frameBottom
        configureTkObjectColor(frameBottom)
        frameBottom.columnconfigure(0,weight=1)
        frameBottom.columnconfigure(1,weight=1)
        if True:
            buttonConfirm = Button(frameBottom, text='确定', width=10, command=self.onBtnConfirm)
            buttonConfirm.grid(row=0, column=0)
            configureTkObjectColor(buttonConfirm)
            buttonCancel = Button(frameBottom, text='取消', width=10, command=self.onBtnCancel)
            buttonCancel.grid(row=0, column=1)
            configureTkObjectColor(buttonCancel)


        # 刷新
        self.updateFrameTop(True)
        self.updateFrameMiddle()


    def setIndex(self, index):
        self.index = index

    def getIndex(self):
        return self.index


    # 刷新上组件
    def updateFrameTop(self, refreshType=False, refreshTitle=False):
        tempData = self.tempData
        key = None

        # 选择类型
        if refreshType:
            typeCombobox = self.typeCombobox
            typeCombobox['values'] = GlobalValue.TL_SETTING_KEY
            success = False
            key = getSettingKey(tempData)
            if key and key in GlobalValue.TL_SETTING_KEY:
                for i in range(0,len(GlobalValue.TL_SETTING_KEY)):
                    if key == GlobalValue.TL_SETTING_KEY[i]:
                        typeCombobox.current(i)
                        success = True
                        break
            if not success:
                typeCombobox.current(0)
                key = GlobalValue.TL_SETTING_KEY[0]
                self.setDataTypeKey(key, tempData)
        else:
            key = getSettingKey(tempData)

        # 启用拖入选中框
        checkbuttonDrop = self.checkbuttonDrop
        py3_common.setCheckbuttonEnable(checkbuttonDrop, key != 'line')
        self.checkbuttonDropVar.set(1 if 'useDrop' in tempData and tempData['useDrop'] else 0)

        # 上下箭头
        buttonUp = self.buttonUp
        buttonDown = self.buttonDown
        py3_common.setBtnEnable(buttonUp, self.data != None)
        py3_common.setBtnEnable(buttonDown, self.data != None)

        # 大小
        entryW = self.entryW
        entryH = self.entryH
        py3_common.setEditorEnable(entryW, key != 'line')
        # py3_common.setEditorEnable(entryH, key != 'line')
        dw, dh = self.getDefaultSize(key)
        py3_common.setEntryText(entryW, str(tempData['width']) if 'width' in tempData else str(dw))
        py3_common.setEntryText(entryH, str(tempData['height']) if 'height' in tempData else str(dh))

        # 打开所在位置按钮
        buttonOpenDir = self.buttonOpenDir
        py3_common.setBtnEnable(buttonOpenDir, key != 'line')

        # 删除节点按钮
        buttonDel = self.buttonDel
        py3_common.setBtnEnable(buttonDel, self.data != None)

        # 标记选中框
        py3_common.setCheckbuttonEnable(self.checkbuttonBookmark, key != 'line')
        self.checkbuttonBookmarkVar.set(1 if 'bookmark' in tempData and tempData['bookmark'] else 0)

        # 执行前询问选择框
        py3_common.setCheckbuttonEnable(self.checkbuttonAskExe, key != 'line')
        self.checkbuttonAskExe.configure(text=(str('执行前询问') if not getOptionAskBeforeExecuting(key) else str('执行前不询问')))
        self.checkbuttonAskExeVar.set(1 if 'askExeMark' in tempData and tempData['askExeMark'] else 0)

        # 禁用选中框
        py3_common.setCheckbuttonEnable(self.checkbuttonDisable, key != 'line')
        self.checkbuttonDisableVar.set(1 if 'disable' in tempData and tempData['disable'] else 0)

        # 标题
        textTitle = self.textTitle
        if re.search(r'^\s*$', py3_common.getTextText(textTitle)) or refreshTitle:
            if key == 'line':
                py3_common.setTextText(textTitle, tempData['text'] if 'text' in tempData else '')
            else:
                py3_common.setTextText(textTitle, tempData['btnText'] if 'btnText' in tempData else '')

    # 刷新中组件
    def updateFrameMiddle(self):
        tempData = self.tempData
        # frameMiddle = self.frameMiddle
        try:
            # 清空记录
            for k in self.tmExUi.keys():
                ui = self.tmExUi[k]
                ui.grid_remove()
                ui.destroy()
                # del self.tmExUi[k]
            self.tmExUi = dict()

            # 中 删除
            if self.frameMiddle:
                self.frameMiddle.destroy()
                del self.frameMiddle

            # 中 创建
            frameMiddle = Frame(self)
            frameMiddle.grid(row=1,column=0,sticky='nsew')
            self.frameMiddle = frameMiddle
            configureTkObjectColor(frameMiddle)

            if not self.tmExFun:
                tmExFun = dict()
                tmExFun['createColorLabelBtn'] = self.createColorLabelBtn
                self.tmExFun = tmExFun

            key = getSettingKey(tempData)
            script = getImportModule(getModuleNameWithTypeStr(key))
            script.createEditUi(frameMiddle, self.tmExUi, tempData, configureTkObjectColor, self.dnd, self.tmExFun)
        except Exception as e:
            py3_common.Logging.error(e)

    # 类型选择
    def onTypeComboboxSelect(self):
        tempData = self.tempData
        key = self.typeCombobox.get()
        self.setDataTypeKey(key, tempData)

        # 刷新
        self.updateFrameTop()
        self.updateFrameMiddle()

    # 上下移动
    def onBtnUpDownClick(self, value):
        index_ = self.mainView.moveItem(self.index, value)
        if index_ != None:
            self.index = index_

    # 打开所在位置
    def onBtnOpenDirClick(self):
        tempData = self.tempData
        try:
            key = getSettingKey(tempData)
            script = getImportModule(getModuleNameWithTypeStr(key))
            path_ = script.getPath(tempData, self.tmExUi)
            if path_ and os.path.exists(path_):
                # dirPath = os.path.dirname(os.path.abspath(path_))
                py3_common.Logging.debug(os.path.abspath(path_))
                result = py3_common.popen('explorer /select,"'+ os.path.abspath(path_) + '"')
                # py3_common.Logging.info(result)
        except Exception as e:
            py3_common.Logging.error(e)

    # 删除节点
    def onBtnDel(self):
        value = messagebox.askokcancel('确认', '被删除节点信息将保存在 "%s"，\n是否删除该节点？' % os.path.realpath(GlobalValue.DELETED_NODES_BACKUP_JSON_PATH))
        if not value:
            return
        tempData = self.tempData
        self.mainView.saveNodeData(self.index, tempData, SaveNodeDataOper.Delete)
        self.destroy()

    def onBtnCancel(self):
        # 关闭
        self.destroy()

    def onBtnConfirm(self):
        result = self.saveTempData()
        if result:
            tempData = self.tempData

            # 关闭
            self.destroy()

    # 筛选保留字段
    def screenKey(self, data):
        try:
            key = getSettingKey(data)
            tlSaveKey = set()

            for k in GlobalValue.TMTL_BASE_KEY[data['nodeType']]:
                tlSaveKey.add(k)

            script = getImportModule(getModuleNameWithTypeStr(key))
            tlAdvSaveKey = script.getTlAdvSaveKey()
            for k in tlAdvSaveKey:
                tlSaveKey.add(k)

            tlDelKey = list()
            for k in data:
                if not k in tlSaveKey:
                    tlDelKey.append(k)
            for k in tlDelKey:
                del data[k]
        except Exception as e:
            py3_common.Logging.error(e)

    # 设置类型进data
    def setDataTypeKey(self, key, data):
        if key == 'line':
            data['nodeType'] = 'Line'
        else:
            data['nodeType'] = 'Btn'
            data['typeStr'] = key

    # 保存数据
    def saveTempData(self):
        tempData = self.getSaveTempData()
        if not tempData:
            return False

        if self.data == None:
            # 插入
            self.mainView.saveNodeData(self.index, tempData, SaveNodeDataOper.Insert)
        else:
            # 修改
            self.mainView.saveNodeData(self.index, tempData, SaveNodeDataOper.Edit)

        return True

    def getSaveTempData(self):
        tempData = self.tempData
        key = getSettingKey(tempData)

        # 启用拖入选中框
        # tempData['useDrop'] = self.checkbuttonDropVar.get() > 0
        # if not tempData['useDrop']:
        #     del tempData['useDrop']
        py3_common.setKVInDataWithExcludeDefault(tempData, 'useDrop', self.checkbuttonDropVar.get() > 0, False)
        # 标记选中框
        # tempData['bookmark'] = self.checkbuttonBookmarkVar.get() > 0
        # if not tempData['bookmark']:
        #     del tempData['bookmark']
        py3_common.setKVInDataWithExcludeDefault(tempData, 'bookmark', self.checkbuttonBookmarkVar.get() > 0, False)
        # 执行前询问选择框
        py3_common.setKVInDataWithExcludeDefault(tempData, 'askExeMark', self.checkbuttonAskExeVar.get() > 0, False)
        # 禁用选中框
        py3_common.setKVInDataWithExcludeDefault(tempData, 'disable', self.checkbuttonDisableVar.get() > 0, False)

        # 大小
        dw, dh = self.getDefaultSize(key)
        w, h = py3_common.getEntryText(self.entryW), py3_common.getEntryText(self.entryH)
        # if not w or abs(int(w)) == dw:
        #     if 'width' in tempData:
        #         del tempData['width']
        # else:
        #     tempData['width'] = abs(int(w))
        # if not h or abs(int(h)) == dh:
        #     if 'height' in tempData:
        #         del tempData['height']
        # else:
        #     tempData['height'] = abs(int(h))
        if not w:
            w = dw
        if not h:
            h = dh
        py3_common.setKVInDataWithExcludeDefault(tempData, 'width', abs(int(w)), dw)
        py3_common.setKVInDataWithExcludeDefault(tempData, 'height', abs(int(h)), dh)

        # 标题
        title = py3_common.getTextText(self.textTitle)
        if key == 'line':
            tempData['text'] = title
        else:
            tempData['btnText'] = title

        try:
            script = getImportModule(getModuleNameWithTypeStr(key))
            if not script.saveData(self.tmExUi, tempData):
                return False
        except Exception as e:
            py3_common.Logging.error(e)

        self.screenKey(tempData)
        # print(tempData)
        return tempData


    # 获取默认大小
    def getDefaultSize(self, key):
        defaultSize = GlobalValue.TM_NODE_TYPE['Line' if key == 'line' else 'Btn']['defaultSize']
        return defaultSize['width'], defaultSize['height']

    def copyNodeConfig(self):
        tempData = self.getSaveTempData()
        if not tempData:
            return False
        copyStr = json.dumps(tempData, ensure_ascii=False, indent=None, sort_keys=False)
        py3_common.Logging.debug('-----copy nodeData-----')
        py3_common.Logging.debug(copyStr)
        self.clipboard_clear()
        self.clipboard_append(copyStr)
        return True

    def pasteNodeConfig(self):
        try:
            self.tempData = json.loads(self.clipboard_get(), object_pairs_hook=OrderedDict)
        except json.JSONDecodeError:
            # raise e
            py3_common.Logging.error(e)
            return False
        # 刷新
        self.updateFrameTop(refreshType=True, refreshTitle=True)
        self.updateFrameMiddle()

    # 保存部分设置
    def changeAndSaveTlProperty(self, tmData, refresh=True, isDelete=False):
        tempData = self.tempData
        for k in tmData:
            if isDelete:
                if k in tempData:
                    del tempData[k]
            else:
                tempData[k] = tmData[k]
        result = self.saveTempData()
        if result and refresh:
            dispatchEvent(EventType.Event_NodeChange, self.index)

    # 创建修改颜色按钮
    # dataKey:颜色在节点data里面的key
    # tlKey:默认颜色的tlKey
    def createColorLabelBtn(self, frame, text, dataKey, tlKey, width=10):
        labelBtn = Label(frame, text=text, width=width, relief='groove', borderwidth=2)
        self.updateLabelBtnColor(labelBtn, dataKey, tlKey)
        labelBtn.bind('<Button-1>', lambda e,labelBtn=labelBtn,tlKey=tlKey, dataKey=dataKey:self.openAskColor(labelBtn, dataKey, tlKey))

        # 还原默认
        colorTemp = getColorWithTlKey(tlKey, True)
        tmData = dict()
        tmData[dataKey] = colorTemp
        labelBtn.bind('<Button-3>', lambda e,labelBtn=labelBtn,tlKey=tlKey, dataKey=dataKey:self.setWithDefaultColor(labelBtn, dataKey, tlKey))
        # self.tlColorBtn.append([labelBtn, tlKey])
        return labelBtn

    # 更新按钮字体颜色
    # dataKey:颜色在节点data里面的key
    # tlKey:默认颜色的tlKey
    def updateLabelBtnColor(self, labelBtn, dataKey, tlKey):
        tempData = self.tempData
        colorTemp = tempData[dataKey] if dataKey in tempData else None
        if not colorTemp:
            colorTemp = getColorWithTlKeyAutoDefault(tlKey)
            # if not colorTemp:
            #     colorTemp = getColorWithTlKey(tlKey, True)
        if colorTemp:
            r,g,b = self.winfo_rgb(colorTemp)
            rw,gw,bw = self.winfo_rgb('white')
            rhm,ghm,bhm = 0.4,0.8,0.4   #绿色看起来最亮，亮度权重高点
            isLight = (r*rhm+g*ghm+b*bhm) > (rw*rhm+gw*ghm+bw*bhm)/3
            # py3_common.Logging.debug(colorTemp,r,g,b,rw,gw,bw,isLight)
            labelBtn.configure(bg=colorTemp, fg='black' if isLight else 'white')

    # 打开颜色设置界面
    def openAskColor(self, labelBtn, dataKey, tlKey):
        tempData = self.tempData
        colorTemp = tempData[dataKey] if dataKey in tempData else getColorWithTlKeyAutoDefault(tlKey)
        color = None
        if colorTemp:
            color_ = askcolor(title="颜色", color=colorTemp)
            if color_:
                py3_common.Logging.debug(color_)
                color = color_[1]
        else:
            color_ = askcolor(title="颜色")
            if color_:
                color = color_[1]
        # if not color:
        #     color = colorTemp if colorTemp else getColorWithTlKey(tlKey, True)
        if color:
            tmData = dict()
            tmData[dataKey] = color
            # self.saveColor(labelBtn, tlKey, color)
            self.changeAndSaveTlProperty(tmData)
            self.updateLabelBtnColor(labelBtn, dataKey, tlKey)

    def setWithDefaultColor(self, labelBtn, dataKey, tlKey):
        # colorTemp = getColorWithTlKey(tlKey, True)
        tmData = dict()
        tmData[dataKey] = None
        self.changeAndSaveTlProperty(tmData, isDelete=True)
        self.updateLabelBtnColor(labelBtn, dataKey, tlKey)

    def onBtnTipsAskExeClick(self):
        tipsStr = u'该项涵义根据 "全局 执行前询问" 选项状态变化'
        messagebox.showinfo('帮助', tipsStr, parent=self)

    def testSaveExeIcon(self):
        # tempData = self.tempData
        # key = getSettingKey(tempData)
        # if key == 'exe':
        #     try:
        #         script = getImportModule(getModuleNameWithTypeStr(key))
        #         path_ = script.getPath(tempData, self.tmExUi)
        #         saveExeIcon(path_, './test/testIcon.bmp')
        #     except Exception as e:
        #         py3_common.Logging.error(e)
        pass
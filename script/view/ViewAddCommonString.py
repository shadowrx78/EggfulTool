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

from .. import py3_common, GlobalValue
from ..GlobalValue import *
from ..EventProxy import *
from ..UndoRedoHelper import *
from .BaseView import *
from lib.tksheet import *
from .ViewText import ViewText, ViewTextTypeEnum
from .ViewLineCopyString import *


# 添加常用文本界面
class ViewAddCommonString(BaseView):
    """
    添加常用文本界面
    参数:
    initWindow:tkObj 父容器
    """
    def __init__(self, initWindow):
        if self.checkUniqueNeedClose():
            return
        super(ViewAddCommonString, self).__init__(initWindow)
        self.initWindow = initWindow
        self.tlData = GlobalValue.TL_COMMON_STRING
        self.tlNowData = py3_common.deep_copy_dict(self.tlData)  #复制一份做当前数据缓存，所有修改都改这份

        self.tlKey = []
        self.undoRedoHelper = UndoRedoHelper()

        self.autoUpdateView = True
        self.initUi()

    # 是否需要锁定焦点，子类重载
    def isNeedGrab(self):
        return True

    # 是否唯一，子类重载
    def isUnique(self):
        return True

    def initUi(self):
        self.title('添加常用文本')
        self.resizable(width=False, height=False)
        self.minsize(200, 100)
        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)

        self.protocol("WM_DELETE_WINDOW", self.onBtnCancel)
        self.bind('<Control-z>', self.onKeyboardCtrlZClick)
        self.bind('<Control-y>', self.onKeyboardCtrlYClick)
        self.bind('<plus>', lambda e:self.onBtnAddClick())
        self.bind('<Control-plus>', lambda e:True)  #plus跟表格的ctrl+plus冲突，消除一下
        # self.bind('<Up>', lambda e,arrow=ArrowDirEnum.Up:self.onKeyboardArrowClick(arrow))
        # self.bind('<Left>', lambda e,arrow=ArrowDirEnum.Left:self.onKeyboardArrowClick(arrow))
        # self.bind('<Down>', lambda e,arrow=ArrowDirEnum.Down:self.onKeyboardArrowClick(arrow))
        # self.bind('<Right>', lambda e,arrow=ArrowDirEnum.Right:self.onKeyboardArrowClick(arrow))
        # self.bind('<Home>', lambda e,arrow=ArrowDirEnum.Home:self.onKeyboardArrowClick(arrow))
        # self.bind('<End>', lambda e,arrow=ArrowDirEnum.End:self.onKeyboardArrowClick(arrow))
        # self.bind('<Prior>', lambda e,arrow=ArrowDirEnum.PageUp:self.onKeyboardArrowClick(arrow))
        # self.bind('<Next>', lambda e,arrow=ArrowDirEnum.PageDown:self.onKeyboardArrowClick(arrow))
        self.bind('<Escape>', lambda e:self.onKeyboardEscapeClick())
        self.bind('<Control-Return>', lambda e:self.onBtnConfirm())
        self.bind('<Control-s>', lambda e, icv=False:self.onBtnConfirm(isCloseView=icv))
        self.bind('<Control-f>', lambda e:self.onBtnSearchClick())

        self.initEventListen()

        frameTop = Frame(self)
        frameTop.columnconfigure(0,weight=1)
        frameTop.grid(row=0,column=0,sticky='nsew')
        self.tkThemeHelper.addTkObj(frameTop)

        # 表格
        if True:
            sheet = Sheet(frameTop)
            sheet.grid(row=0, column=0, sticky='nsew')
            self.tkThemeHelper.addTkObj(sheet)
            sheet.enable_bindings(
                'single_select',
                'column_drag_and_drop',# /'move_columns',
                'arrowkeys',# all arrowkeys including page up and down
                'column_width_resize',
                'double_click_column_resize',
                'row_width_resize',
                'row_height_resize',
                'double_click_row_resize',
                )
            sheet.bind('<Double-Button-1>', self.onSheetDoubleButton1Click)
            sheet.bind('<Return>', self.onSheetKeyBoardReturnClick)
            sheet.bind('<Delete>', self.onSheetKeyBoardDeleteClick)
            sheet.bind('<Control-c>', self.onSheetCtrlCClick)
            sheet.bind('<Control-Shift-Up>', lambda e:self.onBtnUpClick())
            sheet.bind('<Control-Shift-Down>', lambda e:self.onBtnDownClick())
            sheet.bind('<Control-Shift-D>', lambda e:self.onBtnCopyOneClick())
            sheet.bind('<Control-Return>', lambda e:True)
            # sheet.bind('<Home>', lambda e:True)
            # sheet.bind('<End>', lambda e:True)
            # sheet.bind('<Prior>', lambda e:True)    #PageUp
            # sheet.bind('<Next>', lambda e:True)     #PageDown
            self.sheet = sheet
            bindTkSheetKeyboardArrowEvent(self, self.sheet)
            self.bindSheetRightClick()

        # 按钮
        if True:
            frameBtn = Frame(frameTop)
            frameBtn.grid(row=0, column=1, sticky='ns')
            self.tkThemeHelper.addTkObj(frameBtn)
            frameBtnR = 0
            frameBtnPady = 4
            frameTempWH = (120,30)

            frmTemp = Frame(frameBtn, height=frameTempWH[1], width=frameTempWH[0])
            frmTemp.grid(row=frameBtnR, column=0)
            self.tkThemeHelper.addTkObj(frmTemp)
            frameBtnR += 1

            btnAdd = Button(frameBtn, text='+', width=10, height=1, command=self.onBtnAddClick, takefocus=0)
            btnAdd.grid(row=frameBtnR, column=0, pady=frameBtnPady)
            self.tkThemeHelper.addTkObj(btnAdd)
            frameBtnR += 1

            btnDel = Button(frameBtn, text='-', width=10, height=1, command=self.onBtnDelClick, takefocus=0)
            btnDel.grid(row=frameBtnR, column=0, pady=frameBtnPady)
            self.tkThemeHelper.addTkObj(btnDel)
            frameBtnR += 1

            frmTemp = Frame(frameBtn, height=frameTempWH[1], width=frameTempWH[0])
            frmTemp.grid(row=frameBtnR, column=0)
            self.tkThemeHelper.addTkObj(frmTemp)
            frameBtnR += 1

            btnUp = Button(frameBtn, text='▲\nCtrl+Shift+↑', width=10, height=2, command=self.onBtnUpClick, takefocus=0)
            btnUp.grid(row=frameBtnR, column=0, pady=frameBtnPady)
            self.tkThemeHelper.addTkObj(btnUp)
            frameBtnR += 1

            btnDown = Button(frameBtn, text='▼\nCtrl+Shift+↓', width=10, height=2, command=self.onBtnDownClick, takefocus=0)
            btnDown.grid(row=frameBtnR, column=0, pady=frameBtnPady)
            self.tkThemeHelper.addTkObj(btnDown)
            frameBtnR += 1

            frmTemp = Frame(frameBtn, height=frameTempWH[1], width=frameTempWH[0])
            frmTemp.grid(row=frameBtnR, column=0)
            self.tkThemeHelper.addTkObj(frmTemp)
            frameBtnR += 1

            btnCopyOne = Button(frameBtn, text='复制一份\nCtrl+Shift+D', width=10, height=2, command=self.onBtnCopyOneClick, takefocus=0)
            btnCopyOne.grid(row=frameBtnR, column=0, pady=frameBtnPady)
            self.tkThemeHelper.addTkObj(btnCopyOne)
            frameBtnR += 1

            btnEdit = Button(frameBtn, text='编辑', width=10, height=1, command=self.onBtnEditClick, takefocus=0)
            btnEdit.grid(row=frameBtnR, column=0, pady=frameBtnPady)
            self.tkThemeHelper.addTkObj(btnEdit)
            frameBtnR += 1

            frmTemp = Frame(frameBtn, height=frameTempWH[1], width=frameTempWH[0])
            frmTemp.grid(row=frameBtnR, column=0)
            self.tkThemeHelper.addTkObj(frmTemp)
            frameBtnR += 1

            btnCopyOne = Button(frameBtn, text='搜索\nCtrl+F', width=10, height=2, command=self.onBtnSearchClick, takefocus=0)
            btnCopyOne.grid(row=frameBtnR, column=0, pady=frameBtnPady)
            self.tkThemeHelper.addTkObj(btnCopyOne)
            frameBtnR += 1

            frmTemp = Frame(frameBtn, height=frameTempWH[1], width=frameTempWH[0])
            frmTemp.grid(row=frameBtnR, column=0)
            self.tkThemeHelper.addTkObj(frmTemp)
            frameBtnR += 1

        frameBottom = Frame(self)
        frameBottom.rowconfigure(1,weight=1)
        frameBottom.columnconfigure(0,weight=1)
        frameBottom.columnconfigure(1,weight=1)
        frameBottom.grid(row=1,column=0,sticky='nsew')
        self.tkThemeHelper.addTkObj(frameBottom)

        # 提示
        labelTips = Label(frameBottom, text='撤销：Ctrl+Z | 重做：Ctrl+Y | 保存：Ctrl+S', anchor='w')
        labelTips.grid(row=0,column=0,sticky='nsew',columnspan=2,rowspan=1)
        self.tkThemeHelper.addTkObj(labelTips)

        # 确定取消按钮
        if True:
            buttonConfirm = Button(frameBottom, text='确定修改', width=10, command=self.onBtnConfirm, takefocus=0)
            buttonConfirm.grid(row=1, column=0)
            self.tkThemeHelper.addTkObj(buttonConfirm)
            buttonCancel = Button(frameBottom, text='取消', width=10, command=self.onBtnCancel, takefocus=0)
            buttonCancel.grid(row=1, column=1)
            self.tkThemeHelper.addTkObj(buttonCancel)

        self.tkThemeHelper.update()
        if self.autoUpdateView:
            self.updateView()


    def initEventListen(self):
        self.removeAllEventListen()
        self.addEventListener(EventType.Event_UndoRedoHelperDataChange, self.onEvent_UndoRedoHelperDataChange)


    # 刷新界面
    def updateView(self):
        tlNowData = self.tlNowData
        tlTitle = ['值']     #列标题
        tlRowIndex = list()     #行标题
        tlTlData = list()       #表格每行数据
        if len(tlNowData) > 0:
            for i in range(0,len(tlNowData)):
                tlTlData.append([tlNowData[i]])
                tlRowIndex.append(str(i+1))
        py3_common.setDataToTkSheet(self.sheet, tlTitle=tlTitle, tlRowIndex=tlRowIndex, tlTlData=tlTlData)

        self.tlTlData = tlTlData

        self.sheet.fix_select_row_col()
        if len(tlTlData) > 0:
            self.sheet.set_col_width(0)




    # -----------------------------tk事件-----------------------------
    # 表格双击
    def onSheetDoubleButton1Click(self, event):
        sheet = self.sheet
        if sheet.identify_row(event) == None or sheet.identify_column(event) == None:
            return
        py3_common.Logging.debug(self.getClassName(),'onSheetDoubleButton1Click')
        self.onBtnEditClick()

    # 表格回车
    def onSheetKeyBoardReturnClick(self, event):
        sheet = self.sheet
        if sheet.identify_row(event) == None or sheet.identify_column(event) == None:
            return
        py3_common.Logging.debug(self.getClassName(),'onSheetKeyBoardReturnClick')
        self.onBtnEditClick()

    # 列表删除
    def onSheetKeyBoardDeleteClick(self, event):
        sheet = self.sheet
        if sheet.identify_row(event) == None or sheet.identify_column(event) == None:
            return
        py3_common.Logging.debug(self.getClassName(),'onSheetKeyBoardDeleteClick')
        self.onBtnDelClick()

    # 表格复制
    def _tkSheetSingleCopy(self, sheet):
        currentlySelected = self.sheet.get_currently_selected()  #当前选中行列
        try:
            r,c = currentlySelected.row, currentlySelected.column
            data = self.sheet.get_data(r,c,r+1,c+1)
            copyStr = str(data)
            # self.clipboard_clear()
            # self.clipboard_append(copyStr)
            GlobalValue.copyStr2Clipboard(copyStr)
            py3_common.Logging.info2('复制内容：%s' % copyStr)
        except Exception as e:
            # raise e
            py3_common.Logging.warning('复制内容失败')
            py3_common.Logging.warning(e)

    # 表格ctrl+c
    def onSheetCtrlCClick(self, event):
        py3_common.Logging.debug(self.getClassName(),'onSheetCtrlCClick')
        self._tkSheetSingleCopy(self.sheet)

    # 响应表格右键点击
    def _onTkSheetRightClick(self, event, sheet, menubar):
        # py3_common.Logging.info(event)
        r = sheet.identify_row(event)
        c = sheet.identify_column(event)
        if r != None and c != None and not sheet.is_rc_out_of_range(r,c):
            sheet.select_cell(r, c, redraw=False)
            menubar.delete(0,END)
            menubar.add_command(label='复制', command=lambda ent=sheet:self._tkSheetSingleCopy(ent), accelerator='Ctrl+C')
            menubar.post(event.x_root,event.y_root)

    # 绑定表格右键点击
    def bindSheetRightClick(self):
        sheet = self.sheet
        menubar = Menu(sheet, tearoff=False)
        self.tkThemeHelper.addTkObj(menubar)
        sheet.bind('<Button-3>', lambda e, ent=sheet, menu=menubar:self._onTkSheetRightClick(e, ent, menu))

    # ctrl+z 撤销
    def onKeyboardCtrlZClick(self, event):
        py3_common.Logging.debug(self.getClassName(),'onKeyboardCtrlZClick')
        suc = self.undoRedoHelper.undo(self.tlNowData)
        if suc:
            self.updateView()

    # ctrl+y 重做
    def onKeyboardCtrlYClick(self, event):
        py3_common.Logging.debug(self.getClassName(),'onKeyboardCtrlYClick')
        suc = self.undoRedoHelper.redo(self.tlNowData)
        if suc:
            self.updateView()

    def onKeyboardArrowClick(self, arrow):
        # py3_common.Logging.debug(self.getClassName(),'onKeyboardArrowClick', arrow)
        # r,c = self.sheet.get_currently_selected_rc()
        # if r == None or c == None:
        #     rAmount, cAmount = self.sheet.get_row_col_amount()
        #     if rAmount > 0 and cAmount > 0:
        #         rn, cn = 0, 0
        #         if arrow == ArrowDirEnum.Up:
        #             rn = rAmount-1
        #         elif arrow == ArrowDirEnum.Left:
        #             cn = cAmount-1
        #         self.sheet.select_cell(rn, cn, redraw=False)
        #         self.sheet.MT.see(rn, cn, keep_xscroll=True, check_cell_visibility=False)
        #         self.after(1, lambda: self.sheet.MT.focus_set())
        GlobalValue.onKeyboardArrowClickInViewWithTkSheet(self, self.sheet, arrow)

    def onKeyboardEscapeClick(self):
        py3_common.Logging.debug(self.getClassName(),'onKeyboardEscapeClick')
        self.onBtnCancel()

    # 搜索回调
    def onSearchStrCallback(self, copyStr, index):
        sheet = self.sheet
        rn, cn = index, 0
        if not sheet.is_rc_completely_visible(rn, cn):
            sheet.select_cell(rn, cn, redraw=False)
            sheet.MT.see(rn, cn, keep_xscroll=True, check_cell_visibility=False)
        else:
            sheet.select_cell(rn, cn, redraw=True)



    # -----------------------------按钮响应-----------------------------
    # 添加
    def onBtnAddClick(self):
        py3_common.Logging.debug(self.getClassName(),'onBtnAddClick')
        self.showEditViewText(len(self.tlNowData))

    # 删除
    def onBtnDelClick(self):
        py3_common.Logging.debug(self.getClassName(),'onBtnDelClick')
        sheet = self.sheet
        r,c,rcSuc = py3_common.tkSheetGetSelectedRCHelper(sheet, isShowMessageBox=True, messageboxParent=self)
        if not rcSuc:
            return
        self.delData([r])

    # 上移
    def onBtnUpClick(self):
        py3_common.Logging.debug(self.getClassName(),'onBtnUpClick')
        sheet = self.sheet
        r,c,rcSuc = py3_common.tkSheetGetSelectedRCHelper(sheet, isShowMessageBox=True, messageboxParent=self)
        if not rcSuc:
            return
        if r <= 0:
            return
        tlNowData = py3_common.deep_copy_dict(self.tlNowData)
        tempTmInfo = tlNowData[r]
        del tlNowData[r]
        tlNowData.insert(r-1, tempTmInfo)
        sheet.select_cell(r-1, c, redraw=False)
        sheet.MT.see(r-1, c, keep_xscroll=True, check_cell_visibility=False)
        self._setData([], tlNowData)

    # 下移
    def onBtnDownClick(self):
        py3_common.Logging.debug(self.getClassName(),'onBtnDownClick')
        sheet = self.sheet
        r,c,rcSuc = py3_common.tkSheetGetSelectedRCHelper(sheet, isShowMessageBox=True, messageboxParent=self)
        if not rcSuc:
            return
        if r >= len(self.tlNowData)-1:
            return
        tlNowData = py3_common.deep_copy_dict(self.tlNowData)
        tempTmInfo = tlNowData[r]
        del tlNowData[r]
        tlNowData.insert(r+1, tempTmInfo)
        sheet.select_cell(r+1, c, redraw=False)
        sheet.MT.see(r+1, c, keep_xscroll=True, check_cell_visibility=False)
        self._setData([], tlNowData)

    # 复制一份
    def onBtnCopyOneClick(self):
        py3_common.Logging.debug(self.getClassName(),'onBtnCopyOneClick')
        sheet = self.sheet
        r,c,rcSuc = py3_common.tkSheetGetSelectedRCHelper(sheet, isShowMessageBox=True, messageboxParent=self)
        if not rcSuc:
            return
        info = self.tlNowData[r]
        self._setData([r+1], info, isInsert=True)
        sheet.select_cell(r+1, c, redraw=False)
        sheet.MT.see(r+1, c, keep_xscroll=True, check_cell_visibility=False)

    # 编辑
    def onBtnEditClick(self):
        py3_common.Logging.debug(self.getClassName(),'onBtnEditClick')
        sheet = self.sheet
        r,c,rcSuc = py3_common.tkSheetGetSelectedRCHelper(sheet, isShowMessageBox=True, messageboxParent=self)
        if not rcSuc:
            return
        self.showEditViewText(r)

    # 搜索
    def onBtnSearchClick(self):
        py3_common.Logging.debug(self.getClassName(),'onBtnSearchClick')
        tlStr = list()
        tlTlData = self.tlTlData
        for i in range(0,len(tlTlData)):
            tlStr.append(tlTlData[i][0])
        view = ViewLineCopyString(self, tlStr, fCallback=self.onSearchStrCallback, isCopyStr=False)

    # 确定修改
    def onBtnConfirm(self, isCloseView=True):
        py3_common.Logging.debug(self.getClassName(),'onBtnConfirm')
        if self.undoRedoHelper.hasModify():
            self.dispatchConfirmEvent(self.tlNowData, self.tlKey)
            self.undoRedoHelper.markSave()  #记录保存
        if isCloseView:
            self.close()

    # 取消
    def onBtnCancel(self):
        py3_common.Logging.debug(self.getClassName(),'onBtnCancel')
        if self.undoRedoHelper.hasModify():
            value = messagebox.askyesnocancel('确认', '是否保存修改', parent=self)
            if value == None:
                return
            elif value == False:
                self.close()
            else:
                self.onBtnConfirm()
        else:
            self.close()

    # 弹文本输入框界面
    def showEditViewText(self, index):
        py3_common.Logging.debug(self.getClassName(),'showEditViewText')
        tlNowData = self.tlNowData
        try:
            title = '输入文本'
            textStr = tlNowData[index] if index >= 0 and index < len(tlNowData) else ''

            tlCustomBtnData = [
                {
                    'text': '确定',
                    'command': lambda v, i=index:self.onEditConfirm(v, i),
                    'bindKey':'<Control-Return>',
                },
                {
                    'text': '取消',
                    'command': lambda v, i=index:self.onEditEscape(v, i),
                },
            ]
            tlBind = [
                {
                    'bindKey':'<Escape>',
                    'fCallback':lambda v, i=index:self.onEditEscape(v, i),
                },
                {
                    'bindKey':'WM_DELETE_WINDOW',
                    'fCallback':lambda v, i=index:self.onEditEscape(v, i),
                },
            ]

            viewTextType = ViewTextTypeEnum.Text
            view = ViewText(self, title=title, text=textStr, enable=True, tlCustomBtnData=tlCustomBtnData, viewTextType=viewTextType, tlBind=tlBind)
        except Exception as e:
            py3_common.Logging.error_(self.getClassName(),'showEditViewText')
            py3_common.Logging.error_('index', index)
            raise e

    # 确定修改
    def onEditConfirm(self, view, index):
        py3_common.Logging.debug(self.getClassName(),'onEditConfirm')
        textStr = view.getTextStr()
        try:
            if py3_common.is_str_empty(textStr):
                py3_common.messageboxShowerror2('错误','请输入文本',parent=view)
                return
            view.close()
            self._setData([index], textStr)
        except Exception as e:
            py3_common.Logging.error_(self.getClassName(),'onEditConfirm')
            py3_common.Logging.error_('index', index)
            raise e

    # 键盘esc
    def onEditEscape(self, view, index):
        py3_common.Logging.debug(self.getClassName(),'onEditEscape')
        hasModify = False
        oldTextStr, suc = py3_common.getValueWithTlKey(self.tlNowData, [index])
        if suc:
            textStr = view.getTextStr()
            hasModify = textStr != oldTextStr
        else:
            textStr = view.getTextStr()
            hasModify = not py3_common.is_str_empty(textStr)
        if hasModify:
            value = messagebox.askyesnocancel('确认', '是否保存修改', parent=view)
            if value == None:
                return
            elif value == False:
                view.close()
            else:
                self.onEditConfirm(view, index)
        else:
            view.close()




    # -----------------------------事件响应-----------------------------
    # 发送确认修改事件
    def dispatchConfirmEvent(self, tlNowData, tlKey):
        dispatchEvent(EventType.Event_SettingTlCommonStringChange, tlNowData, tlKey)

    def onEvent_UndoRedoHelperDataChange(self, uid):
        if uid == self.undoRedoHelper.getUid():
            py3_common.Logging.debug(self.getClassName(),'onEvent_UndoRedoHelperDataChange')
            self.setTitleWithModify(self.undoRedoHelper.hasModify())




    # -----------------------------数据-----------------------------
    # 删除数据
    def delData(self, tlKey):
        py3_common.Logging.debug(self.getClassName(),'delData')
        self._setData(tlKey, None, isDel=True)

    # 设置数据
    def _setData(self, tlKey, value, isDel=False, isInsert=False):
        self.undoRedoHelper.setValueWithTlKey(self.tlNowData, tlKey, value, isDel=isDel, isInsert=isInsert)
        self.updateView()
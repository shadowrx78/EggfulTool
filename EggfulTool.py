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
# from PIL import Image, ImageTk

import sys
from sys import platform
from importlib import import_module
import traceback

# import ccbparser
# import plistlib

from concurrent.futures import ThreadPoolExecutor, wait

from script import tkVirtualListHelper

from script import py3_common
from ctypes import windll

from script import GlobalValue
from script import SysTrayIcon
from script.GlobalValue import *
from script.EventProxy import *

from script.node.LineNode import *
from script.node.BtnNode import *
from script.node.CreateNode import *

from script.view.ListLineNodeView import *
from script.view.NodeSettingView import *
from script.view.RootSettingView import *

# import win32ui
# import win32gui
# import win32con
# import win32api


PROGRAM_TITLE_NAME = '有点卵用工具'
PROGRAM_NAME = 'EggfulTool'
PROGRAM_VERSION = '1.0.7α1'

TL_UI_MODE_DATA = [
    {'name':'通常', 'key':UiModeEnum.Normal},
    {'name':'编辑', 'key':UiModeEnum.Edit}
]

# 打包成exe后内部资源路径要改下
EXE_SOURSE_BASE_PATH = None
try:
    EXE_SOURSE_BASE_PATH = sys._MEIPASS
except Exception as e:
    EXE_SOURSE_BASE_PATH = '.'

ICO_PATH = os.path.join(EXE_SOURSE_BASE_PATH, 'script/icon.ico')









class PrintLogger(object):  # create file like object
    def __init__(self, mainView):  # pass reference to text widget
        self.mainView = mainView  # keep ref

    def write(self, text):
        Logging.error_(text, end='')
        # messagebox.showerror('错误', text, parent=self.mainView)
        # print(text)

    def flush(self):  # needed for file like object
        pass


# 设置tk报错回调
Tk.report_callback_exception = py3_common.showError


# cmd命令相关
def popen(cmd, mode='r', bufsize=-1):
    # print "--------popen"
    # print cmd
    if mode == 'w':
        return subprocess.Popen(cmd, shell=True, bufsize=bufsize, stdin=subprocess.PIPE).stdin
    else:
        return subprocess.Popen(cmd, shell=True, bufsize=bufsize, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL).stdout


# # 解析成imageTk
# def getTkImage(pilImage, width=None, height=None):
#     if pilImage:
#         # print("+++++++++++++++++++++++++")
#         # print(pilImage)
#         image_tk = None
#         if width or height:
#         # if True:
#             ow,oh = pilImage.size
#             nw,nh = 0,0
#             if not width:
#                 width = ow
#             if not height:
#                 height = oh

#             if ow/width >= oh/height:
#                 nw = math.floor(width)
#                 nh = math.floor(math.floor(width)*oh/ow)
#             else:
#                 nw = math.floor(math.floor(height)*ow/oh)
#                 nh = math.floor(height)

#             if nw > 0 and nh > 0:
#                 image = pilImage.resize((nw,nh), Image.ANTIALIAS)
#                 image_tk = ImageTk.PhotoImage(image=image)
#         else:
#             image_tk = ImageTk.PhotoImage(image=pilImage)
#         return image_tk
#     return None



# # 初始化节点类型信息
GlobalValue.TM_NODE_TYPE = {
    'Base':{'class':tkVirtualListHelper.BaseNode, 'defaultSize':{'width':0, 'height':0}},     #父类 姑且能创但基本没用
    'Line':{'class':LineNode, 'defaultSize':{'width':0, 'height':20}},     #分割线
    'Btn':{'class':BtnNode, 'defaultSize':{'width':GlobalValue.FRAME_DEFAULT_WIDTH, 'height':GlobalValue.FRAME_DEFAULT_HEIGHT}},      #按钮
    'Create':{'class':CreateNode, 'defaultSize':{'width':GlobalValue.FRAME_DEFAULT_WIDTH, 'height':GlobalValue.FRAME_DEFAULT_HEIGHT}}    #新建 编辑模式才出来
}







# 主界面
class MainGui(Frame):
    def __init__(self,initWindow):
        super().__init__(initWindow)
        self.initWindow = initWindow
        # sys.stderr = PrintLogger(self)
        self.setInitWindow()

    def __del__(self):
        py3_common.Logging.info2('MainGui __del__')


    #设置窗口
    def setInitWindow(self):
        #设置顶级窗体的行列权重，否则子组件的拉伸不会填充整个窗体
        self.initWindow.rowconfigure(0,weight=1)
        self.initWindow.columnconfigure(0,weight=1)
        #设置继承类MWindow的行列权重，保证内建子组件会拉伸填充
        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)

        self.initWindow.title("%s v%s" % (PROGRAM_TITLE_NAME, PROGRAM_VERSION))           #窗口名
        self.initWindow.iconbitmap(ICO_PATH)
        #self.initWindow.geometry('320x160+10+10')                         #290 160为窗口大小，+10 +10 定义窗口弹出时的默认展示位置
        self.initWindow.geometry('1080x640')
        # self.initWindow["bg"] = "pink"                                    #窗口背景色，其他背景色见：blog.csdn.net/chl0000/article/details/7657887
        self.initWindow.attributes("-alpha", GlobalValue.WINDOW_ALPHA/100.0)                          #虚化，值越小虚化程度越高
        self.initWindow.minsize(600, 400)                                  #限制窗口最小大小
        # self.initWindow.wm_attributes('-topmost',1)       #置顶

        # 禁用最大化按钮
        # self.initWindow.resizable(0,0)
        # toplevel.transient(1)     #子界面这样写

        self.initWindow.bind('<FocusIn>', self.onFocus)

        # self.initWindow.wm_attributes('-type', 'splash')
        # self.initWindow.overrideredirect(True)

        self.dnd = TkDnD(self.initWindow)

        # self['bg'] = 'black'
        # self.configure(bg='black')
        self.grid(row=0,column=0,sticky='nsew')

        # ---------菜单栏---------
        self.mbar = Menu(self.initWindow)                      #定义顶级菜单实例
        self.menuFile = Menu(self.mbar, tearoff=False)             #在顶级菜单下创建菜单项
        self.mbar.add_cascade(label=' 文件 ',menu=self.menuFile) #添加子菜单
        # FileOption.add_command(label="Open Folder", command=None, accelerator="Ctrl+Shift+O")  
        self.menuFile.add_command(label="从文件导入节点配置",command=self.menuImportNodesConfig)
        self.menuFile.add_command(label="从文件导入设置",command=self.menuImportSetting)
        self.menuFile.add_command(label="导出当前节点配置",command=self.menuExportNodesConfig)
        self.menuFile.add_command(label="导出当前设置",command=self.menuExportSetting)
        self.menuFile.add_separator()                        #添加分割线
        self.menuFile.add_command(label="定位到节点配置文件",command=lambda path=GlobalValue.NODES_CONFIG_JSON_PATH:self.openPathOnExplorer(path))
        self.menuFile.add_command(label="定位到设置配置文件",command=lambda path=GlobalValue.SETTING_CONFIG_JSON_PATH:self.openPathOnExplorer(path))
        self.menuFile.add_command(label="定位到已删除节点备份文件",command=lambda path=GlobalValue.DELETED_NODES_BACKUP_JSON_PATH:self.openPathOnExplorer(path))
        self.menuFile.add_command(label="定位到配置备份路径",command=lambda path=GlobalValue.JSON_BACKUP_DIR:self.openPathOnExplorer(path))
        self.menuFile.add_separator()                        #添加分割线
        self.menuFile.add_command(label="刷新",command=self.menuRefresh)
        self.menuFile.add_command(label="格式化节点配置路径",command=self.menuFormatNodesConfigPaths)
        self.menuFile.add_separator()                        #添加分割线
        self.menuFile.add_command(label="退出",command=self.closeRootWindow)

        self.menuOptions = Menu(self.mbar, tearoff=False)             #在顶级菜单下创建菜单项
        self.mbar.add_cascade(label=' 选项 ',menu=self.menuOptions) #添加子菜单

        self.menuOptionsAskExe = Menu(self.menuOptions, tearoff=False)
        self.tmIsAskBeforeExecuting = dict()
        for i in range(0,len(GlobalValue.TL_SETTING_KEY)):
            typeStr = GlobalValue.TL_SETTING_KEY[i]
            if typeStr != 'line':
                self.tmIsAskBeforeExecuting[typeStr] = IntVar()
                self.tmIsAskBeforeExecuting[typeStr].set(1 if getOptionAskBeforeExecuting(typeStr) else 0)
                self.menuOptionsAskExe.add_checkbutton(label=typeStr, command=lambda t=typeStr:self.menuGlobalAskBeforeExecuting(t), variable=self.tmIsAskBeforeExecuting[typeStr])
        self.menuOptions.add_cascade(label='全局 执行前询问 ',menu=self.menuOptionsAskExe) #添加子菜单

        self.isDisableRightClickEdit = IntVar()
        self.isDisableRightClickEdit.set(1 if GlobalValue.DISABLE_RCLICK_EDIT_NODE else 0)
        self.menuOptions.add_checkbutton(label="禁用右键编辑节点", command=self.menuDisableRightClickEdit, variable=self.isDisableRightClickEdit)
        self.menuOptions.add_separator()                        #添加分割线
        self.menuOptions.add_command(label="设置",command=self.menuSetting)

        self.menuDebug = Menu(self.mbar, tearoff=False)             #在顶级菜单下创建菜单项
        self.mbar.add_cascade(label=' 调试 ',menu=self.menuDebug) #添加子菜单
        self.menuDebug.add_command(label="查看当前环境变量",command=self.menuPrintEnviron)
        self.menuDebug.add_command(label="复制环境变量到剪贴板",command=self.menuCopyEnvironToClipboard)
        if GlobalValue.IS_DEBUG:
            self.menuDebug.add_command(label="测试报错",command=self.menuTestShowError)
            self.menuDebug.add_command(label="测试双击小图标",command=self.onSysTrayLDoubleClick)

        self.menuHelp = Menu(self.mbar, tearoff=False)             #在顶级菜单下创建菜单项
        self.mbar.add_cascade(label=' 帮助 ',menu=self.menuHelp) #添加子菜单
        self.menuHelp.add_command(label="使用说明",command=self.menuShowHelp)

        self.initWindow.config(menu=self.mbar)                     #将顶级菜单注册到窗体

        self.initWindow.bind('<Up>', lambda e,arrow=ArrowDirEnum.Up:self.onKeyboardArrowClick(arrow))
        self.initWindow.bind('<Left>', lambda e,arrow=ArrowDirEnum.Left:self.onKeyboardArrowClick(arrow))
        self.initWindow.bind('<Down>', lambda e,arrow=ArrowDirEnum.Down:self.onKeyboardArrowClick(arrow))
        self.initWindow.bind('<Right>', lambda e,arrow=ArrowDirEnum.Right:self.onKeyboardArrowClick(arrow))
        self.initWindow.bind('<Delete>', self.onKeyBoardDeleteClick)
        self.initWindow.bind('<Control-p>', lambda e,mode=ListLineNodeViewModeEnum.P:self.openListLineNodeView(mode))
        self.initWindow.bind('<Control-r>', lambda e,mode=ListLineNodeViewModeEnum.R:self.openListLineNodeView(mode))
        self.initWindow.bind('<Control-f>', lambda e,mode=ListLineNodeViewModeEnum.F:self.openListLineNodeView(mode))
        self.initWindow.bind('<Control-c>', lambda e:self.copySelectNodeConfig())
        self.initWindow.bind('<Home>', lambda e,v=0:self.jumpTo(v))
        self.initWindow.bind('<End>', lambda e,v=1:self.jumpTo(v))
        self.initWindow.bind('<Prior>', lambda e,v=-1:self.jumpWithPageUpDown(v))
        self.initWindow.bind('<Next>', lambda e,v=1:self.jumpWithPageUpDown(v))
        # self.initWindow.bind("<Key>", lambda e: print(f"<Key> {e.char!r}"))
        self.initWindow.bind('<Escape>', self.onKeyBoardEscapeClick)
        # self.initWindow.bind('<Enter>', lambda e:self.initWindow.focus_force())

        self.isHideTitleBar = False
        self.initWindow.bind('<F11>', lambda e:self.switchHideTitleBar())

        # 鼠标在界面内无点击移动事件
        self.initWindow.bind('<Motion>', self.onRootMotion)

        # 鼠标中键拖动窗口
        self.initWindow.bind('<Button-2>', self.onMouseButton2Click)
        self.initWindow.bind('<B2-Motion>', self.onMouseButton2Motion)

        # 覆盖关闭按钮功能
        self.initWindow.protocol("WM_DELETE_WINDOW", self.closeRootWindow)


        panelWindow1 = PanedWindow(self, showhandle=False, sashrelief='sunken')
        panelWindow1.grid(row=0,column=0,sticky='nsew')
        self.panelWindow1 = panelWindow1

        # ---------主Frame---------
        frameMain = Frame(panelWindow1)
        # frm_left.grid(row=0,column=0,sticky='nsew');#左侧Frame帧拉伸填充
        panelWindow1.add(frameMain, minsize=320)    #限制Frame最小大小
        self.frameMain = frameMain

        frameMain.rowconfigure(0,weight=1)
        # frameMain.rowconfigure(1,weight=1)
        frameMain.columnconfigure(0,weight=1)

        # frame_t1 = Frame(frameMain, relief='ridge', bd=1)
        # frame_t1.grid(row=0,column=0,sticky='nsew')
        # frame_t1.bind('<Button-1>', self.on_frame_t1_click)
        # frame_t2 = Frame(frameMain, relief='ridge', bd=1)
        # frame_t2.grid(row=1,column=0,sticky='nsew')
        # frame_t2.bind('<Button-1>', self.on_frame_t2_click)

        # ---------虚拟列表---------
        if True:
            # style = ttk.Style()
            # style.theme_use('clam')
            # style.configure("Vertical.TScrollbar", gripcount=0, borderwidth=0,
            #                 background="blue", darkcolor="DarkGreen", lightcolor="LightGreen",
            #                 troughcolor="gray", bordercolor="green", arrowcolor="white", arrowsize=20)

            args = dict()
            args['createNodeFun'] = self.createNodeFun
            args['getNodeSizeWithDataFun'] = self.getNodeSizeWithDataFun
            args['isBindMouseWheel'] = True
            args['hasScrollbar'] = True
            args['padding'] = {'w':10, 'h':10}
            # args['canvasKwArgs']={'bg':'black'}
            args['canvasKwArgs']={'highlightthickness':0}   #画布自带2像素边界，不消除掉换颜色会很怪
            # args['onScrollFrameConfigureFun'] = self.onScrollFrameConfigureFun
            args['onEnterFun'] = self.onVirtualListEnter
            args['onLeaveFun'] = self.onVirtualListLeave
            virtualListFrame = tkVirtualListHelper.VirtualListFrame(frameMain, args, relief='groove', bd=3)
            virtualListFrame.grid(row=0,column=0,sticky='nsew')
            self.virtualListFrame = virtualListFrame

        # ---------模式选择---------
        frameMode = Frame(frameMain, relief='flat', bd=3)    #模式底Frame
        frameMode.grid(row=1,column=0,sticky='nsew')
        self.frameMode = frameMode
        frameMode.rowconfigure(0,weight=1)
        frameMode.columnconfigure(0,weight=1)
        frameModeSelectBtn = Frame(frameMode)
        self.frameModeSelectBtn = frameModeSelectBtn
        frameModeSelectBtn.grid(column=0, row=0, sticky='ew')
        label = Label(frameModeSelectBtn, text='模式：')
        label.grid(column=0, row=0)
        self.frameModeLabel = label
        # 模式单选按钮
        self.modeSelectValue = IntVar()
        self.modeSelectValue.set(0)
        self.tlModeRadiobutton = list()
        for x in range(0,len(TL_UI_MODE_DATA)):
            modeData = TL_UI_MODE_DATA[x]
            modeName = modeData['name'] if 'name' in modeData else modeData['key']
            btn = Radiobutton(frameModeSelectBtn, text=modeName, variable=self.modeSelectValue, value=x, command=lambda :self.selectUiMode(self.modeSelectValue.get()), takefocus=0)
            btn.grid(column=x+1, row=0)
            self.tlModeRadiobutton.append(btn)
        self.initWindow.bind('<Control-Tab>', lambda e:self.selectUiMode((self.modeSelectValue.get() + 1) % len(TL_UI_MODE_DATA)))

        # ---------缓存初始化---------
        self.settingView = None
        self.listLineNodeView = None
        self.rootSettingView = None
        self.isInVirtualList = False
        self.inVirtualListMousePos = None

        self.eventNodeChangeHandle = addEventListener(EventType.Event_NodeChange, self.onEventNodeChange)
        self.eventSettingColorChangeHandle = addEventListener(EventType.Event_SettingColorChange, self.onEventSettingColorChange)
        self.eventSettingOptionsChangeHandle = addEventListener(EventType.Event_SettingOptionsChange, self.onEventSettingOptionsChange)

        self.tkPosX = 0
        self.tkPosY = 0
        self.initWindow.update_idletasks()
        self.frmW = self.initWindow.winfo_rootx() - self.initWindow.winfo_x()
        self.frmH = self.initWindow.winfo_rooty() - self.initWindow.winfo_y()

        self.executor = ThreadPoolExecutor(max_workers=1)   #线程池
        GlobalValue.ROOT_THREAD_POOL_EXECUTOR = self.executor

        self.refreshColors()
        self.updateTlNode()
        # self.test_create_nodes()

        # # 弹出初始化错误提示
        # showTlInitErrorMsg()

        # 通知栏图标相关
        menuOptions = (('设置', None, self.onSysTraySetting),)
        self.sysTrayIcon = SysTrayIcon.SysTrayIcon(ICO_PATH,
            PROGRAM_TITLE_NAME,
            menuOptions,
            on_quit=self.onSysTrayExit,
            quit_text='退出',
            on_ldouble_click=self.onSysTrayLDoubleClick,
            window_class_name=PROGRAM_NAME,
            )




    # -----------------------------菜单栏-----------------------------
    # 从文件导入节点配置
    def menuImportNodesConfig(self):
        filePath = filedialog.askopenfilename(title='选择节点配置文件', filetypes=[('Json文件','.json'), ('','.*')], initialdir='.')
        if not filePath or not os.path.isfile(filePath):
            return
        self.copyAndCoverFile(filePath, GlobalValue.NODES_CONFIG_JSON_PATH)
        self.menuRefresh()

    # 从文件导入设置
    def menuImportSetting(self):
        filePath = filedialog.askopenfilename(title='选择设置文件', filetypes=[('Json文件','.json'), ('','.*')], initialdir='.')
        if not filePath or not os.path.isfile(filePath):
            return
        self.copyAndCoverFile(filePath, GlobalValue.SETTING_CONFIG_JSON_PATH)
        self.menuRefresh()

    # 导出当前节点配置
    def menuExportNodesConfig(self):
        filePath = filedialog.asksaveasfilename(title='选择保存路径', initialfile=os.path.basename(GlobalValue.NODES_CONFIG_JSON_PATH), defaultextension='.json',filetypes = [("Json文件",".json")])
        if not filePath:
            return
        exportTempJson(GlobalValue.TEMP_NODE_LIST, filePath, isNodesConfig=True)

    # 导出当前设置
    def menuExportSetting(self):
        filePath = filedialog.asksaveasfilename(title='选择保存路径', initialfile=os.path.basename(GlobalValue.SETTING_CONFIG_JSON_PATH), defaultextension='.json',filetypes = [("Json文件",".json")])
        if not filePath:
            return
        tmSetting = getTmSettingData()
        exportTempJson(tmSetting, filePath, isNodesConfig=False)

    def copyAndCoverFile(self, fromFilePath, toFilePath):
        # oldFName = os.path.basename(fromFilePath)
        # newFName = os.path.basename(toFilePath)
        newDir = os.path.dirname(toFilePath)
        if os.path.isfile(toFilePath):
            py3_common.delete_file_folder(toFilePath)
        py3_common.check_dir(newDir)
        py3_common.copy_file_in_dir(fromFilePath, toFilePath)

    # 初始化json
    def menuRefresh(self):
        # folder_selected = filedialog.askopenfilename(title='选择文件', filetypes=[('battle.proto','.proto')])
        # self.init_desc_file(folder_selected)
        refreshNodesConfig()
        refreshProjectSetting()
        # 弹出初始化错误提示
        showTlInitErrorMsg()
        self.refreshColors()
        self.refreshOptions()
        self.updateTlNode()

    # 设置
    def menuSetting(self):
        if self.rootSettingView:
            try:
                self.rootSettingView.destroy()
            except Exception as e:
                # raise e
                pass
            self.rootSettingView = None

        # 弹框用TopLevel
        # py3_common.Logging.debug3(index)
        view = RootSettingView(self.initWindow, self)
        # view.wm_attributes('-topmost',1)
        # view.minsize(300, 200)
        self.rootSettingView = view
        view.after(1, lambda: view.focus_force())

        tkCenter(view)

        # 锁定焦点
        view.grab_set()

    # 使用说明
    def menuShowHelp(self):
        tipsStr = '''主窗口：
ctrl+p：搜索分割线
ctrl+r：搜索标记
ctrl+f：搜索全部
ctrl+tab：切换模式

通常模式：
右键点击打开配置面板

编辑模式：
左键点击打开配置面板，右键点击选中
选中状态下：
键盘←/↑：节点上移，键盘↓/→：节点下移
键盘delete：删除节点
键盘ctrl+c：复制节点json至剪贴板
键盘esc：返回通常模式

配置面板：
键盘alt+c：复制节点json至剪贴板
键盘alt+v：粘贴剪贴板json
键盘esc：关闭配置面板

搜索面板：
键盘↑/↓：选择搜索结果
键盘esc/enter：关闭搜索面板
搜索逻辑使用精确匹配'''
        messagebox.showinfo('帮助', tipsStr)

    # 打印当前环境变量
    def menuPrintEnviron(self):
        envContent = self.getEnvironJsonContent()
        messagebox.showinfo('当前环境变量', envContent)

    # 复制环境变量到剪贴板
    def menuCopyEnvironToClipboard(self):
        envContent = self.getEnvironJsonContent()
        self.clipboard_clear()
        self.clipboard_append(envContent)

    def getEnvironJsonContent(self):
        env = os.environ
        envDict = dict(env)
        content = json.dumps(envDict, ensure_ascii=False, indent=2, sort_keys=True)
        return content

    # 格式化节点配置文件内路径
    def menuFormatNodesConfigPaths(self):
        # global TEMP_NODE_LIST
        for i in range(0,len(GlobalValue.TEMP_NODE_LIST)):
            nodeData = GlobalValue.TEMP_NODE_LIST[i]
            if nodeData['nodeType'] == 'Btn':
                settingKey = getSettingKey(nodeData)
                tlPathKeyData = list()
                if settingKey == 'folder':
                    tlPathKeyData.append({'key':'folderPath', 'isTl':False})
                elif settingKey == 'exe':
                    tlPathKeyData.append({'key':'exePath', 'isTl':False})
                elif settingKey == 'cmd':
                    tlPathKeyData.append({'key':'tlFilePath', 'isTl':True})
                for pathKeyData in tlPathKeyData:
                    if pathKeyData['isTl']:
                        for i2 in range(0,len(nodeData[pathKeyData['key']])):
                            if nodeData[pathKeyData['key']][i2] != '':
                                nodeData[pathKeyData['key']][i2] = os.path.normpath(nodeData[pathKeyData['key']][i2])
                    else:
                        if nodeData[pathKeyData['key']] != '':
                            nodeData[pathKeyData['key']] = os.path.normpath(nodeData[pathKeyData['key']])
        self.saveTlNodeData()

    # 全局执行前询问开关
    def menuGlobalAskBeforeExecuting(self, typeStr):
        setOptionAskBeforeExecuting(typeStr, self.tmIsAskBeforeExecuting[typeStr].get() > 0)
        saveProjectSetting()

    # 禁用右键编辑节点
    def menuDisableRightClickEdit(self):
        GlobalValue.DISABLE_RCLICK_EDIT_NODE = self.isDisableRightClickEdit.get() > 0
        saveProjectSetting()

    # 在文件资源管理器打开路径
    def openPathOnExplorer(self, path):
        py3_common.Logging.debug('打开%s' % os.path.abspath(path))
        if os.path.isfile(path):
            popen('explorer /select,"'+ os.path.abspath(path) + '"')
        elif os.path.isdir(path):
            os.startfile(os.path.abspath(path))
        else:
            messagebox.showinfo('提示', '路径不存在：%s' % os.path.abspath(path), parent=self)

    # 关闭界面
    def closeRootWindow(self):
        py3_common.Logging.debug('closeRootWindow 主界面关闭')
        # self.initWindow.destroy()
        if self.sysTrayIcon != None:
            self.sysTrayIcon.destroy()
        # 粗暴杀进程
        os._exit(0)



    # -----------------------------通知栏小图标-----------------------------
    # 小图标运行在不同线程，回调如果要操作主窗口，则需要先回到主线程再调用
    def sysTrayThreadHelper(self, sysTrayIcon=None):
        time.sleep(0.01)
        return sysTrayIcon

    def onSysTrayCallback(self, command, sysTrayIcon=None):
        if not self:
            return
        thread = self.executor.submit(self.sysTrayThreadHelper, sysTrayIcon)
        thread.add_done_callback(lambda s: command(s))

    # 左键双击
    def onSysTrayLDoubleClick(self, sysTrayIcon=None):
        py3_common.Logging.debug('onSysTrayLDoubleClick')
        def helper(s=None):
            self.initWindow.wm_deiconify()  #最小化了要重新弹出界面
            self.initWindow.focus_force()   #设置焦点
        self.onSysTrayCallback(helper, sysTrayIcon)

    # 退出
    def onSysTrayExit(self, sysTrayIcon=None):
        py3_common.Logging.debug('onSysTrayExit')
        # self.initWindow.destroy()
        # os._exit(0)
        self.closeRootWindow()

    # 设置
    def onSysTraySetting(self, sysTrayIcon=None):
        py3_common.Logging.debug('onSysTraySetting')
        self.menuSetting()


    # -----------------------------模式选择-----------------------------
    def selectUiMode(self, index):
        if index >= 0 and index < len(TL_UI_MODE_DATA):
            # 记录鼠标附件节点
            oldNodeIndex, oldNodeRealIndex = self.getNowMouseNearNodeIndex()
            oldYShift = 0
            if oldNodeIndex != None:
                oldYShift = self.virtualListFrame.virtualListCanvas.getIndexVisualYShift(oldNodeIndex)
            # print(oldNodeIndex, oldNodeRealIndex, oldYShift)

            # global UI_MODE
            GlobalValue.UI_MODE = TL_UI_MODE_DATA[index]['key']
            self.modeSelectValue.set(index)
            # py3_common.Logging.info(GlobalValue.UI_MODE)
            # self.refresh_sp_frames()
            self.selectEditItem(None, False)
            self.updateTlNode()

            if oldNodeRealIndex != None:
                newNodeIndex = self.getNodeIndexWithRealNodeIndex(oldNodeRealIndex)
                # print(newNodeIndex, oldYShift)
                self.virtualListFrame.jumpToIndex(newNodeIndex, -oldYShift)

    # 获取现在鼠标附件的节点index和真实节点index
    # 真实节点index排除Create类型节点
    def getNowMouseNearNodeIndex(self):
        nodeIndex = None
        if self.inVirtualListMousePos:
            nodeIndex = self.virtualListFrame.virtualListCanvas.getNearIndexWithPos(self.inVirtualListMousePos)
        else:
            nodeIndex = self.virtualListFrame.virtualListCanvas.getNearIndexWithPos({'x':0, 'y':0})
        if GlobalValue.UI_MODE == UiModeEnum.Normal:
            return nodeIndex, nodeIndex
        else:
            if nodeIndex != None:
                nodeData = GlobalValue.TEMP_NODE_LIST[nodeIndex]
                if nodeData['nodeType'] == 'Create':
                    nodeIndex_ = nodeIndex
                    nodeIndex = None
                    if nodeIndex_ < len(GlobalValue.TEMP_NODE_LIST) - 1:
                        nodeIndex = nodeIndex_ + 1
                    elif nodeIndex_ > 0:
                        nodeIndex = nodeIndex_ - 1
            if nodeIndex != None:
                nodeIndex_ = -1
                for i in range(0,len(GlobalValue.TEMP_NODE_LIST)):
                    nodeData = GlobalValue.TEMP_NODE_LIST[i]
                    if nodeData['nodeType'] != 'Create':
                        nodeIndex_ = nodeIndex_ + 1
                    if i == nodeIndex:
                        break
                return nodeIndex, nodeIndex_
        return None, None

    # 真实节点index转节点index
    def getNodeIndexWithRealNodeIndex(self, realNodeIndex):
        if GlobalValue.UI_MODE == UiModeEnum.Normal:
            return realNodeIndex
        else:
            nodeIndex = None
            nodeIndex_ = -1
            for i in range(0,len(GlobalValue.TEMP_NODE_LIST)):
                nodeData = GlobalValue.TEMP_NODE_LIST[i]
                if nodeData['nodeType'] != 'Create':
                    nodeIndex_ = nodeIndex_ + 1
                if realNodeIndex == nodeIndex_:
                    nodeIndex = i
                    break
            return nodeIndex

    # 将data转换成节点的args
    def convertNodeArgs(self, data=dict()):
        # 拷贝一份data
        args = dict()
        for k in data:
            args[k] = data[k]

        # tkdnd拖入模块
        if not 'dnd' in args:
            args['dnd'] = self.dnd

        if not 'mainView' in args:
            args['mainView'] = self

        return args


    def createNodeFun(self, data, scrollFrame, autoInit=True):
        # args = self.convertNodeArgs(data)
        args = data
        node = None
        if 'nodeType' in data and data['nodeType'] in GlobalValue.TM_NODE_TYPE:
            node = GlobalValue.TM_NODE_TYPE[data['nodeType']]['class'](scrollFrame, args=args, autoInit=autoInit)
        else:
            node = GlobalValue.TM_NODE_TYPE['Base']['class'](scrollFrame, args=args, autoInit=autoInit)
        return node


    def getNodeSizeWithDataFun(self, data):
        nodeType = data['nodeType'] if 'nodeType' in data and data['nodeType'] in GlobalValue.TM_NODE_TYPE else 'Base'
        defaultSize = GlobalValue.TM_NODE_TYPE[nodeType]['defaultSize']
        w = data['width'] if 'width' in data else defaultSize['width']
        h = data['height'] if 'height' in data else defaultSize['height']

        # 特殊处理
        if nodeType == 'Line':
            w = self.virtualListFrame.virtualListCanvas.winfo_width()

        return w, h

    def onVirtualListEnter(self, event):
        self.isInVirtualList = True

    def onVirtualListLeave(self, event):
        self.isInVirtualList = False
        self.inVirtualListMousePos = None

    def onRootMotion(self, event):
        virtualListCanvas = self.virtualListFrame.virtualListCanvas
        # print(event.x, event.y, event.x_root, event.y_root)
        # print(virtualListCanvas.winfo_x(), virtualListCanvas.winfo_y(), virtualListCanvas.winfo_width(), virtualListCanvas.winfo_height(), virtualListCanvas.winfo_rootx(), virtualListCanvas.winfo_rooty())
        posX = event.x_root - virtualListCanvas.winfo_rootx()
        posY = event.y_root - virtualListCanvas.winfo_rooty()
        # 判断在画布内
        if posX >= 0 and posX <= virtualListCanvas.winfo_width() and posY >= 0 and posY <= virtualListCanvas.winfo_height():
            # print('----------------------------------')
            # print(posX, posY)
            self.inVirtualListMousePos = {'x':posX, 'y':posY}
            # print(self.inVirtualListMousePos)
        else:
            self.inVirtualListMousePos = None



    # 设置界面
    def openNodeSettingView(self, index, data=None):
        # if self.inVirtualListMousePos:
        #     nodeIndex = self.virtualListFrame.virtualListCanvas.getNearIndexWithPos(self.inVirtualListMousePos)
        #     print("aaaaaaaaaaaaaaaa", index, nodeIndex)
        self.selectEditItem()

        if self.settingView:
            try:
                self.settingView.destroy()
            except Exception as e:
                # raise e
                pass
            self.settingView = None

        # 弹框用TopLevel
        # py3_common.Logging.debug3(index)
        view = NodeSettingView(self.initWindow, self, index, data)
        # view.wm_attributes('-topmost',1)
        # view.minsize(300, 200)
        self.settingView = view
        view.after(1, lambda: view.focus_force())

        tkCenter(view)

        # 锁定焦点
        view.grab_set()

        # view.rowconfigure(1,weight=1)

    # 搜索行标记界面
    def openListLineNodeView(self, mode):
        if self.listLineNodeView:
            try:
                self.listLineNodeView.destroy()
            except Exception as e:
                # raise e
                pass
            self.listLineNodeView = None

        # 弹框用TopLevel
        # py3_common.Logging.debug3(index)
        view = ListLineNodeView(self.initWindow, self, mode, self.virtualListFrame.getTlData())
        # view.wm_attributes('-topmost',1)
        # view.minsize(300, 200)
        self.listLineNodeView = view
        view.after(1, lambda: view.focus_force())

        tkCenter(view, anchorPos={'x':0.8, 'y':0.5})

        # 锁定焦点
        # view.grab_set()

    def copySelectNodeConfig(self):
        if GlobalValue.NOW_SELECT_INDEX != None and GlobalValue.UI_MODE == UiModeEnum.Edit:
            # tlNodeData = self.virtualListFrame.getTlData()
            tlNodeData = GlobalValue.TEMP_NODE_LIST
            if not tlNodeData or GlobalValue.NOW_SELECT_INDEX >= len(tlNodeData):
                return False
            nodeData = tlNodeData[GlobalValue.NOW_SELECT_INDEX]
            if nodeData['nodeType'] == 'Create':
                return False
            copyStr = json.dumps(nodeData, ensure_ascii=False, indent=None, sort_keys=False)
            py3_common.Logging.debug('-----copy nodeData-----')
            py3_common.Logging.debug(copyStr)
            self.clipboard_clear()
            self.clipboard_append(copyStr)
            return True
        return False

    def updateTlNode(self):
        # global TEMP_NODE_LIST
        self.removeCreateNodeToTlNode()
        if GlobalValue.UI_MODE == UiModeEnum.Edit:
            self.addCreateNodeToTlNode()

        # # global FORCE_SHOW_SELECT
        # GlobalValue.FORCE_SHOW_SELECT = False
        # if self.settingView or self.listLineNodeView:
        #     GlobalValue.FORCE_SHOW_SELECT = True

        tlNodeData = list()
        for i in range(0,len(GlobalValue.TEMP_NODE_LIST)):
            tlNodeData.append(self.convertNodeArgs(GlobalValue.TEMP_NODE_LIST[i]))
        self.virtualListFrame.setTlData(tlNodeData)

        if self.listLineNodeView and self.listLineNodeView.winfo_exists():
            self.listLineNodeView.updateTlNodeData(self.virtualListFrame.getTlData())

    def refreshNodeByIndex(self, index, ui=True, ex=False):
        # # global FORCE_SHOW_SELECT
        # GlobalValue.FORCE_SHOW_SELECT = False
        # if self.settingView or self.listLineNodeView:
        #     GlobalValue.FORCE_SHOW_SELECT = True
        self.virtualListFrame.virtualListCanvas.refreshNodeByIndex(index, ui=ui, ex=ex)

    def onEventNodeChange(self, *args):
        # if GlobalValue.IS_DEBUG:
        #     py3_common.Logging.debug2('MainGui onEventNodeChange', args)
        if args != None and len(args) > 0:
            self.refreshNodeByIndex(*args)
        else:
            self.updateTlNode()

    def addCreateNodeToTlNode(self):
        # global TEMP_NODE_LIST
        createNodeData = {'nodeType':'Create'}
        # createNodeData = {
        #         'nodeType':'Btn',
        #         # 'width':100,
        #         # 'height':100,
        #         # 'bgColor':'white',
        #         # 'typeStr':'folder',
        #         # 'typeStr':'exe',
        #         'typeStr':'cmd',
        #         'useDrop':True,
        #         'btnText':'测试',
        #         'folderPath':'.',
        #         'exePath':'D:/Beyond Compare 4/BCompare.exe',
        #         # 'exePath':'F:/src/branch/lietianxiaQuick3_trunk_black_bt/run_ui2res.bat',
        #         'command':'python %p0 -p %0 -i 2',
        #         # 'command':'python %p -p %0 -i 0',
        #         # 'filePath':u'E:/记录/py/备份/test_svn.py'
        #         'tlFilePath':[u'E:/记录/py/备份/json_helper.py']
        #         # 'filePath':u'E:/sdk-ios/pytest/test14/script/test_svn.py'
        #     }
        createNodeData = self.convertNodeArgs(createNodeData)
        if len(GlobalValue.TEMP_NODE_LIST) > 0:
            if GlobalValue.TEMP_NODE_LIST[len(GlobalValue.TEMP_NODE_LIST)-1]['nodeType'] == 'Create':
                # 加过不加
                return
            # Line为分隔 末尾添加CreateNode
            lastLineIndex = -1
            tlAddIndex = list()
            for i in range(0,len(GlobalValue.TEMP_NODE_LIST)):
                nodeData = GlobalValue.TEMP_NODE_LIST[i]
                if nodeData['nodeType'] == 'Create':
                    # 加过不加
                    return
                if nodeData['nodeType'] == 'Line' and i >= lastLineIndex:
                    tlAddIndex.insert(0, i)     #倒序记录
                    lastLineIndex = i

            for i in range(0,len(tlAddIndex)):
                GlobalValue.TEMP_NODE_LIST.insert(tlAddIndex[i], py3_common.deep_copy_dict(createNodeData))
            # 尾部加一个
            GlobalValue.TEMP_NODE_LIST.append(py3_common.deep_copy_dict(createNodeData))
        else:
            GlobalValue.TEMP_NODE_LIST.append(createNodeData)


    def removeCreateNodeToTlNode(self):
        # global TEMP_NODE_LIST
        if len(GlobalValue.TEMP_NODE_LIST) > 0:
            tlRemoveIndex = list()
            for i in range(0,len(GlobalValue.TEMP_NODE_LIST)):
                nodeData = GlobalValue.TEMP_NODE_LIST[i]
                if nodeData['nodeType'] == 'Create':
                    tlRemoveIndex.insert(0, i)     #倒序记录
            if len(tlRemoveIndex) > 0:
                for i in range(0,len(tlRemoveIndex)):
                    del GlobalValue.TEMP_NODE_LIST[tlRemoveIndex[i]]


    def moveItem(self, index, shift):
        # global TEMP_NODE_LIST

        # 转换真实index
        index_ = self.convertIndex(None, index)
        if index_ == None:
            return
        # 还原真实表
        self.removeCreateNodeToTlNode()

        toIndex = min(max(index_ + shift, 0), len(GlobalValue.TEMP_NODE_LIST))
        # py3_common.Logging.debug(index, index_, shift, toIndex)
        nodeData = GlobalValue.TEMP_NODE_LIST.pop(index_)
        GlobalValue.TEMP_NODE_LIST.insert(toIndex, nodeData)

        if GlobalValue.UI_MODE == UiModeEnum.Edit:
            self.addCreateNodeToTlNode()

        # 转换当前index
        toIndex_ = self.convertIndex(toIndex)
        if toIndex_ == None:
            toIndex_ = index
        if GlobalValue.NOW_SELECT_INDEX == index:
            self.selectEditItem(toIndex_, False)

        self.updateTlNode()
        self.saveTlNodeData()
        if not self.virtualListFrame.virtualListCanvas.isIndexInVisualRange(toIndex_, allInRange=True, isNow=True):
            visualRange = self.virtualListFrame.virtualListCanvas.getScrollFrameVisualRange()
            nodeData_ = self.virtualListFrame.virtualListCanvas.getNodeDataByIndex(toIndex_)
            value = 0
            if nodeData_ and visualRange:
                if nodeData_['y'] + nodeData_['height'] > visualRange['y'] + visualRange['height']:
                    value = 1
            self.jumpToIndex(toIndex_, value=value)
        return toIndex_

    def convertIndex(self, realIndex=None, virtualIndex=None):
        if realIndex != None:
            # 转换成虚拟index
            tempIndex = -1
            for i in range(0,len(GlobalValue.TEMP_NODE_LIST)):
                nodeData = GlobalValue.TEMP_NODE_LIST[i]
                if nodeData['nodeType'] == 'Line' or nodeData['nodeType'] == 'Btn':
                    tempIndex += 1
                if tempIndex == realIndex:
                    return i
        elif virtualIndex != None:
            # 转换成真实index
            tempIndex = -1
            for i in range(0,len(GlobalValue.TEMP_NODE_LIST)):
                nodeData = GlobalValue.TEMP_NODE_LIST[i]
                if nodeData['nodeType'] == 'Line' or nodeData['nodeType'] == 'Btn':
                    tempIndex += 1
                if i == virtualIndex:
                    return tempIndex

    def selectEditItem(self, index=None, update=True):
        # global NOW_SELECT_INDEX
        needUpdate = update and GlobalValue.NOW_SELECT_INDEX != index
        GlobalValue.NOW_SELECT_INDEX = index
        if needUpdate:
            self.updateTlNode()

    def onKeyboardArrowClick(self, arrow):
        if arrow == ArrowDirEnum.Up:
            if GlobalValue.NOW_SELECT_INDEX != None and GlobalValue.UI_MODE == UiModeEnum.Edit:
                self.moveItem(GlobalValue.NOW_SELECT_INDEX, -1)
        elif arrow == ArrowDirEnum.Down:
            if GlobalValue.NOW_SELECT_INDEX != None and GlobalValue.UI_MODE == UiModeEnum.Edit:
                self.moveItem(GlobalValue.NOW_SELECT_INDEX, 1)
        elif arrow == ArrowDirEnum.Left:
            if GlobalValue.NOW_SELECT_INDEX != None and GlobalValue.UI_MODE == UiModeEnum.Edit:
                self.moveItem(GlobalValue.NOW_SELECT_INDEX, -1)
        elif arrow == ArrowDirEnum.Right:
            if GlobalValue.NOW_SELECT_INDEX != None and GlobalValue.UI_MODE == UiModeEnum.Edit:
                self.moveItem(GlobalValue.NOW_SELECT_INDEX, 1)

    def onKeyBoardDeleteClick(self, event):
        # global NOW_SELECT_INDEX
        if GlobalValue.UI_MODE == UiModeEnum.Edit and GlobalValue.NOW_SELECT_INDEX != None:
            selectIndex = GlobalValue.NOW_SELECT_INDEX
            GlobalValue.NOW_SELECT_INDEX = None
            self.saveNodeData(selectIndex, None, SaveNodeDataOper.Delete)

    def onFocus(self, event):
        if self.listLineNodeView:
            try:
                self.listLineNodeView.destroy()
            except Exception as e:
                # raise e
                pass
            self.listLineNodeView = None

        # global FORCE_SHOW_SELECT
        GlobalValue.FORCE_SHOW_SELECT = False
        if GlobalValue.NOW_SELECT_INDEX != None:
            # py3_common.Logging.debug2('FORCE_SHOW_SELECT', GlobalValue.FORCE_SHOW_SELECT)
            self.refreshNodeByIndex(GlobalValue.NOW_SELECT_INDEX, False, True)

    def jumpToIndex(self, index, yShift=0, value=0):
        return self.virtualListFrame.jumpToIndex(index, yShift, value)

    # 0=顶 1=底
    def jumpTo(self, value=0):
        return self.virtualListFrame.jumpTo(value)

    def jumpWithPageUpDown(self, value):
        return self.virtualListFrame.jumpWithPageUpDown(value)

    # Esc键
    def onKeyBoardEscapeClick(self, event):
        self.initWindow.focus_force()
        if GlobalValue.UI_MODE == UiModeEnum.Edit:
            self.selectUiMode(0)

    # 鼠标中键
    def onMouseButton2Click(self, event):
        self.tkPosX, self.tkPosY = event.x, event.y

    # 鼠标中键拖动
    def onMouseButton2Motion(self, event):
        newX = (event.x - self.tkPosX) + self.initWindow.winfo_x()
        newY = (event.y - self.tkPosY) + self.initWindow.winfo_y()
        self.initWindow.geometry('+%d+%d' % (newX, newY))

    def switchHideTitleBar(self):
        self.isHideTitleBar = not self.isHideTitleBar

        def setAppwindow(root):
            GWL_EXSTYLE=-20
            WS_EX_APPWINDOW=0x00040000
            WS_EX_TOOLWINDOW=0x00000080

            hwnd = windll.user32.GetParent(root.winfo_id())
            style = windll.user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
            style = style & ~WS_EX_TOOLWINDOW
            style = style | WS_EX_APPWINDOW
            res = windll.user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, style)
            # re-assert the new window style
            root.wm_withdraw()
            root.after(1, lambda :root.wm_deiconify())
            root.after(1, lambda :root.focus_force())

        ox, oy = self.initWindow.winfo_x(), self.initWindow.winfo_y()
        nx, ny = (ox + self.frmW) if self.isHideTitleBar else (ox - self.frmW), (oy + self.frmH) if self.isHideTitleBar else (oy - self.frmH)
        self.initWindow.overrideredirect(self.isHideTitleBar)
        if self.isHideTitleBar:
            self.initWindow.after(1, lambda :setAppwindow(self.initWindow))
        self.initWindow.config(menu=self.mbar if not self.isHideTitleBar else '')
        self.initWindow.after(1, lambda :self.initWindow.geometry('+%d+%d' % (nx, ny)))

    def refreshColors(self):
        # print(getColorWithTlKeyAutoDefault(['common', 'bgColor']))
        # windows无效
        # self.mbar.configure(background='black', fg='white', activebackground='#004c99', activeforeground='white')
        fc_ = getColorWithTlKeyAutoDefault
        self.configure(bg=fc_(['common', 'bgColor']))
        configureTkObjectColor(self)
        # self.panelWindow1.configure(bg=fc_(['common', 'bgColor']))
        configureTkObjectColor(self.panelWindow1)
        # self.frameMain.configure(bg=fc_(['common', 'bgColor']))
        configureTkObjectColor(self.frameMain)
        # self.frameMode.configure(bg=fc_(['common', 'bgColor']))
        configureTkObjectColor(self.frameMode)
        # self.frameModeSelectBtn.configure(bg=fc_(['common', 'bgColor']))
        configureTkObjectColor(self.frameModeSelectBtn)
        # self.frameModeLabel.configure(bg=fc_(['common', 'bgColor']), fg=fc_(['common', 'fgColor']))
        configureTkObjectColor(self.frameModeLabel)
        for i in range(0,len(self.tlModeRadiobutton)):
            # self.tlModeRadiobutton[i].configure(bg=fc_(['common', 'bgColor']), fg=fc_(['common', 'fgColor']), selectcolor=fc_(['common', 'bgColor']), activebackground=fc_(['common', 'bgColor']), activeforeground=fc_(['common', 'fgColor']))
            configureTkObjectColor(self.tlModeRadiobutton[i])

        self.virtualListFrame.configure(bg=fc_(['common', 'canvasBgColor']))
        self.virtualListFrame.virtualListCanvas.configure(bg=fc_(['common', 'canvasBgColor']))
        self.virtualListFrame.virtualListCanvas.scrollFrame.configure(bg=fc_(['common', 'canvasBgColor']))
        # self.virtualListFrame.canvasVsb.configure(bg='blue')

        tlStyleKeyMark = list()
        def fc_mark(tlKey):
            tlStyleKeyMark.append(tlKey)
            return fc_(tlKey)

        style = ttk.Style()
        # py3_common.Logging.debug(ttk.Style.__init__.__code__.co_varnames)
        # py3_common.Logging.debug(style.configure.__code__.co_varnames)
        # py3_common.Logging.debug('theme_names', style.theme_names())
        # ('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
        # style.theme_use('clam')
        style.theme_use('default')
        style.configure("Vertical.TScrollbar", gripcount=0, borderwidth=0, arrowsize=16,
                        # sliderrelief='flat',
                        background=fc_mark(['common', 'ttkScrollbar', 'background', 'normal']),
                        # foreground='yellow',
                        # darkcolor="yellow",
                        # lightcolor="yellow",
                        troughcolor=fc_mark(['common', 'ttkScrollbar', 'troughcolor']),
                        # bordercolor="yellow",
                        # arrowcolor=fc_mark(['common', 'ttkScrollbar', 'arrowcolor', 'normal']))
                        arrowcolor=fc_mark(['common', 'fgColor']))
        style.map('Vertical.TScrollbar',
                    background=[('active', fc_mark(['common', 'ttkScrollbar', 'background', 'active'])),
                                ('disabled', fc_mark(['common', 'ttkScrollbar', 'background', 'disabled']))],
                                # ('readonly', fc_mark(['common', 'ttkScrollbar', 'background', 'disabled']))],
                    # foreground=[('active', 'yellow'), ('disabled', 'yellow')],
                    arrowcolor=[('disabled', fc_mark(['common', 'ttkScrollbar', 'arrowcolor', 'disabled']))])
        style.configure("Horizontal.TScrollbar", gripcount=0, borderwidth=0, arrowsize=16,
                        # sliderrelief='flat',
                        background=fc_mark(['common', 'ttkScrollbar', 'background', 'normal']),
                        # foreground='yellow',
                        # darkcolor="yellow",
                        # lightcolor="yellow",
                        troughcolor=fc_mark(['common', 'ttkScrollbar', 'troughcolor']),
                        # bordercolor="yellow",
                        # arrowcolor=fc_mark(['common', 'ttkScrollbar', 'arrowcolor', 'normal']))
                        arrowcolor=fc_mark(['common', 'fgColor']))
        style.map('Horizontal.TScrollbar',
                    background=[('active', fc_mark(['common', 'ttkScrollbar', 'background', 'active'])),
                                ('disabled', fc_mark(['common', 'ttkScrollbar', 'background', 'disabled']))],
                                # ('readonly', fc_mark(['common', 'ttkScrollbar', 'background', 'disabled']))],
                    # foreground=[('active', 'yellow'), ('disabled', 'yellow')],
                    arrowcolor=[('disabled', fc_mark(['common', 'ttkScrollbar', 'arrowcolor', 'disabled']))])
        style.configure("TCombobox", gripcount=0, borderwidth=1, arrowsize=16, selectborderwidth=0,
                        # sliderrelief='flat',
                        # background=fc_mark(['common', 'ttkCombobox', 'background', 'normal']),
                        background=fc_mark(['common', 'bgColor']),
                        # foreground=fc_mark(['common', 'ttkCombobox', 'foreground', 'normal']),
                        foreground=fc_mark(['common', 'fgColor']),
                        # fieldbackground=fc_mark(['common', 'ttkCombobox', 'fieldbackground', 'normal']),
                        fieldbackground=fc_mark(['common', 'tkEntry', 'bgColor']),
                        # darkcolor="yellow",
                        # lightcolor="yellow",
                        troughcolor=fc_mark(['common', 'ttkCombobox', 'troughcolor']),
                        # bordercolor="yellow",
                        # arrowcolor=fc_mark(['common', 'ttkCombobox', 'arrowcolor', 'normal']))
                        arrowcolor=fc_mark(['common', 'fgColor']),
                        selectbackground=fc_mark(['common', 'tkEntry', 'selectBgColor']),
                        selectforeground=fc_mark(['common', 'tkEntry', 'selectFgColor'])
                        # selectforeground=fc_mark(['common', 'ttkCombobox', 'selectforeground']),
                        # insertcolor=fc_mark(['common', 'ttkCombobox', 'insertcolor'])
                        )
        self.initWindow.option_add('*TCombobox*Listbox*Background', fc_mark(['common', 'tkEntry', 'bgColor']))
        self.initWindow.option_add('*TCombobox*Listbox*Foreground', fc_mark(['common', 'fgColor']))
        self.initWindow.option_add('*TCombobox*Listbox*selectBackground', fc_mark(['common', 'tkEntry', 'selectBgColor']))
        self.initWindow.option_add('*TCombobox*Listbox*selectForeground', fc_mark(['common', 'tkEntry', 'selectFgColor']))
        style.map('TCombobox',
                    background=[('active', fc_mark(['common', 'ttkScrollbar', 'background', 'active'])),
                                ('disabled', fc_mark(['common', 'ttkCombobox', 'background', 'disabled'])),
                                # ('readonly', fc_mark(['common', 'ttkCombobox', 'background', 'readonly']))],
                                ('readonly', fc_mark(['common', 'bgColor']))],
                    foreground=[('active', fc_mark(['common', 'ttkCombobox', 'foreground', 'active'])),
                                ('disabled', fc_mark(['common', 'ttkCombobox', 'foreground', 'disabled'])),
                                # ('readonly', fc_mark(['common', 'ttkCombobox', 'foreground', 'readonly']))],
                                ('readonly', fc_mark(['common', 'fgColor']))],
                    fieldbackground=[('active', fc_mark(['common', 'tkEntry', 'bgColor'])),
                                ('disabled', fc_mark(['common', 'tkEntry', 'disabledBgColor'])),
                                # ('readonly', fc_mark(['common', 'ttkCombobox', 'fieldbackground', 'readonly']))],
                                ('readonly', fc_mark(['common', 'tkEntry', 'bgColor']))],
                    arrowcolor=[('disabled', fc_mark(['common', 'ttkScrollbar', 'arrowcolor', 'disabled']))])

        isAllDefault = True
        for k in tlStyleKeyMark:
            rgbCn = tuple((c//256 for c in self.initWindow.winfo_rgb(getColorWithTlKeyAutoDefault(k))))
            rgbCd = tuple((c//256 for c in self.initWindow.winfo_rgb(getColorWithTlKey(k, True, StyleEnum.Default))))
            if rgbCn[0] != rgbCd[0] or rgbCn[1] != rgbCd[1] or rgbCn[2] != rgbCd[2]:
                isAllDefault = False
                break
        if isAllDefault:
            style.theme_use('vista')

    # 刷新选项
    def refreshOptions(self):
        # 全局执行前询问
        for typeStr in self.tmIsAskBeforeExecuting:
            self.tmIsAskBeforeExecuting[typeStr].set(1 if getOptionAskBeforeExecuting(typeStr) else 0)
        self.isDisableRightClickEdit.set(1 if GlobalValue.DISABLE_RCLICK_EDIT_NODE else 0)
        self.initWindow.attributes("-alpha", GlobalValue.WINDOW_ALPHA/100.0)

    def onEventSettingColorChange(self):
        self.refreshColors()

    def onEventSettingOptionsChange(self):
        self.refreshOptions()


    # -----------------------------数据处理-----------------------------
    # 保存单个节点数据
    def saveNodeData(self, index, nodeData, oper=SaveNodeDataOper.Edit):
        # global TEMP_NODE_LIST
        isChange = False
        if oper == SaveNodeDataOper.Insert:
            GlobalValue.TEMP_NODE_LIST.insert(index, nodeData)
            isChange = True
        elif oper == SaveNodeDataOper.Edit:
            if len(GlobalValue.TEMP_NODE_LIST) > index:
                GlobalValue.TEMP_NODE_LIST[index] = nodeData
                isChange = True
        elif oper == SaveNodeDataOper.Delete:
            if len(GlobalValue.TEMP_NODE_LIST) > index:
                addDeletedNodeBackup(GlobalValue.TEMP_NODE_LIST[index])
                del GlobalValue.TEMP_NODE_LIST[index]
                isChange = True
        if isChange:
            self.saveTlNodeData()
            self.updateTlNode()

    # 保存全部节点数据
    def saveTlNodeData(self):
        if not os.path.isfile(GlobalValue.NODES_CONFIG_JSON_PATH):
            py3_common.Logging.info(u'没有找到配置json，初始化')
            createNodesConfigJson()
        else:
            dumpNodesConfigList()




    # -----------------------------测试-----------------------------
    def on_frame_t1_click(self, event):
        py3_common.Logging.debug("11111")
        py3_common.Logging.debug(event)

    def on_frame_t2_click(self, event):
        py3_common.Logging.debug("22222")
        py3_common.Logging.debug(event)

    def test_create_nodes(self):
        tlData = list()
        tlData.append({
            'nodeType':'Line',
            'text':'测试'
        })
        # for x in range(0,1):
        #     tlData.append({
        #         'nodeType':'Line',
        #         'text':'测试'
        #     })
        # tlData.append({
        #     'nodeType':'Btn',
        #     # 'width':100,
        #     # 'height':100,
        #     # 'bgColor':'white',
        #     'typeStr':'folder',
        #     'btnText':'测试'
        # })
        for x in range(0,2000):
            # data = {
            #     'nodeType':'Btn',
            #     # 'width':100,
            #     # 'height':100,
            #     # 'bgColor':'white',
            #     # 'typeStr':'folder',
            #     # 'typeStr':'exe',
            #     'typeStr':'cmd',
            #     'useDrop':True,
            #     'btnText':'测试' + str(x),
            #     'folderPath':'.',
            #     'exePath':'D:/Beyond Compare 4/BCompare.exe',
            #     # 'exePath':'F:/src/branch/lietianxiaQuick3_trunk_black_bt/run_ui2res.bat',
            #     'command':'python %p0 -p %0 -i 2',
            #     # 'command':'python %p -p %0 -i 0',
            #     # 'filePath':u'E:/记录/py/备份/test_svn.py'
            #     'tlFilePath':[u'E:/记录/py/备份/json_helper.py']
            #     # 'filePath':u'E:/sdk-ios/pytest/test14/script/test_svn.py'
            # }
            data = {'nodeType':'Create'}
            data = self.convertNodeArgs(data)
            tlData.append(data)
        # self.create_nodes(tlData)
        self.virtualListFrame.setTlData(tlData)

    # 测试报错
    def menuTestShowError(self):
        # py3_common.Logging.error('测试')
        temp = 1234
        temp2 = '' + temp






    # 画布鼠标滚轮监听
    # 绑定
    def bindCanvasMousewheel(self, event):
        if platform == "linux" or platform == "linux2":
            self.canvas.bind_all("<Button-4>", fp(self.onCanvasMousewheel, scroll=-1))
            self.canvas.bind_all("<Button-5>", fp(self.onCanvasMousewheel, scroll=1))
        else:
            # <MouseWheel>
            # <Control-MouseWheel>
            # <Shift-MouseWheel>
            self.canvas.bind_all("<MouseWheel>", self.onCanvasMousewheel)
            # self.canvas.bind_all("<Control-MouseWheel>", self.onCanvasCtrlMousewheel)
            # self.canvas.bind_all("<Shift-MouseWheel>", self.onCanvasShiftMousewheel)

    # 解绑
    def unbindCanvasMousewheel(self, event):
        if platform == "linux" or platform == "linux2":
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        else:
            self.canvas.unbind_all("<MouseWheel>")
            # self.canvas.unbind_all("<Control-MouseWheel>")
            # self.canvas.unbind_all("<Shift-MouseWheel>")

    # 响应滚动(滚轮)
    def onCanvasMousewheel(self, event):
        # //整除
        delta = (event.delta // 120)
        # mac有点不一样
        if platform == 'darwin':
            delta = event.delta
        self.canvas.yview_scroll(-1 * delta, "units")

    # 响应滚动(shift+滚轮)
    def onCanvasShiftMousewheel(self, event):
        # self.canvas.xview_scroll(-1 * (event.delta // 120), "units")
        pass

    # # 响应滚动(ctrl+滚轮)
    # def onCanvasCtrlMousewheel(self, event):
    #     # print(event.delta // 120)
    #     # print(event.delta)
    #     # print(platform)

    #     if self.tl_frame:
    #         # mac有点不一样
    #         delta = (event.delta // 120)
    #         if platform == 'darwin':
    #             delta = event.delta
    #         global FRAME_SCALE
    #         scale = FRAME_SCALE + delta*(FRAME_SCALE_MAX-FRAME_SCALE_MIN)/10
    #         scale = max(min(scale, FRAME_SCALE_MAX), FRAME_SCALE_MIN)
    #         FRAME_SCALE = scale
    #         # self.refresh_nodes_scale()
    #         # self.after(len(self.tl_frame)+ADD_DELAY, self.refresh_nodes_pos)



    # 路径标准化
    def pathRegulate(self, path):
        path = path.replace('\\', '/')
        return path








def gui_start():
    # initWindow = Tk()              #实例化出一个父窗口
    # ZMJ_PORTAL = MainGui(initWindow)
    # # 设置根窗口默认属性
    # ZMJ_PORTAL.setInitWindow()

    # initWindow.mainloop()          #父窗口进入事件循环，可以理解为保持窗口运行，否则界面不展示

    initWindow = Tk()
    # global INIT_WINDOW
    # INIT_WINDOW = initWindow
    GlobalValue.INIT_WINDOW = initWindow
    # initWindow.configure(bg='blue')
    # initWindow['bg'] = 'blue'


    tkFont = font.nametofont("TkDefaultFont")
    print('tkFont',tkFont.actual())
    # global DEFAULT_TK_FONT_SIZE
    # DEFAULT_TK_FONT_SIZE = tkFont.actual()['size']
    GlobalValue.DEFAULT_TK_FONT_SIZE = tkFont.actual()['size']

    # GlobalValue.UI_MODE = UI_MODE

    # global pixelVirtual
    # pixelVirtual = PhotoImage(width=1, height=1)

    myGuiProgram = MainGui(initWindow)

    tkCenter(initWindow)
    # 弹出初始化错误提示
    showTlInitErrorMsg()

    initWindow.mainloop()

    os._exit(0)


gui_start()
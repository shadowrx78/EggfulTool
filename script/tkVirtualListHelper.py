#! python3
# -*- coding: utf-8 -*-

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter.messagebox import showerror
import os, re
import hashlib
import time

import random
import json
import math
import ctypes
from collections import OrderedDict

from sys import platform

# import ccbparser
# import plistlib


###########################
# TK虚拟列表
###########################



# 彩色输出
STD_OUTPUT_HANDLE = -11
std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
'''Logging class for log manager'''
class Logging:
    # Windows CMD命令行 字体颜色定义 text colors
    FOREGROUND_BLACK = 0x00 # black.
    FOREGROUND_DARKBLUE = 0x01 # dark blue.
    FOREGROUND_DARKGREEN = 0x02 # dark green.
    FOREGROUND_DARKSKYBLUE = 0x03 # dark skyblue.
    FOREGROUND_DARKRED = 0x04 # dark red.
    FOREGROUND_DARKMAGENTA = 0x05 # dark magenta.
    FOREGROUND_DARKYELLOW = 0x06 # dark yellow.
    FOREGROUND_DARKWHITE = 0x07 # dark white.
    FOREGROUND_DARKGRAY = 0x08 # dark gray.
    FOREGROUND_BLUE = 0x09 # blue.
    FOREGROUND_GREEN = 0x0a # green.
    FOREGROUND_SKYBLUE = 0x0b # skyblue.
    FOREGROUND_RED = 0x0c # red.
    FOREGROUND_MAGENTA = 0x0d # magenta.    品红 偏紫色
    FOREGROUND_YELLOW = 0x0e # yellow.
    FOREGROUND_WHITE = 0x0f # white.
     
    # Windows CMD命令行 背景颜色定义 background colors
    BACKGROUND_BLUE = 0x10 # dark blue.
    BACKGROUND_GREEN = 0x20 # dark green.
    BACKGROUND_DARKSKYBLUE = 0x30 # dark skyblue.
    BACKGROUND_DARKRED = 0x40 # dark red.
    BACKGROUND_DARKMAGENTA = 0x50 # dark magenta.
    BACKGROUND_DARKYELLOW = 0x60 # dark yellow.
    BACKGROUND_DARKWHITE = 0x70 # dark white.
    BACKGROUND_DARKGRAY = 0x80 # dark gray.
    BACKGROUND_BLUE = 0x90 # blue.
    BACKGROUND_GREEN = 0xa0 # green.
    BACKGROUND_SKYBLUE = 0xb0 # skyblue.
    BACKGROUND_RED = 0xc0 # red.
    BACKGROUND_MAGENTA = 0xd0 # magenta.
    BACKGROUND_YELLOW = 0xe0 # yellow.
    BACKGROUND_WHITE = 0xf0 # white.


    # Logging.log(s, color=Logging.FOREGROUND_BLACK | Logging.BACKGROUND_WHITE)
    @staticmethod
    def log(*s, color=FOREGROUND_DARKWHITE):
        Logging.set_cmd_text_color(color)
        print(*s)
        Logging.reset_color()

    @staticmethod
    def debug(*s):
        Logging.log(*s, color=Logging.FOREGROUND_MAGENTA)

    @staticmethod
    def info(*s):
        Logging.log(*s, color=Logging.FOREGROUND_GREEN)

    @staticmethod
    def warning(*s):
        Logging.log(*s, color=Logging.FOREGROUND_YELLOW)

    @staticmethod
    def error(*s):
        Logging.log(*s, color=Logging.FOREGROUND_RED)

    @staticmethod
    def set_cmd_text_color(color, handle=std_out_handle):
        Bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
        return 

    @staticmethod
    def reset_color():
        # Logging.set_cmd_text_color(Logging.RED | Logging.GREEN | Logging.BLUE)
        Logging.set_cmd_text_color(Logging.FOREGROUND_DARKWHITE)


    # 测试用
    @staticmethod
    def debug2(*s):
        Logging.log(*s, color=Logging.FOREGROUND_SKYBLUE)

    @staticmethod
    def debug3(*s):
        Logging.log(*s, color=Logging.FOREGROUND_BLUE|Logging.BACKGROUND_YELLOW)





# 读取json到list
def loadJsonToList(path, ignoreLog=False, isOrdered=True):
    if not os.path.isfile(path):
        if not ignoreLog:
            Logging.error("不存在文件:%s" % path)
        return False

    _config = open(path,'r',encoding='UTF-8')
    try:
        fileContent = _config.read()
    finally:
        _config.close()
    config_List = None
    try:
        if isOrdered:
            config_List = json.loads(fileContent, object_pairs_hook=OrderedDict)
        else:
            config_List = json.loads(fileContent)
    except json.JSONDecodeError:
        # raise e
        pass
    return config_List


# 将list写入json
def dumpJsonFromList(path, config_List, indent=None, sort_keys=False, print_dump_path=True):
    if not config_List or not path:
        return False

    with open(path,"wb") as _config:
        content = json.dumps(config_List, ensure_ascii=False, indent=indent, sort_keys=sort_keys)
        try:
            _config.write(content.encode('utf-8'))
        finally:
            _config.close()
        if print_dump_path:
            Logging.info("写入json:%s" % path)
        return True
    return False


def try_decode_str(tryStr):
    if not isinstance(tryStr, unicode):
        tl_code = ['utf-8', 'ascii', 'gbk']
        decode_suc = False
        decode_str = None
        for code in tl_code:
            if not decode_suc:
                try:
                    decode_str = tryStr.decode(code)
                    decode_suc = True
                except Exception as e:
                    # raise e
                    pass

        if decode_suc and decode_str != None:
            tryStr = decode_str
    return tryStr


# def showtime(f, sub_f, name):
#     start_time = time.time()
#     f(sub_f)
#     print("{} time: {:.4f}s".format(name, time.time() - start_time))

def showtime(name, start_time=None, color=Logging.FOREGROUND_DARKWHITE):
    now_time = time.time()
    if start_time != None:
        Logging.log("[{}] nowTime: {:.4f}s, startTime: {:.4f}s, timeShift: {:.4f}s".format(name, now_time, start_time, now_time - start_time), color=color)
    else:
        Logging.log("[{}] nowTime: {:.4f}s".format(name, now_time), color=color)
    return now_time






BG_COLOR = 'gray94'

# 节点父类
class BaseNode(Frame):
    """
    节点父类
    参数:
    args:
        nodeType:string 节点类型标记,默认'Base'
        bgColor:string 节点背景颜色
    """
    def __init__(self, initWindow, args=None, autoInit=True, **kwargs):
        super(BaseNode, self).__init__(initWindow, takefocus=0, **kwargs)
        self.args = args if args != None else dict()
        self.initWindow = initWindow
        self.grid_propagate(False)   #关闭布局几何传播
        self.propagate(False)   #关闭布局几何传播
        # 实际大小设置有时间差 作为记录
        self.width_ = 0
        self.height_ = 0
        # 位置设置没时间差 独立出来方便扩展
        self.x_ = 0
        self.y_ = 0
        self.hasInitSize = False
        self.hasInitPos = False
        self.visible = True

        self.exData = dict()

        self.tlConfigureCallback = list()

        if autoInit:
            self.initUi()

    def initUi(self):
        self.bind('<Configure>', self.onConfigure)
        # self.updateArgs(self.args)

    def updateArgs(self, args=dict()):
        self.args = args
        if 'bgColor' in args:
            self.changeBg(args['bgColor'])

    def refresh(self):
        self.updateArgs(self.args)

    # 颜色
    def changeBg(self, bg=None):
        if not bg:
            bg = BG_COLOR
        self.configure(bg=bg)

    # 大小
    def getContentSize(self):
        # return self.winfo_width(), self.winfo_height()
        return self.width_, self.height_

    def setContentSize(self, width=None, height=None):
        if width == None and height == None:
            return
        w,h = self.getContentSize()
        if width == w and height == h and self.hasInitSize:
            return
        self.width_ = width if width != None else w
        self.height_ = height if height != None else h
        self.configure(width=self.width_, height=self.height_)
        self.hasInitSize = True

    # 位置
    def getPos(self):
        return self.x_, self.y_

    def setPos(self, x=None, y=None):
        if x == None and y == None:
            return
        x_, y_ = self.getPos()
        if x == x_ and y == y_ and self.hasInitPos and self.visible:
            return
        self.x_ = x if x != None else x_
        self.y_ = y if y != None else y_
        self.place(x=self.x_, y=self.y_)
        self.hasInitPos = True
        self.visible = True

    # 属性改变回调
    def onConfigure(self, event):
        # print(event.x, event.y, event.width, event.height)
        tlRemoveIdx = list()
        for i in range(0,len(self.tlConfigureCallback)):
            if self.tlConfigureCallback[i](event):    #调用回调 返回true则清除
                tlRemoveIdx.append(i)
        for i in range(len(tlRemoveIdx), 0, -1):  #清除完成的回调
            self.tlConfigureCallback.pop(tlRemoveIdx[i-1])

    # 节点类型
    def getType(self):
        return self.args['nodeType'] if 'nodeType' in self.args else 'Base'

    # 获取数据
    def getArgs(self):
        return self.args

    # 添加属性改变回调 外部 单次
    def addConfigureCallback(self, callback):
        self.tlConfigureCallback.append(callback)

    # 获取默认大小
    def getDefaultSize(self):
        # defaultSize = TM_NODE_TYPE[self.getType()]['defaultSize']
        # return defaultSize['width'], defaultSize['height']
        return 100, 100

    # 设置可见
    def setVisible(self, visible):
        if visible:
            if not self.visible:
                x, y = self.getPos()
                self.place(x=x, y=y)
                self.visible = True
        else:
            self.place_forget()
            self.visible = False

    # 额外数据 标记用
    def setExData(self, exData, update=True):
        if update:
            for k in exData:
                self.exData[k] = exData[k]
        else:
            self.exData = exData

    def getExData(self, key=None):
        if key == None:
            return self.exData
        else:
            if key in self.exData:
                return self.exData[key]
        return None

    def refreshEx(self):
        self.setExData(self.exData, False)



# tk的画布宽高限制在30000像素左右，以后优化，思路是滚动条连接到自定义函数让画布循环滚动
class VirtualListCanvas(Canvas):
    """
    虚拟列表画布
    参数:
    args:
        createNodeFun:function(self, data, scrollFrame, autoInit=True) 创建节点方法,节点必须继承BaseNode（必须）
        getNodeSizeWithDataFun:function(data) 根据数据获取节点大小的方法（必须）
        onScrollFrameConfigureFun:function(configureData) 滑动Frame属性改变回调（可选）
            configureData:{'changeField':set('width','height','x','y'), 'event':event}
        padding:{'w':number, 'h':number} 间隔（可选）
        isBindMouseWheel:bool 是否绑定鼠标滚轮滚动（可选）
    kwargs:tkinter画布初始化参数
    """
    def __init__(self, initWindow, args, **kwargs):
        super(VirtualListCanvas, self).__init__(initWindow, takefocus=0, **kwargs)
        self.args = args
        self.createNodeFun = args['createNodeFun'] if 'createNodeFun' in args else None
        self.getNodeSizeWithDataFun = args['getNodeSizeWithDataFun'] if 'getNodeSizeWithDataFun' in args else None
        self.onScrollFrameConfigureFun = args['onScrollFrameConfigureFun'] if 'onScrollFrameConfigureFun' in args else None
        self.padding = args['padding'] if 'padding' in args and isinstance(args['padding'], dict) else {'w':0, 'h':0}
        if not 'w' in self.padding:
            self.padding['w'] = 0
        if not 'h' in self.padding:
            self.padding['h'] = 0

        self.initUi()

    def initUi(self):
        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)
        self.scrollFrame = Frame(self, width=self.winfo_width(), height=10)
        self.create_window((0, 0), window=self.scrollFrame, anchor="nw")

        self.bind('<Configure>', self.onCanvasConfigure)
        self.scrollFrame.bind('<Configure>', self.onScrollFrameConfigure)

        # 鼠标滚动相关
        if 'isBindMouseWheel' in self.args and self.args['isBindMouseWheel']:
            self.bind('<Enter>', self.bindCanvasMousewheel)
            self.bind('<Leave>', self.unbindCanvasMousewheel)


        # ---------缓存初始化---------
        self.realScrollFrameHeight = None    #记录节点布局实际高度
        self.tmOldCanvasSize = {'width':0, 'height':0}   #记录画布大小
        self.tmOldScrollFramePosSize = {'x':0, 'y':0, 'width':0, 'height':0}     ##记录scrollFrame大小
        self.nodePool = list()     #节点池
        self.tlNodeData = None     #节点数据
        self.tmVisualNode = dict()     #当前可视节点
        self.refreshPosLock = False
        self.refreshPosCount = 0

    # 画布属性改变
    def onCanvasConfigure(self, event):
        # start_time = None
        # start_time = showtime('onCanvasConfigure', start_time, color=Logging.FOREGROUND_DARKYELLOW)
        self.scrollFrame.configure(width=self.winfo_width()-4)
        # self.refreshListView()
        if hasattr(event, 'height') and self.tmOldCanvasSize['height'] != event.height:
            if self.realScrollFrameHeight:
                # scrollFrame高度太小会可以上下滚
                height_ = max(self.realScrollFrameHeight, self.winfo_height()-4)
                self.scrollFrame.configure(height=height_)
            self.refreshListView()
        if hasattr(event, 'width'):
            self.tmOldCanvasSize['width'] = event.width
        if hasattr(event, 'height'):
            self.tmOldCanvasSize['height'] = event.height
        # start_time = showtime('onCanvasConfigure', start_time, color=Logging.FOREGROUND_DARKYELLOW)

    # 画布内节点属性改变
    def onScrollFrameConfigure(self, event):
        # start_time = None
        # start_time = showtime('onScrollFrameConfigure', start_time, color=Logging.FOREGROUND_DARKMAGENTA)
        self.configure(scrollregion=(0,0,self.scrollFrame.winfo_width(),self.scrollFrame.winfo_height()))

        if hasattr(event, 'width') and self.tmOldScrollFramePosSize['width'] != event.width:
            # self.refresh_line_nodes_size()
            self.refreshListView()
        elif hasattr(event, 'y') and self.tmOldScrollFramePosSize['y'] != event.y:
            self.refreshListView()

        # 外部回调
        if self.onScrollFrameConfigureFun:
            tempT = dict()
            tempT['changeField'] = set()
            tempT['event'] = event
            if hasattr(event, 'width') and self.tmOldScrollFramePosSize['width'] != event.width:
                tempT['changeField'].add('width')
            if hasattr(event, 'height') and self.tmOldScrollFramePosSize['height'] != event.height:
                tempT['changeField'].add('height')
            if hasattr(event, 'x') and self.tmOldScrollFramePosSize['x'] != event.x:
                tempT['changeField'].add('x')
            if hasattr(event, 'y') and self.tmOldScrollFramePosSize['y'] != event.y:
                tempT['changeField'].add('y')
            self.onScrollFrameConfigureFun(tempT)

        if hasattr(event, 'width'):
            self.tmOldScrollFramePosSize['width'] = event.width
        if hasattr(event, 'height'):
            self.tmOldScrollFramePosSize['height'] = event.height
        if hasattr(event, 'x'):
            self.tmOldScrollFramePosSize['x'] = event.x
        if hasattr(event, 'y'):
            self.tmOldScrollFramePosSize['y'] = event.y
        # start_time = showtime('onScrollFrameConfigure', start_time, color=Logging.FOREGROUND_DARKMAGENTA)


    def setTlData(self, tlData):
        # # 序列化
        # for i in range(0,len(tlData)):
        #     tlData[i]['data_index'] = i
        self.tlNodeData = tlData
        self.refreshListView()

    def getTlData(self):
        return self.tlNodeData

    def getNodeByIndex(self, index):
        for uid in self.tmVisualNode:
            node = self.tmVisualNode[uid]
            if node.getExData('index') == index:
                return node

    def refreshNodeByIndex(self, index, ui=True, ex=False):
        node = self.getNodeByIndex(index)
        if node:
            if ui:
                node.refresh()
            if ex:
                node.refreshEx()


    # 排版
    def refreshListView(self):
        # Logging.error('==========================')
        # Logging.error(self.refreshPosLock, self.refreshPosCount)
        if self.refreshPosLock:
            self.refreshPosCount += 1
            # if dataRefresh:
            #     self.delayDataRefresh = True
            return
        if hasattr(self, 'tlNodeData') and self.tlNodeData != None:
            self.refreshPosLock = True
            paddingW = self.padding['w']
            paddingH = self.padding['h']

            # 只取可视
            # Logging.log('---------------------')
            # start_time = None
            # start_time = showtime('getOrCreateNode', start_time, color=Logging.FOREGROUND_DARKYELLOW)
            tlLineNodeData, nowY = self._getTlLineNodeDataVisual(paddingW, paddingH)
            # Logging.debug2(tlLineNodeData)


            oldTmVisNode = self.tmVisualNode
            self.tmVisualNode = dict()

            tmNodeData = dict()
            for tlNodeData in tlLineNodeData:
                for nodeData in tlNodeData:
                    tmNodeData[nodeData['index']] = nodeData

            tmNodeDataIndexFound = set()
            # 原有的保留可见
            for uid in oldTmVisNode:
                node = oldTmVisNode[uid]
                if node.getExData('index') in tmNodeData:
                    nodeData = tmNodeData[node.getExData('index')]
                    # 节点类型相同才保留
                    if (nodeData['data']['nodeType'] if 'nodeType' in nodeData['data'] else 'Base') == node.getType():
                        self.tmVisualNode[uid] = node
                        node.updateArgs(nodeData['data'])
                        node.setPos(nodeData['x'], nodeData['y'])
                        node.setExData({'index':node.getExData('index'), 'nodeData':nodeData})   #跟新建的节点保持相同行为
                        tmNodeDataIndexFound.add(node.getExData('index'))

            for index in tmNodeData:
                if not index in tmNodeDataIndexFound:
                    nodeData = tmNodeData[index]
                    node = self.getOrCreateNode(nodeData['data'])
                    node.setExData({'index':index, 'nodeData':nodeData})
                    node.setPos(nodeData['x'], nodeData['y'])
                    self.tmVisualNode[node.getExData('uid')] = node


            self.flyNoVisualNode()

            def callback():
                # nonlocal padding
                if self:
                    self.realScrollFrameHeight = math.ceil(nowY + paddingH)
                    # scrollFrame高度太小会可以上下滚
                    height_ = max(self.realScrollFrameHeight, self.winfo_height()-4)
                    self.scrollFrame.configure(height=height_)
            # self.after(len(tlLineNodeData)+ADD_DELAY, callback)
            callback()
            # start_time = showtime('getOrCreateNode', start_time, color=Logging.FOREGROUND_DARKYELLOW)
            self.refreshPosLock = False
            if self.refreshPosCount > 0:
                # delayDataRefresh = self.delayDataRefresh
                # self.delayDataRefresh = False
                self.refreshPosCount = 0
                self.refreshListView()
                self.refreshPosCount = 0
            self.refreshPosCount = 0

    # 算出每行排列节点的index
    def _getTlLineNodeData(self, paddingW=0, paddingH=0):
        # 用数据算
        if hasattr(self, 'tlNodeData') and self.tlNodeData != None:
            tlLineNodeData = list()  #记录每行排列的节点index
            nowY = 0
            if len(self.tlNodeData) > 0:
                # 分配行
                width_max = self.scrollFrame.winfo_width()
                nowLineWidth = 0
                tempT = list()     #当前行
                for index in range(0,len(self.tlNodeData)):
                    data = self.tlNodeData[index]  #节点数据
                    nodeW, nodeH = self._getNodeSizeWithData(data)
                    newTempT = None   #新行
                    lineNodeData = {'index':index, 'width':nodeW, 'height':nodeH, 'data':data}

                    newWidth = nowLineWidth + nodeW + (paddingW if len(tempT) > 0 else 0)
                    if newWidth > width_max and len(tempT) > 0:     #超过宽度换行
                        newTempT = list()
                        newTempT.append(lineNodeData)
                        nowLineWidth = nodeW
                    else:
                        tempT.append(lineNodeData)
                        nowLineWidth = newWidth

                    if newTempT:  #有新行 之前的记录
                        if tempT and len(tempT) > 0:
                            tlLineNodeData.append(tempT)
                        tempT = newTempT
                if tempT and len(tempT) > 0:
                    tlLineNodeData.append(tempT)

                # 计算坐标
                if tlLineNodeData and len(tlLineNodeData) > 0:
                    for i in range(0, len(tlLineNodeData)):
                        tlData = tlLineNodeData[i]     #1行
                        lineHeight = 0
                        nowX = 0
                        y = (paddingH if i != 0 else 0) + nowY    #第一行不加padding
                        for j in range(0,len(tlData)):
                            data = tlData[j]
                            lineHeight = max(lineHeight, data['height'])  #记录行高
                            x = nowX + (paddingW if j != 0 else 0)
                            nowX = x + data['width']
                            data['x'] = x
                            data['y'] = y
                        nowY = y + lineHeight   #记录

            return tlLineNodeData, nowY

    # 算出每行排列节点的index 只取可见的
    def _getTlLineNodeDataVisual(self, paddingW=0, paddingH=0):
        tlLineNodeData, nowY = self._getTlLineNodeData(paddingW, paddingH)
        tlLineNodeData_ = list()
        visualRange = self.getScrollFrameVisualRange()
        for lineNodeData in tlLineNodeData:
            visible = False
            # print(lineNodeData)
            for nodeData in lineNodeData:
                if self.isInVisualRange(nodeData['x'], nodeData['y'], nodeData['width'], nodeData['height'], visualRange):
                    visible = True
                    break
            # print(visible)
            if visible:
                tlLineNodeData_.append(lineNodeData)
        # print(tlLineNodeData_)
        return tlLineNodeData_, nowY

    # 检测节点是否在可视范围内
    def isNodeInVisualRange(self, node, visualRange=None, allInRange=False):
        x, y = node.getPos()
        w, h = node.getContentSize()

        if not visualRange:
            visualRange = self.getScrollFrameVisualRange()

        return self.isInVisualRange(x, y, w, h, visualRange, allInRange)

    def isIndexInVisualRange(self, index, visualRange=None, allInRange=False, isNow=False):
        if isNow and self.tmVisualNode != None:
            for uid in self.tmVisualNode:
                node = self.tmVisualNode[uid]
                if node.getExData('index') == index:
                    if not allInRange:
                        return True
                    else:
                        nodeData_ = node.getExData('nodeData')
                        if nodeData_:
                            if not visualRange:
                                visualRange = self.getScrollFrameVisualRange()
                            return self.isInVisualRange(nodeData_['x'], nodeData_['y'], nodeData_['width'], nodeData_['height'], visualRange, allInRange)
            return False
        else:
            nodeData_ = self.getNodeDataByIndex(index)
            if not nodeData_:
                return False
            if not visualRange:
                visualRange = self.getScrollFrameVisualRange()
            return self.isInVisualRange(nodeData_['x'], nodeData_['y'], nodeData_['width'], nodeData_['height'], visualRange, allInRange)

    def isInVisualRange(self, x, y, width, height, visualRange=None, allInRange=False):
        if not visualRange:
            visualRange = self.getScrollFrameVisualRange()

        v1 = False
        v2 = False
        v3 = False
        v4 = False
        if not allInRange:
            v1 = y + height >= visualRange['y']
            v2 = y <= visualRange['y'] + visualRange['height']
            v3 = x + width >= visualRange['x']
            v4 = x <= visualRange['x'] + visualRange['width']
        else:
            v1 = y >= visualRange['y']
            v2 = y + height <= visualRange['y'] + visualRange['height']
            v3 = x >= visualRange['x']
            v4 = x + width <= visualRange['x'] + visualRange['width']

        return (v1 and v2 and v3 and v4)

    def getNodeDataByIndex(self, index):
        paddingW = self.padding['w']
        paddingH = self.padding['h']
        tlLineNodeData, nowY = self._getTlLineNodeData(paddingW, paddingH)
        nodeData_ = None
        for tlNodeData in tlLineNodeData:
            for nodeData in tlNodeData:
                if index == nodeData['index']:
                    nodeData_ = nodeData
                    break
            if nodeData_:
                break
        return nodeData_

    # 画布内节点可视范围
    def getScrollFrameVisualRange(self):
        canvasW, canvasH = self.winfo_width(), self.winfo_height()  #画布大小
        # print(canvasW, canvasH)
        # frame位置大小
        scrollFrameX, scrollFrameY, scrollFrameW, scrollFrameH = self.scrollFrame.winfo_x(), self.scrollFrame.winfo_y(), self.scrollFrame.winfo_width(), self.scrollFrame.winfo_height()
        # print(scrollFrameX, scrollFrameY, scrollFrameW, scrollFrameH)
        visualRange = {'x':0, 'y':max(-scrollFrameY, 0), 'width':scrollFrameW, 'height':canvasH-max(scrollFrameY, 0)}
        # print(visualRange)
        return visualRange


    # yShift y方向偏移像素
    # value 0=顶 1=底
    def jumpToIndex(self, index, yShift=0, value=0):
        paddingW = self.padding['w']
        paddingH = self.padding['h']
        tlLineNodeData, nowY = self._getTlLineNodeData(paddingW, paddingH)
        nodeData_ = None
        lineHeight = 0
        for tlNodeData in tlLineNodeData:
            lineHeight = 0
            for nodeData in tlNodeData:
                lineHeight = max(lineHeight, nodeData['height'])
                if index == nodeData['index'] and not nodeData_:
                    nodeData_ = nodeData
            if nodeData_:
                break
        if not nodeData_:
            return False
        canvasH = self.winfo_height()
        scrollFrameH = self.scrollFrame.winfo_height()
        # print(lineHeight, scrollFrameH, canvasH)
        toScrollFrameY = min(max(nodeData_['y']+(-(canvasH-lineHeight)*value)+yShift, 0), scrollFrameH-canvasH)
        self.yview_moveto(float(toScrollFrameY+1)/scrollFrameH)
        return True

    # 根据pos获取最近的index
    # 不是实际距离最近，会按行划分
    # pos是相对画布左上角的xy坐标
    def getNearIndexWithPos(self, pos, visualRange=None):
        if not visualRange:
            visualRange = self.getScrollFrameVisualRange()
        realPos = {'x':pos['x'] + visualRange['x'], 'y':pos['y'] + visualRange['y']}

        paddingW = self.padding['w']
        paddingH = self.padding['h']
        tlLineNodeData, nowY = self._getTlLineNodeData(paddingW, paddingH)
        for i in range(0,len(tlLineNodeData)):
            tlNodeData = tlLineNodeData[i]
            nodeData = tlNodeData[0]
            if nodeData and nodeData['y'] > realPos['y']:
                if i > 0 and i < len(tlLineNodeData):
                    return tlLineNodeData[i-1][0]['index']
                break
        if realPos['y'] <= visualRange['y'] + visualRange['height'] and len(tlLineNodeData) > 0:
            return tlLineNodeData[len(tlLineNodeData)-1][0]['index']
        return None

    # 获取index的节点在可视范围的y偏移
    def getIndexVisualYShift(self, index, visualRange=None):
        if not visualRange:
            visualRange = self.getScrollFrameVisualRange()

        nodeData_ = self.getNodeDataByIndex(index)
        if nodeData_:
            return nodeData_['y'] - visualRange['y']

    def jumpWithYShift(self, yShift):
        scrollFrameX, scrollFrameY, scrollFrameW, scrollFrameH = self.scrollFrame.winfo_x(), self.scrollFrame.winfo_y(), self.scrollFrame.winfo_width(), self.scrollFrame.winfo_height()
        canvasH = self.winfo_height()
        toScrollFrameY = min(max(-scrollFrameY+yShift, 0), scrollFrameH-canvasH)
        self.yview_moveto(float(toScrollFrameY+1)/scrollFrameH)
        return True

    # 0=顶 1=底
    def jumpTo(self, value=0):
        scrollFrameX, scrollFrameY, scrollFrameW, scrollFrameH = self.scrollFrame.winfo_x(), self.scrollFrame.winfo_y(), self.scrollFrame.winfo_width(), self.scrollFrame.winfo_height()
        canvasH = self.winfo_height()
        toScrollFrameY = min(max(round(scrollFrameH*value*1.0), 0), scrollFrameH-canvasH)
        self.yview_moveto(float(toScrollFrameY+1)/scrollFrameH)
        return True

    def jumpWithPageUpDown(self, value):
        scrollFrameX, scrollFrameY, scrollFrameW, scrollFrameH = self.scrollFrame.winfo_x(), self.scrollFrame.winfo_y(), self.scrollFrame.winfo_width(), self.scrollFrame.winfo_height()
        canvasH = self.winfo_height()
        toScrollFrameY = min(max(-scrollFrameY+(canvasH*value), 0), scrollFrameH-canvasH)
        self.yview_moveto(float(toScrollFrameY+1)/scrollFrameH)
        return True


    def getOrCreateNode(self, data=None, autoInit=True):
        if data == None:
            data = dict()
        nodeType = data['nodeType'] if 'nodeType' in data else 'Base'
        node = None
        for node_ in self.nodePool:
            if not node_.getExData('uid') in self.tmVisualNode and node_.getType() == nodeType:
                # 找到
                node = node_
                node.updateArgs(data)
                break
        if node == None:
            # 没找到
            uid = self.nodePool[len(self.nodePool)-1].getExData('uid') if len(self.nodePool) > 0 else 0
            if self.createNodeFun:
                node = self.createNodeFun(data, self.scrollFrame, autoInit)
                if node:
                    node.setExData({'uid':uid + 1})
                    self.nodePool.append(node)

        return node

    # 超出屏幕的飞远点
    def flyNoVisualNode(self):
        # tm_real_index = dict()
        # for k in self.tmVisualNode:
        #     nodeType = self.tmVisualNode[k].getType()
        #     node_id = self.tmVisualNode[k].getExData('id')
        #     if node_id != None:
        #         if not nodeType in tm_real_index:
        #             tm_real_index[nodeType] = dict()
        #         tm_real_index[nodeType][node_id] = True
        # for nodeType in self.tm_frame_pool:
        #     for node in self.tm_frame_pool[nodeType]:
        #         node_id = node.getExData('id')
        #         if node_id != None and (not nodeType in tm_real_index or not node_id in tm_real_index[nodeType]):
        #             node.setPos(-10000, -10000)

        for node in self.nodePool:
            if not node.getExData('uid') in self.tmVisualNode:
                node.setVisible(False)

    def _getNodeSizeWithData(self, data=None):
        if self.getNodeSizeWithDataFun:
            return self.getNodeSizeWithDataFun(data)
        return 0, 0


    # 画布鼠标滚轮监听
    # 绑定
    def bindCanvasMousewheel(self, event):
        if platform == "linux" or platform == "linux2":
            self.bind_all("<Button-4>", fp(self.onCanvasMousewheel, scroll=-1))
            self.bind_all("<Button-5>", fp(self.onCanvasMousewheel, scroll=1))
        else:
            # <MouseWheel>
            # <Control-MouseWheel>
            # <Shift-MouseWheel>
            self.bind_all("<MouseWheel>", self.onCanvasMousewheel)
            # self.bind_all("<Control-MouseWheel>", self.onCanvasCtrlMousewheel)
            # self.bind_all("<Shift-MouseWheel>", self.onCanvasShiftMousewheel)

    # 解绑
    def unbindCanvasMousewheel(self, event):
        if platform == "linux" or platform == "linux2":
            self.unbind_all("<Button-4>")
            self.unbind_all("<Button-5>")
        else:
            self.unbind_all("<MouseWheel>")
            # self.unbind_all("<Control-MouseWheel>")
            # self.unbind_all("<Shift-MouseWheel>")

    # 响应滚动(滚轮)
    def onCanvasMousewheel(self, event):
        # //整除
        delta = (event.delta // 120)
        # mac有点不一样
        if platform == 'darwin':
            delta = event.delta
        self.yview_scroll(-1 * delta, "units")

    # 响应滚动(shift+滚轮)
    def onCanvasShiftMousewheel(self, event):
        # self.xview_scroll(-1 * (event.delta // 120), "units")
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




class VirtualListFrame(Frame):
    """
    虚拟列表
    参数:
    args:
        createNodeFun:function(self, data, scrollFrame, autoInit=True) 创建节点方法,节点必须继承BaseNode（必须）
        getNodeSizeWithDataFun:function(data) 根据数据获取节点大小的方法（必须）
        onScrollFrameConfigureFun:function(configureData) 滑动Frame属性改变回调（可选）
            configureData:{'changeField':set('width','height','x','y'), 'event':event}
        padding:{'w':number, 'h':number} 间隔（可选）
        hasScrollbar:bool 有无滚动条（可选）
        isBindMouseWheel:bool 是否绑定鼠标滚轮滚动（可选）
        canvasKwArgs:dict 画布初始化参数（可选）
    kwargs:tkinter Frame初始化参数
    """
    def __init__(self, initWindow, args, **kwargs):
        super(VirtualListFrame, self).__init__(initWindow, **kwargs)
        self.args = args
        self.initUi()

    def initUi(self):
        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)

        # 画布
        args = self.args
        canvasArgs = dict()
        canvasArgs['createNodeFun'] = args['createNodeFun'] if 'createNodeFun' in args else None
        canvasArgs['getNodeSizeWithDataFun'] = args['getNodeSizeWithDataFun'] if 'getNodeSizeWithDataFun' in args else None
        canvasArgs['onScrollFrameConfigureFun'] = args['onScrollFrameConfigureFun'] if 'onScrollFrameConfigureFun' in args else None
        canvasArgs['padding'] = args['padding'] if 'padding' in args else None
        canvasKwArgs = args['canvasKwArgs'] if 'canvasKwArgs' in args else dict()

        virtualListCanvas = VirtualListCanvas(self, canvasArgs, **canvasKwArgs)
        virtualListCanvas.grid(row=0, column=0, sticky='nsew')
        self.virtualListCanvas = virtualListCanvas

        # # 鼠标滚动相关
        # if 'isBindMouseWheel' in args and args['isBindMouseWheel']:
        self.bind('<Enter>', self.onEnter)
        self.bind('<Leave>', self.onLeave)

        # 滚动条
        if 'hasScrollbar' in args and args['hasScrollbar']:
            canvasVsb = ttk.Scrollbar(self,orient="vertical",command=self.virtualListCanvas.yview)
            self.virtualListCanvas.configure(yscrollcommand=canvasVsb.set)
            canvasVsb.grid(column=1, row=0, sticky='ns')
            # self.canvasVsb = canvasVsb


    def onEnter(self, event):
        args = self.args

        # 鼠标滚动相关
        if 'isBindMouseWheel' in args and args['isBindMouseWheel']:
            self.bindCanvasMousewheel(event)

        if 'onEnterFun' in args:
            args['onEnterFun'](event)

    def onLeave(self, event):
        args = self.args

        # 鼠标滚动相关
        if 'isBindMouseWheel' in args and args['isBindMouseWheel']:
            self.unbindCanvasMousewheel(event)

        if 'onLeaveFun' in args:
            args['onLeaveFun'](event)


    # 画布鼠标滚轮监听
    # 绑定
    def bindCanvasMousewheel(self, event):
        if platform == "linux" or platform == "linux2":
            self.virtualListCanvas.bind_all("<Button-4>", fp(self.onCanvasMousewheel, scroll=-1))
            self.virtualListCanvas.bind_all("<Button-5>", fp(self.onCanvasMousewheel, scroll=1))
        else:
            # <MouseWheel>
            # <Control-MouseWheel>
            # <Shift-MouseWheel>
            self.virtualListCanvas.bind_all("<MouseWheel>", self.onCanvasMousewheel)
            # self.virtualListCanvas.bind_all("<Control-MouseWheel>", self.onCanvasCtrlMousewheel)
            # self.virtualListCanvas.bind_all("<Shift-MouseWheel>", self.onCanvasShiftMousewheel)

    # 解绑
    def unbindCanvasMousewheel(self, event):
        if platform == "linux" or platform == "linux2":
            self.virtualListCanvas.unbind_all("<Button-4>")
            self.virtualListCanvas.unbind_all("<Button-5>")
        else:
            self.virtualListCanvas.unbind_all("<MouseWheel>")
            # self.virtualListCanvas.unbind_all("<Control-MouseWheel>")
            # self.virtualListCanvas.unbind_all("<Shift-MouseWheel>")

    # 响应滚动(滚轮)
    def onCanvasMousewheel(self, event):
        # //整除
        delta = (event.delta // 120)
        # mac有点不一样
        if platform == 'darwin':
            delta = event.delta
        self.virtualListCanvas.yview_scroll(-1 * delta, "units")

    # 响应滚动(shift+滚轮)
    def onCanvasShiftMousewheel(self, event):
        # self.virtualListCanvas.xview_scroll(-1 * (event.delta // 120), "units")
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

    def setTlData(self, tlData):
        self.virtualListCanvas.setTlData(tlData)

    def getTlData(self):
        return self.virtualListCanvas.getTlData()

    def jumpToIndex(self, index, yShift=0, value=0):
        return self.virtualListCanvas.jumpToIndex(index, yShift, value)

    def jumpWithYShift(self, yShift):
        return self.virtualListCanvas.jumpWithYShift(yShift)

    # 0=顶 1=底
    def jumpTo(self, value=0):
        return self.virtualListCanvas.jumpTo(value)

    def jumpWithPageUpDown(self, value):
        return self.virtualListCanvas.jumpWithPageUpDown(value)





















class TestFrame(Frame):
    """docstring for TestFrame"""
    def __init__(self, initWindow, **kwargs):
        super(TestFrame, self).__init__(initWindow, **kwargs)

class MyGUI(Frame):
    def __init__(self,initWindow):
        super().__init__(initWindow)
        self.initWindow = initWindow
        self.setInitWindow()

    #设置窗口
    def setInitWindow(self):
        #设置顶级窗体的行列权重，否则子组件的拉伸不会填充整个窗体
        self.initWindow.rowconfigure(0,weight=1)
        self.initWindow.columnconfigure(0,weight=1)
        #设置继承类MWindow的行列权重，保证内建子组件会拉伸填充
        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)

        self.initWindow.title("测试")           #窗口名
        #self.initWindow.geometry('320x160+10+10')                         #290 160为窗口大小，+10 +10 定义窗口弹出时的默认展示位置
        self.initWindow.geometry('1080x640')
        self.initWindow["bg"] = "pink"                                    #窗口背景色，其他背景色见：blog.csdn.net/chl0000/article/details/7657887
        # self.initWindow.attributes("-alpha",0.9)                          #虚化，值越小虚化程度越高
        self.initWindow.minsize(600, 400)                                  #限制窗口最小大小

        self.grid(row=0,column=0,sticky='nsew')

        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)
        # self.columnconfigure(1,weight=1)

        # frame = Frame(self, relief='groove', bd=6)
        # frame.grid(row=0,column=0,sticky='nsew')

        # testFrame = TestFrame(self, relief='groove', bd=3)
        # testFrame.grid(row=0,column=1,sticky='nsew')

        args = dict()
        args['createNodeFun'] = self.createNodeFun
        args['getNodeSizeWithDataFun'] = self.getNodeSizeWithDataFun
        args['isBindMouseWheel'] = True
        args['padding'] = {'w':10, 'h':10}
        # virtualListCanvas = VirtualListCanvas(self, args, confine=True, relief='flat', bd=5)
        # virtualListCanvas.grid(row=0, column=0, sticky='nsew')

        # tlData = list()
        # for i in range(0,1000):
        #     tlData.append(dict())
        # virtualListCanvas.setTlData(tlData)

        args['hasScrollbar'] = True
        virtualListFrame = VirtualListFrame(self, args, relief='flat', bd=5)
        virtualListFrame.grid(row=0, column=0, sticky='nsew')
        tlData = list()
        for i in range(0,1000):
            tlData.append(dict())
        virtualListFrame.setTlData(tlData)

    def createNodeFun(self, data, scrollFrame, autoInit=True):
        node = BaseNode(scrollFrame, data, autoInit, relief='flat', bd=5, bg='blue')
        w,h = self.getNodeSizeWithDataFun(data)
        node.setContentSize(w,h)
        return node

    def getNodeSizeWithDataFun(self, data):
        return 100, 100



def guiStart():
    # initWindow = Tk()              #实例化出一个父窗口
    # ZMJ_PORTAL = MyGUI(initWindow)
    # # 设置根窗口默认属性
    # ZMJ_PORTAL.setInitWindow()

    # initWindow.mainloop()          #父窗口进入事件循环，可以理解为保持窗口运行，否则界面不展示

    initWindow = Tk()

    # global pixelVirtual
    # pixelVirtual = PhotoImage(width=1, height=1)

    myGuiProgram = MyGUI(initWindow)

    initWindow.mainloop()



# guiStart()
if __name__ == "__main__":
    guiStart()
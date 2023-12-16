# EggfulTool
一个便于搜索的快捷方式管理工具 - 有点卵用工具
> python3 + tkinter + win32api

# Library
* ctypes
* [pywin32](https://github.com/mhammond/pywin32)
* [tkdnd](https://github.com/petasis/tkdnd)

# 说明
## 4种节点类型

![lineNode](https://github.com/shadowrx78/EggfulTool/blob/main/image/lineNode.png)

![btnNode](https://github.com/shadowrx78/EggfulTool/blob/main/image/btnNode.png)

### line
分割线
### exe
路径只能配置文件，点击按钮模拟双击该文件，拖入文件同样模拟拖入到该文件

![useDrop](https://github.com/shadowrx78/EggfulTool/blob/main/image/useDrop.png)

![drop](https://github.com/shadowrx78/EggfulTool/blob/main/image/drop.gif)

### folder
路径只能配置文件夹，点击按钮打开该文件夹
### cmd
路径可以配置文件和文件夹，点击按钮相当于调用cmd命令，**因此可能被杀毒软件拦截**

配置比较复杂，具体看"!"按钮说明

![cmdConfig](https://github.com/shadowrx78/EggfulTool/blob/main/image/cmdConfig.png)

## 编辑&创建节点
工具有2种模式：通常、编辑

![mode](https://github.com/shadowrx78/EggfulTool/blob/main/image/mode.png)

### 通常模式
右键点击节点打开编辑界面，编辑界面里路径栏可以直接拖入

![dropPath](https://github.com/shadowrx78/EggfulTool/blob/main/image/dropPath.gif)

### 编辑模式
左键点击节点打开编辑界面，右键点击节点选中，选中时按键盘↑↓/←→改变节点位置

![selectNMove](https://github.com/shadowrx78/EggfulTool/blob/main/image/selectNMove.gif)

左键点击+节点新建按钮节点

![createNode](https://github.com/shadowrx78/EggfulTool/blob/main/image/createNode.png)

## 搜索功能
快捷键打开搜索框，输入文本搜索，键盘↑↓选择搜索结果。搜索使用精确搜索，支持python正则表达式
* Ctrl+F 搜索全部节点
* Ctrl+P 搜索分割线
* Ctrl+R 搜索用户标记的节点

![search](https://github.com/shadowrx78/EggfulTool/blob/main/image/search.gif)

# build
```
py -3 -m PyInstaller EggfulTool.py -F --add-data C:\Users\Admin\AppData\Local\Programs\Python\Python39\tcl\tkdnd2.9.2;tkdnd --add-data .\script;.\script --onefile --windowed --icon=.\script\icon.ico -w
```

~~bug随缘修，人跟程序有一个能跑就行~~
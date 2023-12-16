#!/usr/bin/env python
# Module     : SysTrayIcon.py
# Synopsis   : Windows System tray icon.
# Programmer : Simon Brunning - simon@brunningonline.net - modified for Python 3
# Date       : 13 February 2018
# Notes      : Based on (i.e. ripped off from) Mark Hammond's
#              win32gui_taskbar.py and win32gui_menu.py demos from PyWin32
'''TODO

For now, the demo at the bottom shows how to use it...'''

import os
import sys
import win32api         # package pywin32
import win32con
import win32gui_struct
try:
    import winxpgui as win32gui
except ImportError:
    import win32gui

class SysTrayIcon(object):
    '''TODO'''
    QUIT = 'QUIT'
    SPECIAL_ACTIONS = [QUIT]

    FIRST_ID = 1023

    def __init__(self,
                 icon,
                 hover_text,
                 menu_options,
                 on_quit=None,
                 on_ldouble_click=None,
                 default_menu_index=None,
                 window_class_name=None,
                 quit_text='Quit',):

        self.icon = icon
        self.hover_text = hover_text
        self.on_quit = on_quit
        self.on_ldouble_click = on_ldouble_click

        self.isDestory = False

        self.tm_id_2_menu = dict()
        self.tl_checkbox_id = set()
        self.hmenu = None

        menu_options = menu_options + ((quit_text, None, self.QUIT),)
        self._next_action_id = self.FIRST_ID
        self.menu_actions_by_id = set()
        self.menu_options = self._add_ids_to_menu_options(list(menu_options))
        self.menu_actions_by_id = dict(self.menu_actions_by_id)
        del self._next_action_id


        self.default_menu_index = (default_menu_index or 0)
        self.window_class_name = window_class_name or "SysTrayIconPy"

        message_map = {win32gui.RegisterWindowMessage("TaskbarCreated"): self.restart,
                       win32con.WM_DESTROY: self.on_destroy,
                       win32con.WM_COMMAND: self.command,
                       win32con.WM_USER+20 : self.notify,}
        # Register the Window class.
        window_class = win32gui.WNDCLASS()
        hinst = window_class.hInstance = win32gui.GetModuleHandle(None)
        window_class.lpszClassName = self.window_class_name
        window_class.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW;
        window_class.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        window_class.hbrBackground = win32con.COLOR_WINDOW
        window_class.lpfnWndProc = message_map # could also specify a wndproc.
        classAtom = win32gui.RegisterClass(window_class)
        # Create the Window.
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = win32gui.CreateWindow(classAtom,
                                          self.window_class_name,
                                          style,
                                          0,
                                          0,
                                          win32con.CW_USEDEFAULT,
                                          win32con.CW_USEDEFAULT,
                                          0,
                                          0,
                                          hinst,
                                          None)
        win32gui.UpdateWindow(self.hwnd)
        self.notify_id = None
        self.refresh_icon()

        # win32gui.PumpMessages()

    def unpack_menu_option(self, menu_option):
        result = dict()
        result['option_text'] = menu_option[0]
        result['option_icon'] = menu_option[1]
        result['option_action'] = menu_option[2]
        result['option_fState'] = menu_option[3] if len(menu_option) >= 4 else None
        return result

    def _add_ids_to_menu_options(self, menu_options):
        result = []
        for menu_option in menu_options:
            # option_text, option_icon, option_action, option_fState = menu_option
            menu_option_unpack = self.unpack_menu_option(menu_option)
            option_action = menu_option_unpack['option_action']
            # print(menu_option_unpack)

            if callable(option_action) or option_action in self.SPECIAL_ACTIONS:
                self.menu_actions_by_id.add((self._next_action_id, option_action))
                # result.append(menu_option + (self._next_action_id,))
                if menu_option_unpack['option_fState'] != None:
                    self.tl_checkbox_id.add(self._next_action_id)
                menu_option_unpack['option_id'] = self._next_action_id
                result.append(menu_option_unpack)
            elif non_string_iterable(option_action):
                # result.append((option_text,
                #                option_icon,
                #                self._add_ids_to_menu_options(option_action),
                #                self._next_action_id))
                menu_option_unpack['option_action'] = self._add_ids_to_menu_options(option_action)
                menu_option_unpack['option_id'] = self._next_action_id
                result.append(menu_option_unpack)
            else:
                print('Unknown item', option_text, option_icon, option_action)
            self._next_action_id += 1
        return result

    def refresh_icon(self):
        # Try and find a custom icon
        hinst = win32gui.GetModuleHandle(None)
        if os.path.isfile(self.icon):
            icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
            hicon = win32gui.LoadImage(hinst,
                                       self.icon,
                                       win32con.IMAGE_ICON,
                                       0,
                                       0,
                                       icon_flags)
        else:
            print("Can't find icon file - using default.")
            hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)

        if self.notify_id: message = win32gui.NIM_MODIFY
        else: message = win32gui.NIM_ADD
        self.notify_id = (self.hwnd,
                          0,
                          win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP,
                          win32con.WM_USER+20,
                          hicon,
                          self.hover_text)
        win32gui.Shell_NotifyIcon(message, self.notify_id)

    def restart(self, hwnd, msg, wparam, lparam):
        self.notify_id = None
        self.refresh_icon()

    def on_destroy(self, hwnd, msg, wparam, lparam):
        if self.on_quit: self.on_quit(self)
        # nid = (self.hwnd, 0)
        # win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
        # win32gui.PostQuitMessage(0) # Terminate the app.
        self.destroy()

    def destroy(self):
        if not self or self.isDestory:
            return
        nid = (self.hwnd, 0)
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
        win32gui.PostQuitMessage(0) # Terminate the app.
        self.isDestory = True

    def notify(self, hwnd, msg, wparam, lparam):
        if lparam==win32con.WM_LBUTTONDBLCLK:
            if self.on_ldouble_click:
                self.on_ldouble_click(self)
            else:
                self.execute_menu_option(self.default_menu_index + self.FIRST_ID)
        elif lparam==win32con.WM_RBUTTONUP:
            self.show_menu()
        elif lparam==win32con.WM_LBUTTONUP:
            pass
        return True

    def show_menu(self):
        menu = self.hmenu
        # if not menu:
        if True:
            menu = win32gui.CreatePopupMenu()
            self.create_menu(menu, self.menu_options)
            #win32gui.SetMenuDefaultItem(menu, 1000, 0)
            self.hmenu = menu

        pos = win32gui.GetCursorPos()
        # See http://msdn.microsoft.com/library/default.asp?url=/library/en-us/winui/menus_0hdi.asp
        win32gui.SetForegroundWindow(self.hwnd)
        win32gui.TrackPopupMenu(menu,
                                win32con.TPM_LEFTALIGN,
                                pos[0],
                                pos[1],
                                0,
                                self.hwnd,
                                None)
        win32gui.PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)

    def create_menu(self, menu, menu_options):
        # for option_text, option_icon, option_action, option_id, option_fState in menu_options[::-1]:
        for menu_option_unpack in menu_options[::-1]:
            option_text = menu_option_unpack['option_text']
            option_icon = menu_option_unpack['option_icon']
            option_action = menu_option_unpack['option_action']
            option_id = menu_option_unpack['option_id']
            option_fState_blist = menu_option_unpack['option_fState']
            option_fState = None
            if option_fState_blist:
                option_fState = win32con.MFS_CHECKED if option_fState_blist[0] else win32con.MFS_UNCHECKED

            self.tm_id_2_menu[option_id] = menu

            if option_icon:
                option_icon = self.prep_menu_icon(option_icon)

            if option_id in self.menu_actions_by_id:                
                item, extras = win32gui_struct.PackMENUITEMINFO(text=option_text,
                                                                hbmpItem=option_icon,
                                                                wID=option_id,
                                                                fState=option_fState)
                win32gui.InsertMenuItem(menu, 0, 1, item)
            else:
                submenu = win32gui.CreatePopupMenu()
                self.create_menu(submenu, option_action)
                item, extras = win32gui_struct.PackMENUITEMINFO(text=option_text,
                                                                hbmpItem=option_icon,
                                                                hSubMenu=submenu)
                win32gui.InsertMenuItem(menu, 0, 1, item)

    def prep_menu_icon(self, icon):
        # First load the icon.
        ico_x = win32api.GetSystemMetrics(win32con.SM_CXSMICON)
        ico_y = win32api.GetSystemMetrics(win32con.SM_CYSMICON)
        hicon = win32gui.LoadImage(0, icon, win32con.IMAGE_ICON, ico_x, ico_y, win32con.LR_LOADFROMFILE)

        hdcBitmap = win32gui.CreateCompatibleDC(0)
        hdcScreen = win32gui.GetDC(0)
        hbm = win32gui.CreateCompatibleBitmap(hdcScreen, ico_x, ico_y)
        hbmOld = win32gui.SelectObject(hdcBitmap, hbm)
        # Fill the background.
        brush = win32gui.GetSysColorBrush(win32con.COLOR_MENU)
        win32gui.FillRect(hdcBitmap, (0, 0, 16, 16), brush)
        # unclear if brush needs to be feed.  Best clue I can find is:
        # "GetSysColorBrush returns a cached brush instead of allocating a new
        # one." - implies no DeleteObject
        # draw the icon
        win32gui.DrawIconEx(hdcBitmap, 0, 0, hicon, ico_x, ico_y, 0, 0, win32con.DI_NORMAL)
        win32gui.SelectObject(hdcBitmap, hbmOld)
        win32gui.DeleteDC(hdcBitmap)

        return hbm.Detach()

    def command(self, hwnd, msg, wparam, lparam):
        id = win32gui.LOWORD(wparam)
        self.execute_menu_option(id)

    def execute_menu_option(self, id):
        menu_action = self.menu_actions_by_id[id]      
        if menu_action == self.QUIT:
            win32gui.DestroyWindow(self.hwnd)
        else:
            if id in self.tl_checkbox_id:
                menu = self.tm_id_2_menu[id]
                state = win32gui.GetMenuState(menu, id, win32con.MF_BYCOMMAND)
                is_check = False
                if state != -1 and not (state & win32con.MF_CHECKED):
                    is_check = True
                check_flags = win32con.MFS_CHECKED if is_check else win32con.MFS_UNCHECKED
                rc = win32gui.CheckMenuItem(
                    menu, id, win32con.MF_BYCOMMAND | check_flags
                )

                # new_state = win32gui.GetMenuState(menu, id, win32con.MF_BYCOMMAND)
                # if new_state & win32con.MF_CHECKED != check_flags:
                #     raise RuntimeError("The new item didn't get the new checked state!")
                menu_action(self, is_check)
            else:
                menu_action(self)

def non_string_iterable(obj):
    try:
        iter(obj)
    except TypeError:
        return False
    else:
        return not isinstance(obj, str)

# Minimal self test. You'll need a bunch of ICO files in the current working
# directory in order for this to work...
if __name__ == '__main__':
    import itertools, glob

    icons = itertools.cycle(glob.glob('*.ico'))
    hover_text = "SysTrayIcon.py Demo"
    def hello(sysTrayIcon): print("Hello World.")
    def simon(sysTrayIcon): print("Hello Simon.")
    def switch_icon(sysTrayIcon):
        sysTrayIcon.icon = next(icons)
        sysTrayIcon.refresh_icon()
    blist1, blist2, blist3 = [False], [True], [False]
    def on_check_box1(sysTrayIcon, is_check):
        print('check box1', is_check)
        blist1[0] = is_check
    def on_check_box2(sysTrayIcon, is_check):
        print('check box2', is_check)
        blist2[0] = is_check
    def on_check_box3(sysTrayIcon, is_check):
        print('check box3', is_check)
        blist3[0] = is_check
    menu_options = (('Say Hello', next(icons), hello),
                    ('Switch Icon', None, switch_icon),
                    ('check box1', None, on_check_box1, blist1),
                    ('check box2', None, on_check_box2, blist2),
                    ('A sub-menu', next(icons), (('Say Hello to Simon', next(icons), simon),
                                                  ('Switch Icon', next(icons), switch_icon),
                                                  ('check box3', None, on_check_box3, blist3),
                                                 ))
                   )
    def bye(sysTrayIcon): print('Bye, then.')

    print('------------------')
    print(next(icons))
    SysTrayIcon(next(icons), hover_text, menu_options, on_quit=bye, default_menu_index=1)
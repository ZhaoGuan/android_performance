#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
from moudle.device_info import DeviceInfoRun, app_pid
from moudle.info_report import info_report
import tkinter as tk
import tkinter.messagebox as msgbox
import os
import time

PATH = os.path.dirname(os.path.abspath(__file__))
info_path = PATH + "/info"
report_path = PATH + "/report"


def make_dir(dirs):
    if not os.path.exists(dirs):
        os.makedirs(dirs)


make_dir(info_path)
make_dir(report_path)
device_info = None
running = None
window = tk.Tk()
window.title("Android性能收集")

window.geometry('500x300')
my_label = tk.Label(window, text="请先连接好数据线并且确保ADB能够正常使用")
package_name_entry = tk.Entry(window)
my_label.pack()
package_name_entry.pack()


def begin():
    package_name = package_name_entry.get()
    if package_name == "":
        msgbox.showerror(title='启动失败', message='未填写应用包名')
        return
    pid = app_pid(package_name)
    t.insert("insert", package_name + "\n")
    t.insert("insert", pid + "\n")
    if pid == "":
        msgbox.showerror(title='启动失败', message='未发现对应应用的pid')
        return
    global device_info
    global running
    device_info = DeviceInfoRun(package_name)
    device_info.start()
    running = True
    t.insert("insert", "启动性能收集\n")


def end():
    global running
    if running is True:
        device_info.end()
        t.insert('insert', "关闭性能收集\n")
        time.sleep(5)
        info_report()
        running = None
    else:
        t.insert('insert', "未启动别瞎搞!\n")


b1 = tk.Button(window, text='insert point', width=10,
               height=2, command=begin)
b2 = tk.Button(window, text='insert point', width=10,
               height=2, command=end)
b1.pack()
b2.pack()

t = tk.Text(window)
t.pack()

window.mainloop()

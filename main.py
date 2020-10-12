#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
from moudle.device_info import DeviceInfoRun, app_pid
from moudle.info_report import info_report
from moudle.app_start_info import AppStart
import tkinter as tk
import tkinter.messagebox as msgbox
import os
import time

PATH = os.path.dirname(os.path.abspath(__file__))
info_path = PATH + "/info"
report_path = PATH + "/report"

device_info = None
running = None
window = tk.Tk()
window.title("Android性能收集")

window.geometry('500x300')
my_label = tk.Label(window, text="请先连接好数据线并且确保ADB能够正常使用,\n"
                                 "电量的测试需要通过ip连接adb。")
my_label.pack()
master = tk.Frame()
master.pack()
frame_l = tk.Frame(master)
frame_r = tk.Frame(master)
frame_l.pack(side="left")
frame_r.pack(side="right")

p_label = tk.Label(frame_l, text="请输入包名:")
a_label = tk.Label(frame_l, text="请输入启动页面名:")
r_label = tk.Label(frame_l, text="请输入要重复启动的次数:")
p_label.pack()
a_label.pack()
r_label.pack()

package_name_entry = tk.Entry(frame_r)
activity_entry = tk.Entry(frame_r)
run_time = tk.Entry(frame_r)

package_name_entry.pack()
activity_entry.pack()
run_time.pack()
start_report = False


def start_avg_time():
    global start_report
    package_name = package_name_entry.get()
    activity = activity_entry.get()
    the_run_time = run_time.get()
    if package_name == "":
        msgbox.showerror(title='启动失败', message='未填写应用包名')
        return
    if activity == "":
        msgbox.showerror(title='启动失败', message='未填写启动页名称')
        return
    if the_run_time == "":
        the_run_time = 5
    ast = AppStart(package_name, activity, int(the_run_time))
    avg_start_time = ast.run()
    start_report = True
    t.insert("end", "平均启动时间为: %s\n" % str(avg_start_time))


def begin():
    package_name = package_name_entry.get()
    if package_name == "":
        msgbox.showerror(title='启动失败', message='未填写应用包名')
        return
    pid = app_pid(package_name)
    t.insert("end", package_name + "\n")
    t.insert("end", pid + "\n")
    if pid == "":
        msgbox.showerror(title='启动失败', message='未发现对应应用的pid')
        return
    global device_info
    global running
    device_info = DeviceInfoRun(package_name)
    device_info.start()
    running = True
    t.insert("end", "启动性能收集\n")


def end():
    global running
    if running is True:
        device_info.end()
        t.insert('end', "关闭性能收集\n")
        time.sleep(5)
        running = None
        info_report()
    else:
        t.insert('end', "未启动别瞎搞!\n")


run_master_frame = tk.Frame()
run_master_frame.pack()
stat_time_info_frame = tk.Frame(run_master_frame)
stat_time_info_frame.pack(side="left")
stat_time_info_label = tk.Label(stat_time_info_frame, text="执行启动时间计算")
stat_time_info_start_button = tk.Button(stat_time_info_frame, text='启动', width=10,
                                        height=2, command=start_avg_time)
stat_time_info_label.pack(side="left")
stat_time_info_start_button.pack()

device_info_frame = tk.Frame(run_master_frame)
device_info_frame.pack(side="right")
device_label = tk.Label(device_info_frame, text="执行性能收集")
device_info_start_button = tk.Button(device_info_frame, text='启动', width=10,
                                     height=2, command=begin)
device_info_stop_button = tk.Button(device_info_frame, text='关闭', width=10,
                                    height=2, command=end)
device_label.pack(side="left")
device_info_start_button.pack()
device_info_stop_button.pack()

t = tk.Text(window)
t.pack()

window.mainloop()

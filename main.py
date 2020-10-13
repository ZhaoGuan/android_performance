#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
from moudle.device_info import DeviceInfoRun, app_pid
from moudle.info_report import info_report, diff_report
from moudle.app_start_info import AppStart
from moudle.utils import get_version_name_by_applicationid, make_dir, dir_list
import tkinter as tk
import tkinter.messagebox as msgbox
import os
import time

PATH = os.path.dirname(os.path.abspath(__file__))
package_name = None
the_version_name = None
device_info = None
running = None
window = tk.Tk()
window.title("Android性能收集")

window.geometry('500x500')
my_label = tk.Label(window, text="请先连接好数据线并且确保ADB能够正常使用,\n"
                                 "电量的测试需要通过ip连接adb.\n"
                                 "adb tcpip 55555\n"
                                 "adb connect 设备的ip")
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
v_label = tk.Label(frame_l, text="请输入应用版本:")
v_label.pack()
p_label.pack()
a_label.pack()
r_label.pack()

package_name_entry = tk.Entry(frame_r)
activity_entry = tk.Entry(frame_r)
run_time = tk.Entry(frame_r)
version_name = tk.Entry(frame_r)
version_name.pack()
package_name_entry.pack()
activity_entry.pack()
run_time.pack()
start_report = False


def start_avg_time():
    global package_name
    global the_version_name
    global start_report
    make_dir(PATH + "/info/")
    package_name = package_name_entry.get()
    activity = activity_entry.get()
    the_run_time = run_time.get()
    the_version_name = version_name.get()
    if package_name == "":
        msgbox.showerror(title='启动失败', message='未填写应用包名')
        return
    if activity == "":
        msgbox.showerror(title='启动失败', message='未填写启动页名称')
        return
    if the_run_time == "":
        the_run_time = 5
    if the_version_name == "":
        the_version_name = get_version_name_by_applicationid(package_name)
        make_dir(PATH + "/info/" + str(the_version_name))
    else:
        make_dir(PATH + "/info/" + str(the_version_name))
    t.insert("end", "启动次数为: %s\n" % str(the_run_time))
    t.insert("end", "请等待执行结束....\n")
    ast = AppStart(package_name, activity, int(the_run_time))
    avg_start_time = ast.run()
    start_report = True
    t.insert("end", "平均启动时间为: %s\n" % str(avg_start_time))


def android_performance_begin():
    global package_name
    global the_version_name
    make_dir(PATH + "/info/")
    package_name = package_name_entry.get()
    the_version_name = version_name.get()
    print(the_version_name)
    if package_name == "":
        msgbox.showerror(title='启动失败', message='未填写应用包名')
        return
    pid = app_pid(package_name)
    t.insert("end", package_name + "\n")
    t.insert("end", pid + "\n")
    if pid == "":
        msgbox.showerror(title='启动失败', message='未发现对应应用的pid')
        return
    if the_version_name == "":
        the_version_name = get_version_name_by_applicationid(package_name)
        make_dir(PATH + "/info/" + str(the_version_name))
    else:
        make_dir(PATH + "/info/" + str(the_version_name))
    global device_info
    global running
    device_info = DeviceInfoRun(package_name)
    device_info.start()
    running = True
    t.insert("end", "启动性能收集\n")


def android_performance_end():
    make_dir(PATH + "/info/")
    global running
    if running is True:
        device_info.end()
        t.insert('end', "关闭性能收集\n")
        time.sleep(5)
        running = None
        info_report({"package_name": package_name, "tag": the_version_name}, start_report)
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
                                     height=2, command=android_performance_begin)
device_info_stop_button = tk.Button(device_info_frame, text='关闭', width=10,
                                    height=2, command=android_performance_end)
device_label.pack(side="left")
device_info_start_button.pack()
device_info_stop_button.pack()

diff_frame = tk.Frame()
diff_frame.pack()
diff_l_frame = tk.Frame(diff_frame)
diff_r_frame = tk.Frame(diff_frame)
diff_l_frame.pack(side="left")
diff_r_frame.pack(side="right")
diff_label = tk.Label(diff_l_frame, text='请输入要比较的版本,版本之间请使用","(英文逗号)分割:')
diff_entry = tk.Entry(diff_l_frame)
diff_label.pack()
diff_entry.pack()


def android_performance_diff():
    data_path = PATH + "/info/"
    if not os.path.exists(data_path):
        t.insert("end", "没有发现性能数据!\n")
        return
    diff_tags = diff_entry.get()
    if diff_tags == "":
        tag_dir_list = dir_list(data_path)
        if len(tag_dir_list) > 1:
            diff_report()
            t.insert("end", "已生成请在report文件夹中查看\n")
        else:
            t.insert('end', "数据不足两组个不进行比较\n")
    else:
        path_list = []
        diff_tag_list = diff_tags.split(",")
        for tag in diff_tag_list:
            path = data_path + tag
            if os.path.exists(path):
                path_list.append(path)
            else:
                t.insert('end', "未发现%s数据\n" % tag)
        if len(path_list) > 1:
            diff_report(path_list)
            t.insert("end", "已生成请在report文件夹中查看\n")
        else:
            t.insert('end', "数据不足两组个不进行比较\n")


diff_button = tk.Button(diff_r_frame, text="启动", width=10,
                        height=2, command=android_performance_diff)
diff_button.pack()

t = tk.Text(window)
t.pack()

window.mainloop()

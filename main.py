#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
import multiprocessing

multiprocessing.freeze_support()
from moudle.performance.device_info import DeviceInfoRun
from moudle.performance.info_report import info_report, diff_report, avg_data
from moudle.performance.app_start_info import AppStart
from moudle.utils import dir_list, MOUDLE_PATH, run_proxy, android_get_devices_name, android_get_application_id_by_pid
import tkinter as tk
import tkinter.messagebox as msgbox
import os
import time
from moudle.utils import *

PATH = os.path.dirname(os.path.abspath(__file__))
package_name = None
the_version_name = None
device_name = None
device_info = None
running = None
port_entry = None
proxy_window_text = None


def base_config():
    package_name = package_name_entry.get()
    activity = activity_entry.get()
    the_version_name = version_name.get()
    device_name = device_name_entry.get()
    if device_name == "":
        device_name = android_get_devices_name()
        window_text.insert("end", "获取设备名称:%s\n" % str(device_name))
    else:
        window_text.insert("end", "设备名称:%s\n" % str(device_name))
    if package_name == "":
        msgbox.showerror(title='启动失败', message='未填写应用包名')
        return
        # package_name = "com.yiding.jianhuo"
        # window_text.insert("end", "使用默认包名:%s\n" % str(package_name))
    else:
        window_text.insert("end", "包名:%s\n" % str(package_name))
    if activity == "":
        msgbox.showerror(title='启动失败', message='未填写启动页名称')
        return
        # activity = "com.yiding.jianhuo.SplashActivity"
        # window_text.insert("end", "使用默认启动页:%s\n" % str(activity))
    else:
        window_text.insert("end", "启动页:%s\n" % str(activity))
    if the_version_name == "":
        the_version_name = android_get_version_name_by_application_id(package_name)
        window_text.insert("end", "自动获取版本号:%s\n" % str(the_version_name))
    else:
        window_text.insert("end", "版本号:%s\n" % str(the_version_name))
    return package_name, activity, the_version_name, device_name


def start_avg_time():
    global package_name
    global the_version_name
    global start_report
    package_name = package_name_entry.get()
    the_run_time = run_time.get()
    the_version_name = version_name.get()
    if the_run_time != "" and int(the_run_time) < 2:
        window_text.insert("end", "启动次数要大于1")
        return
    if the_run_time == "":
        the_run_time = 5
    package_name, activity, the_version_name, device_name = base_config()
    window_text.insert("end", "启动次数为: %s\n" % str(the_run_time))
    window_text.insert("end", "请等待执行结束....\n")
    ast = AppStart(the_version_name, package_name, activity, int(the_run_time))
    avg_start_time = ast.run()
    start_report = True
    window_text.insert("end", "最快启动时间为: %s\n" % str(ast.fast))
    window_text.insert("end", "最慢启动时间为: %s\n" % str(ast.slow))
    window_text.insert("end", "平均启动时间为: %s\n" % str(avg_start_time))


def android_performance_begin():
    global package_name
    global the_version_name
    global device_name
    package_name, activity, the_version_name, device_name = base_config()
    pid = android_get_application_id_by_pid(package_name)
    window_text.insert("end", package_name + "\n")
    window_text.insert("end", pid + "\n")
    if pid == "":
        msgbox.showerror(title='启动失败', message='未发现对应应用的pid')
        return
    if the_version_name == "":
        the_version_name = android_get_version_name_by_application_id(package_name)
    global device_info
    global running
    device_info = DeviceInfoRun(the_version_name, package_name)
    device_info.start()
    running = True
    window_text.insert("end", "启动性能收集\n")


def android_performance_end():
    global running
    if running is True:
        device_info.end()
        window_text.insert('end', "关闭性能收集\n")
        time.sleep(5)
        running = None
        info_report({"package_name": package_name, "tag": the_version_name, "device": device_name}, start_report)
    else:
        window_text.insert('end', "未启动别瞎搞!\n")


def android_performance_diff():
    data_path = MOUDLE_PATH + "/../info/"
    if not os.path.exists(data_path):
        window_text.insert("end", "没有发现性能数据!\n")
        return
    diff_tags = diff_entry.get()
    if diff_tags == "":
        tag_dir_list = dir_list(data_path)
        if len(tag_dir_list) > 1:
            diff_report()
            window_text.insert("end", "已生成请在report文件夹中查看\n")
        else:
            window_text.insert('end', "数据不足两组个不进行比较\n")
    else:
        path_list = []
        diff_tag_list = diff_tags.split(",")
        for tag in diff_tag_list:
            path = data_path + tag
            if os.path.exists(path):
                path_list.append(path)
            else:
                window_text.insert('end', "未发现%s数据\n" % tag)
        if len(path_list) > 1:
            diff_report(path_list)
            window_text.insert("end", "已生成请在report文件夹中查看\n")
        else:
            window_text.insert('end', "数据不足两组个不进行比较\n")


def start_proxy():
    global pid
    global running
    port = port_entry.get()
    if port == "":
        proxy_window_text.insert("end", "请输入端口号!\n")
        return
    if running is not None:
        proxy_window_text.insert("end", "已经启动了代理\n")
        return
    running, pid = run_proxy(port)
    proxy_window_text.insert('end', "启动抓包\n")
    proxy_window_text.insert('end', "抓包服务地址: http://127.0.0.1:8081/\n")
    proxy_window_text.insert('end', "请等待启动!\n")


def stop_proxy():
    global running
    if running is None:
        proxy_window_text.insert('end', "没有启动抓包\n")
    else:
        os.kill(pid, 2)
        running = None
        proxy_window_text.insert('end', "已经关闭抓包\n")


def proxy_top_level():
    global port_entry
    global proxy_window_text
    # 抓包
    proxy_top = tk.Toplevel()
    proxy_top.title("代理抓包工具")
    proxy_top.geometry('500x500')
    proxy_my_label = tk.Label(proxy_top, text=
    "如果需要使用安全证书请连接代理后访问mitm.it,进行证书安装.\n"
    "config.yml中添加过滤的host\n"
    "recording文件夹存放每次录制的数据,report中存放是报告结果\n")
    proxy_my_label.pack()
    proxy_master = tk.Frame(proxy_top)
    proxy_master.pack()
    proxy_frame_l = tk.Frame(proxy_master)
    proxy_frame_r = tk.Frame(proxy_master)
    proxy_frame_l.pack(side="left")
    proxy_frame_r.pack(side="right")

    port_label = tk.Label(proxy_frame_l, text="请输要使用的端口号:")
    port_label.pack()
    port_entry = tk.Entry(proxy_frame_l)
    port_entry.pack()

    proxy_start_button = tk.Button(proxy_frame_r, text='启动', width=10,
                                   height=2, command=start_proxy)
    proxy_stop_button = tk.Button(proxy_frame_r, text='关闭', width=10,
                                  height=2, command=stop_proxy)
    proxy_start_button.pack()
    proxy_stop_button.pack()
    proxy_window_text = tk.Text(proxy_top)
    proxy_window_text.pack()




def upload_avg_data():
    package_name, activity, the_version_name, device_name = base_config()
    app = {"package_name": package_name, "tag": the_version_name, "device": device_name}
    db = DataBase()
    avg_cpu_data, avg_mem_data, battery_stats, battery_time, avg_battery_stats, avg_start_app = avg_data()
    if avg_cpu_data is False:
        window_text.insert('end', "未发现性能数据\n")
        return
    result = db.insert_data(app, avg_cpu_data, avg_mem_data, battery_stats, battery_time, avg_battery_stats,
                            avg_start_app)
    if result:
        window_text.insert('end', "性能数据上传成功\n")
    else:
        window_text.insert('end', "性能数据上传失败\n")


if __name__ == "__main__":
    window = tk.Tk()
    window.title("Android性能收集")
    window.geometry('500x500')
    performance_label = tk.Label(window, text="请先连接好数据线并且确保ADB能够正常使用,\n"
                                              "电量的测试需要通过ip连接adb.\n"
                                              "adb tcpip 5555\n"
                                              "adb connect 设备的ip")
    performance_label.pack()
    device_name_frame = tk.Frame()
    device_name_frame.pack()
    device_name = tk.Label(device_name_frame, text="请输入设备名称:")
    device_name_entry = tk.Entry(device_name_frame)
    device_name.pack(side="left")
    device_name_entry.pack(side="right")
    p_frame = tk.Frame()
    p_frame.pack()
    p_label = tk.Label(p_frame, text="请输入包名:")
    package_name_entry = tk.Entry(p_frame)
    p_label.pack(side="left")
    package_name_entry.pack(side="right")
    a_frame = tk.Frame()
    a_frame.pack()
    a_label = tk.Label(a_frame, text="请输入启动页面名:")
    activity_entry = tk.Entry(a_frame)
    a_label.pack(side="left")
    activity_entry.pack(side="right")
    r_frame = tk.Frame()
    r_frame.pack()
    r_label = tk.Label(r_frame, text="请输入要重复启动的次数:")
    run_time = tk.Entry(r_frame)
    r_label.pack(side="left")
    run_time.pack(side="right")
    v_frame = tk.Frame()
    v_frame.pack()
    v_label = tk.Label(v_frame, text="请输入应用版本:")
    version_name = tk.Entry(v_frame)
    v_label.pack(side="left")
    version_name.pack(side="right")
    # 启动测试
    start_report = False
    run_performance_master_frame = tk.Frame()
    run_performance_master_frame.pack()
    stat_time_info_frame = tk.Frame(run_performance_master_frame)
    stat_time_info_frame.pack(side="left")
    stat_time_info_label = tk.Label(stat_time_info_frame, text="执行启动时间计算")
    stat_time_info_start_button = tk.Button(stat_time_info_frame, text='启动', width=10,
                                            height=2, command=start_avg_time)
    stat_time_info_label.pack(side="left")
    stat_time_info_start_button.pack()
    # 性能手机
    device_info_frame = tk.Frame(run_performance_master_frame)
    device_info_frame.pack(side="right")
    device_label = tk.Label(device_info_frame, text="执行性能收集")
    device_info_start_button = tk.Button(device_info_frame, text='启动', width=10,
                                         height=2, command=android_performance_begin)
    device_info_stop_button = tk.Button(device_info_frame, text='关闭', width=10,
                                        height=2, command=android_performance_end)
    device_label.pack(side="left")
    device_info_start_button.pack()
    device_info_stop_button.pack()
    # diff 部分
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
    diff_button = tk.Button(diff_r_frame, text="启动", width=10,
                            height=2, command=android_performance_diff)
    diff_button.pack()
    p_frame = tk.Frame()
    p_frame.pack()
    proxy_label = tk.Label(p_frame, height=2, text="代理工具启动:")
    proxy_button = tk.Button(p_frame, text='启动', width=10,
                             height=2, command=proxy_top_level)
    proxy_label.pack(side="left")
    proxy_button.pack(side="right")
    window_text = tk.Text(window)
    window_text.pack()

    window.mainloop()

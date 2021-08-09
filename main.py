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
from tkinter import ttk
import tkinter.messagebox as msgbox
import os
import time
from moudle.utils import *
from proxy.url_statistics import make_url_statistics_report, make_url_time_report, make_har

PATH = os.path.dirname(os.getcwd())
package_name = None
the_version_name = None
device_name = None
device_info = None
running = None
port_entry = None
proxy_gui_text = None


def base_config():
    package_name = package_name_entry.get()
    activity = activity_entry.get()
    the_version_name = version_name.get()
    device_name = device_name_entry.get()
    if device_name == "":
        device_name = android_get_devices_name()
        gui_text.insert("end", "获取设备名称:%s\n" % str(device_name))
    else:
        gui_text.insert("end", "设备名称:%s\n" % str(device_name))
    if package_name == "":
        msgbox.showerror(title='启动失败', message='未填写应用包名')
        return
        # package_name = "com.yiding.jianhuo"
        # gui_text.insert("end", "使用默认包名:%s\n" % str(package_name))
    else:
        gui_text.insert("end", "包名:%s\n" % str(package_name))
    if activity == "":
        msgbox.showerror(title='启动失败', message='未填写启动页名称')
        return
        # activity = "com.yiding.jianhuo.SplashActivity"
        # gui_text.insert("end", "使用默认启动页:%s\n" % str(activity))
    else:
        gui_text.insert("end", "启动页:%s\n" % str(activity))
    if the_version_name == "":
        the_version_name = android_get_version_name_by_application_id(package_name)
        gui_text.insert("end", "自动获取版本号:%s\n" % str(the_version_name))
    else:
        gui_text.insert("end", "版本号:%s\n" % str(the_version_name))
    return package_name, activity, the_version_name, device_name


def start_avg_time():
    global package_name
    global the_version_name
    global start_report
    package_name = package_name_entry.get()
    the_run_time = run_time.get()
    the_version_name = version_name.get()
    if the_run_time != "" and int(the_run_time) < 2:
        gui_text.insert("end", "启动次数要大于1")
        return
    if the_run_time == "":
        the_run_time = 5
    package_name, activity, the_version_name, device_name = base_config()
    gui_text.insert("end", "启动次数为: %s\n" % str(the_run_time))
    gui_text.insert("end", "请等待执行结束....\n")
    ast = AppStart(the_version_name, package_name, activity, int(the_run_time))
    avg_start_time = ast.run()
    start_report = True
    gui_text.insert("end", "最快启动时间为: %s\n" % str(ast.fast))
    gui_text.insert("end", "最慢启动时间为: %s\n" % str(ast.slow))
    gui_text.insert("end", "平均启动时间为: %s\n" % str(avg_start_time))


def android_performance_begin():
    global package_name
    global the_version_name
    global device_name
    package_name, activity, the_version_name, device_name = base_config()
    pid = android_get_pid_by_application_id(package_name)
    gui_text.insert("end", package_name + "\n")
    gui_text.insert("end", pid + "\n")
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
    gui_text.insert("end", "启动性能收集\n")


def android_performance_end():
    global running
    if running is True:
        device_info.end()
        gui_text.insert('end', "关闭性能收集\n")
        time.sleep(5)
        running = None
        info_report({"package_name": package_name, "tag": the_version_name, "device": device_name}, start_report)
    else:
        gui_text.insert('end', "未启动别瞎搞!\n")


def android_performance_diff():
    data_path = MOUDLE_PATH + "/../info/"
    if not os.path.exists(data_path):
        gui_text.insert("end", "没有发现性能数据!\n")
        return
    diff_tags = diff_entry.get()
    if diff_tags == "":
        tag_dir_list = dir_list(data_path)
        if len(tag_dir_list) > 1:
            diff_report()
            gui_text.insert("end", "已生成请在report文件夹中查看\n")
        else:
            gui_text.insert('end', "数据不足两组个不进行比较\n")
    else:
        path_list = []
        diff_tag_list = diff_tags.split(",")
        for tag in diff_tag_list:
            path = data_path + tag
            if os.path.exists(path):
                path_list.append(path)
            else:
                gui_text.insert('end', "未发现%s数据\n" % tag)
        if len(path_list) > 1:
            diff_report(path_list)
            gui_text.insert("end", "已生成请在report文件夹中查看\n")
        else:
            gui_text.insert('end', "数据不足两组个不进行比较\n")


def start_proxy():
    global pid
    global running
    port = port_entry.get()
    if port == "":
        proxy_gui_text.insert("end", "请输入端口号!\n")
        return
    if running is not None:
        proxy_gui_text.insert("end", "已经启动了代理\n")
        return
    running, pid = run_proxy(port)
    proxy_gui_text.insert('end', "启动抓包\n")
    proxy_gui_text.insert('end', "抓包服务地址: http://127.0.0.1:8081/\n")
    proxy_gui_text.insert('end', "请等待启动!\n")


def stop_proxy():
    global running
    if running is None:
        proxy_gui_text.insert('end', "没有启动抓包\n")
    else:
        os.kill(pid, 2)
        running = None
        proxy_gui_text.insert('end', "已经关闭抓包\n")


def get_proxy_report():
    report_path = make_url_time_report()
    print(report_path)
    if open_file(report_path) is False:
        proxy_gui_text.insert('end', f"报告路径错误,不存在{report_path}\n")


def get_har():
    report_path = make_har()
    proxy_gui_text.insert('end', f"HAR文件路径:{report_path}")


def get_statistics_report():
    report_path = make_url_statistics_report()
    print(report_path)
    if open_file(report_path) is False:
        proxy_gui_text.insert('end', f"报告路径错误,不存在{report_path}\n")


def proxy_top_level():
    global port_entry
    global proxy_gui_text
    # 抓包
    proxy_top = tk.Toplevel()
    proxy_top.title("代理抓包工具")
    proxy_top.geometry('500x500')
    proxy_my_label = ttk.Label(proxy_top, text=
    "如果需要使用安全证书请连接代理后访问mitm.it,进行证书安装.\n"
    "config.yml中添加过滤的host\n"
    "recording文件夹存放每次录制的数据,report中存放是报告结果\n"
    "report只根据最新抓包结果生成报告\n")
    proxy_my_label.pack()
    proxy_input = ttk.Frame(proxy_top)
    proxy_input.pack()
    port_label = ttk.Label(proxy_input, text="请输要使用的端口号:")
    port_label.pack(side="left")
    port_entry = ttk.Entry(proxy_input)
    port_entry.pack(side="right")
    proxy_master = ttk.Frame(proxy_top)
    proxy_master.pack()
    proxy_frame_l = ttk.Frame(proxy_master)
    proxy_frame_r = ttk.Frame(proxy_master)
    proxy_frame_l.pack(side="left")
    proxy_frame_r.pack(side="right")

    proxy_start_button = ttk.Button(proxy_frame_l, text='启动', width=10,
                                    command=start_proxy)
    proxy_stop_button = ttk.Button(proxy_frame_l, text='关闭', width=10,
                                   command=stop_proxy)
    proxy_report_button = ttk.Button(proxy_frame_r, text='生成报告', width=10,
                                     command=get_proxy_report)
    proxy_har_button = ttk.Button(proxy_frame_r, text='生成HAR', width=10,
                                  command=get_har)
    proxy_statistics_button = ttk.Button(proxy_frame_r, text='生成统计报告', width=10,
                                         command=get_statistics_report)
    proxy_start_button.pack()
    proxy_stop_button.pack()
    proxy_report_button.pack()
    proxy_har_button.pack()
    proxy_statistics_button.pack()
    proxy_gui_text = tk.Text(proxy_top)
    proxy_gui_text.pack()


def upload_avg_data():
    package_name, activity, the_version_name, device_name = base_config()
    app = {"package_name": package_name, "tag": the_version_name, "device": device_name}
    avg_cpu_data, avg_mem_data, battery_stats, battery_time, avg_battery_stats, avg_start_app = avg_data()
    if avg_cpu_data is False:
        gui_text.insert('end', "未发现性能数据\n")


if __name__ == "__main__":
    gui = tk.Tk()
    gui.title("Android性能收集")
    gui.geometry('500x500')
    gui.configure()
    performance_label = ttk.Label(gui, text="请先连接好数据线并且确保ADB能够正常使用,\n"
                                            "电量的测试需要通过ip连接adb.\n"
                                            "adb tcpip 5555\n"
                                            "adb connect 设备的ip")
    performance_label.pack()
    device_name_frame = ttk.Frame()
    device_name_frame.pack()
    device_name = ttk.Label(device_name_frame, text="请输入设备名称:")
    device_name_entry = ttk.Entry(device_name_frame)
    device_name.pack(side="left")
    device_name_entry.pack(side="right")
    p_frame = ttk.Frame()
    p_frame.pack()
    p_label = ttk.Label(p_frame, text="请输入包名:")
    package_name_entry = ttk.Entry(p_frame)
    p_label.pack(side="left")
    package_name_entry.pack(side="right")
    a_frame = ttk.Frame()
    a_frame.pack()
    a_label = ttk.Label(a_frame, text="请输入启动页面名:")
    activity_entry = ttk.Entry(a_frame)
    a_label.pack(side="left")
    activity_entry.pack(side="right")
    r_frame = ttk.Frame()
    r_frame.pack()
    r_label = ttk.Label(r_frame, text="请输入要重复启动的次数:")
    run_time = ttk.Entry(r_frame)
    r_label.pack(side="left")
    run_time.pack(side="right")
    v_frame = ttk.Frame()
    v_frame.pack()
    v_label = ttk.Label(v_frame, text="请输入应用版本:")
    version_name = ttk.Entry(v_frame)
    v_label.pack(side="left")
    version_name.pack(side="right")
    # 启动测试
    start_report = False
    run_performance_master_frame = ttk.Frame()
    run_performance_master_frame.pack()
    stat_time_info_frame = ttk.Frame(run_performance_master_frame)
    stat_time_info_frame.pack(side="left")
    stat_time_info_label = ttk.Label(stat_time_info_frame, text="执行启动时间计算")
    stat_time_info_start_button = ttk.Button(stat_time_info_frame, text='启动', width=10,
                                             command=start_avg_time)
    stat_time_info_label.pack(side="left")
    stat_time_info_start_button.pack()
    # 性能手机
    device_info_frame = ttk.Frame(run_performance_master_frame)
    device_info_frame.pack(side="right")
    device_label = ttk.Label(device_info_frame, text="执行性能收集")
    device_info_start_button = ttk.Button(device_info_frame, text='启动', width=10,
                                          command=android_performance_begin)
    device_info_stop_button = ttk.Button(device_info_frame, text='关闭', width=10,
                                         command=android_performance_end)
    device_label.pack(side="left")
    device_info_start_button.pack()
    device_info_stop_button.pack()
    # diff 部分
    diff_frame = ttk.Frame()
    diff_frame.pack()
    diff_l_frame = ttk.Frame(diff_frame)
    diff_r_frame = ttk.Frame(diff_frame)
    diff_l_frame.pack(side="left")
    diff_r_frame.pack(side="right")
    diff_label = ttk.Label(diff_l_frame, text='请输入要比较的版本,版本之间请使用","(英文逗号)分割:')
    diff_entry = ttk.Entry(diff_l_frame)
    diff_label.pack()
    diff_entry.pack()
    diff_button = ttk.Button(diff_r_frame, text="启动", width=10,
                             command=android_performance_diff)
    diff_button.pack()
    p_frame = ttk.Frame()
    p_frame.pack()
    proxy_label = ttk.Label(p_frame, text="代理工具启动:")
    proxy_button = ttk.Button(p_frame, text='启动', width=10,
                              command=proxy_top_level)
    proxy_label.pack(side="left")
    proxy_button.pack(side="right")
    gui_text = tk.Text(gui)
    gui_text.pack()

    gui.mainloop()

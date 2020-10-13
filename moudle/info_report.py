#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
from jinja2 import Template
import os
import csv
import time
from moudle.utils import new_dir, new_file, make_dir, dir_list, file_list
import numpy as nu

PATH = os.path.dirname(os.path.abspath(__file__))
template = """
<!doctype html>
<html>
<head>
    <title>Android Info</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@2.8.0"></script>
    <!-- 最新版本的 Bootstrap 核心 CSS 文件 -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.3.7/dist/css/bootstrap.min.css"
          crossorigin="anonymous">
    <meta name="viewport" content="initial-scale = 1, user-scalable = no">
    <meta charset="UTF-8">
</head>
<body>
<div>
    <table class="table table-bordered table-hover">
        <tr>
            <th>包名</th>
            <th>标签(版本号)</th>
        </tr>

        <tr>
            <td>{{ app.package_name }}</td>
            <td>{{ app.tag }}</td>
        </tr>
    </table>
    <table id="start_report" class="table table-bordered table-hover">
        <tr>
            <th>包名</th>
            <th>启动页名</th>
            <th>启动次数</th>
            <th>平均启动时间</th>
        </tr>
        
        <tr>
            <td>{{ start_data.package_name }}</td>
            <td>{{ start_data.start_activity }}</td>
            <td>{{ start_data.run_time }}</td>
            <td>{{ start_data.avg_start_time }}</td>
        </tr>
    </table>
    <table class="table table-bordered table-hover">
        <tr>
            <th>耗电量</th>
            <th>用时(秒)</th>
        </tr>

        <tr>
            <td>{{ battery_stats }} mAH</td>
            <td>{{ battery_time }} mAH</td>
        </tr>
    </table>
</div>
<canvas id="cpuChart"></canvas>
<canvas id="memoryChart"></canvas>
<canvas id="fpsChart"></canvas>
<canvas id="netChart"></canvas>

</body>
<script>
    const wh = document.body.clientHeight;
    const cpuChart = document.getElementById('cpuChart');
    const memoryChart = document.getElementById('memoryChart');
    const fpsChart = document.getElementById('fpsChart');
    const netChart = document.getElementById('netChart');
    document.getElementById('start_report').hidden = {{ show_start_report }};
    cpuChart.height = wh / 4;
    memoryChart.height = wh / 4;
    fpsChart.height = wh / 4;
    netChart.height = wh / 4;
    const cpu_ctx = cpuChart.getContext('2d');
    const mem_ctx = memoryChart.getContext('2d');
    const fps_ctx = fpsChart.getContext('2d');
    const net_ctx = netChart.getContext('2d');
    const cpu_chart = new Chart(cpu_ctx, {
        // The type of chart we want to create
        type: 'line',
        // The data for our dataset
        data: {
            labels: {{ cpu_time_labels }},
            datasets: [{
                label: 'CPU',
                // backgroundColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(0, 0, 0, 0.1)',
                borderColor: 'rgb(255, 99, 132)',
                data: {{ cpu_data }}
            }]
        },
        // Configuration options go here
        options: {scales: {yAxes: [{scaleLabel: {display: true, labelString: "%"}}]}}
    });
    const mem_chart = new Chart(mem_ctx, {
        // The type of chart we want to create
        type: 'line',
        // The data for our dataset
        data: {
            labels: {{ mem_time_labels }},
            datasets: [{
                label: 'MEMORY',
                // backgroundColor: 'rgb(193 255 193)',
                backgroundColor: 'rgba(0, 0, 0, 0.1)',
                borderColor: 'rgb(193 255 193)',
                data: {{ mem_data }}
            }]
        },
        // Configuration options go here
        options: {scales: {yAxes: [{scaleLabel: {display: true, labelString: "MB"}}]}}
    });
    const fps_chart = new Chart(fps_ctx, {
        // The type of chart we want to create
        type: 'line',
        // The data for our dataset
        data: {
            labels: {{ fps_time_labels }},
            datasets: [{
                label: 'FPS',
                // backgroundColor: 'rgb(193 255 193)',
                backgroundColor: 'rgba(0, 0, 0, 0.1)',
                borderColor: 'rgb(65,105,225)',
                data: {{ fps_data }}
            }]
        },
        // Configuration options go here
       options: {scales: {yAxes: [{scaleLabel: {display: true, labelString: "FPS"}}]}} 
    });
    const net_chart = new Chart(net_ctx, {
        // The type of chart we want to create
        type: 'line',
        // The data for our dataset
        data: {
            labels: {{ mem_time_labels }},
            datasets: [{
                label: 'TOTAL DOWN NET',
                // backgroundColor: 'rgb(193 255 193)',
                backgroundColor: 'rgba(0, 0, 0, 0.1)',
                borderColor: 'rgb(0,255,255)',
                data: {{ net_total_down_data }}
            },{
                label: 'TOTAL UP NET',
                // backgroundColor: 'rgb(193 255 193)',
                backgroundColor: 'rgba(0, 0, 0, 0.1)',
                borderColor: 'rgb(176,224,230)',
                data: {{ net_total_up_data }}
            }]
        },
        // Configuration options go here
        options: {scales: {yAxes: [{scaleLabel: {display: true, labelString: "KB"}}]}}
    });
</script>
"""

diff_template = """
<!doctype html>
<html>
<head>
    <title>Android性能对比测试结果</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@2.8.0"></script>
    <!-- 最新版本的 Bootstrap 核心 CSS 文件 -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.3.7/dist/css/bootstrap.min.css"
          crossorigin="anonymous">
    <meta name="viewport" content="initial-scale = 1, user-scalable = no">
    <meta charset="UTF-8">
</head>
<body>
<div>
    <table id="start_report" class="table table-bordered table-hover">
        <tr>
            <th>标签(版本号)</th>
            <th>平均CPU使用(%)</th>
            <th>平均Memory使用(MB)</th>
            <th>平均FPS</th>
            <th>平均下行网络使用(KB)</th>
            <th>平均上行网络使用(KB)</th>
            <th>平均电量使用(mAH/S)</th>
            <th>平均启动时间</th>
        </tr>
        {% for data in data_list %}
        <tr>
            <td>{{ data.name }}</td>
            <td>{{ data.cpu }}</td>
            <td>{{ data.mem }}</td>
            <td>{{ data.fps }}</td>
            <td>{{ data.down_net }}</td>
            <td>{{ data.up_net }}</td>
            <td>{{ data.buttery }}</td>
            <td>{{ data.start }}</td>
        </tr>
        {% endfor %}
        </tr>
    </table>
    </table>
</div>

</body>
"""


def get_cpu_data(cpu_file):
    with open(cpu_file) as cpu_f:
        cpu_time_labels = []
        cpu_data = []
        data = csv.DictReader(cpu_f)
        for row in data:
            cpu_time = row["time"]
            rate = row["进程CPU占比(%)"]
            cpu_time_labels.append(cpu_time)
            cpu_data.append(rate)
    return cpu_time_labels, cpu_data


def get_mem_data(mem_file):
    with open(mem_file) as mem_f:
        mem_time_labels = []
        mem_data = []
        data = csv.DictReader(mem_f)
        for row in data:
            mem_time = row["time"]
            mem = row["Native Heap(MB)"]
            mem_time_labels.append(mem_time)
            mem_data.append(mem)
    return mem_time_labels, mem_data


def get_fps_data(fps_file):
    with open(fps_file) as fps_f:
        fps_time_labels = []
        fps_data = []
        data = csv.DictReader(fps_f)
        for row in data:
            fps_time = row["time"]
            fps = float(row["FPS"]) * 0.000000001
            fps_time_labels.append(fps_time)
            fps_data.append(fps)
    return fps_time_labels, fps_data


def get_net_data(net_file):
    with open(net_file) as net_f:
        net_time_labels = []
        net_avg_down_data = []
        net_avg_up_data = []
        net_total_down_data = []
        net_total_up_data = []
        data = csv.DictReader(net_f)
        for row in data:
            net_time = row["time"]
            net_avg_down = float(row["平均下载速度(KB/s)"])
            net_avg_up = float(row["平均上传速度(KB/s)"])
            net_total_down = float(row["下载总流量(KB)"])
            net_total_up = float(row["上传总流量(KB)"])
            net_time_labels.append(net_time)
            net_avg_down_data.append(net_avg_down)
            net_avg_up_data.append(net_avg_up)
            net_total_down_data.append(net_total_down)
            net_total_up_data.append(net_total_up)
    return net_time_labels, net_avg_down_data, net_avg_up_data, net_total_down_data, net_total_up_data


def get_battery_data(battery_file):
    with open(battery_file) as battery_f:
        data = csv.DictReader(battery_f)
        for row in data:
            battery_time = row["time"]
            battery_stats = row["battery(mAh)"]
    return battery_stats, battery_time


def get_start_data(start_file):
    if not start_file:
        return {}
    try:
        with open(start_file) as start_f:
            data = csv.DictReader(start_f)
            for row in data:
                start_data = row
    except:
        start_data = {}
    return start_data


def info_report(app, show_start_report=True):
    if show_start_report:
        show_start_report = "false"
    else:
        show_start_report = "true"
    file_path = new_dir(PATH + "/../info/")
    cpu_file = new_file(file_path + "/cpu_stats/")
    cpu_time_labels, cpu_data = get_cpu_data(cpu_file)
    mem_file = new_file(file_path + "/mem_stats/")
    mem_time_labels, mem_data = get_mem_data(mem_file)
    fps_file = new_file(file_path + "/fps_stats/")
    fps_time_labels, fps_data = get_fps_data(fps_file)
    net_file = new_file(file_path + "/net_stats/")
    net_time_labels, net_avg_down_data, net_avg_up_data, net_total_down_data, net_total_up_data = get_net_data(net_file)
    battery_file = new_file(file_path + "/battery_stats/")
    battery_stats, battery_time = get_battery_data(battery_file)
    try:
        start_file = new_file(file_path + "/start_stats/")
    except:
        start_file = False
    start_data = get_start_data(start_file)
    report = Template(template)
    result = report.render(app=app, cpu_time_labels=cpu_time_labels, cpu_data=cpu_data, mem_time_labels=mem_time_labels,
                           mem_data=mem_data, fps_time_labels=fps_time_labels, fps_data=fps_data,
                           net_total_down_data=net_total_down_data, net_total_up_data=net_total_up_data,
                           battery_time=battery_time, battery_stats=battery_stats, show_start_report=show_start_report,
                           start_data=start_data)
    make_dir(PATH + "/../report/")
    with open(PATH + "/../report/" + app["tag"] + "_" + str(int(time.time())) + "_report.html", "w") as f:
        f.write(result)


def avg_cpu(base_path):
    files = file_list(base_path + "/cpu_stats/")
    cpu_avg_data_list = []
    for file in files:
        cpu_time_labels, cpu_data = get_cpu_data(file)
        cpu_data = nu.average([float(data) for data in cpu_data])
        cpu_avg_data_list.append(cpu_data)
    return nu.average(cpu_avg_data_list)


def avg_mem(base_path):
    files = file_list(base_path + "/mem_stats/")
    mem_avg_data_list = []
    for file in files:
        mem_time_labels, mem_data = get_mem_data(file)
        mem_data = nu.average([float(data) for data in mem_data])
        mem_avg_data_list.append(mem_data)
    return nu.average(mem_avg_data_list)


def avg_fps(base_path):
    files = file_list(base_path + "/fps_stats/")
    fps_avg_data_list = []
    for file in files:
        fps_time_labels, fps_data = get_fps_data(file)
        fps_data = nu.average([float(data) for data in fps_data])
        fps_avg_data_list.append(fps_data)
    return nu.average(fps_avg_data_list)


def avg_net(base_path):
    files = file_list(base_path + "/net_stats/")
    down_avg_data_list = []
    up_avg_data_list = []
    for file in files:
        net_time_labels, net_avg_down_data, net_avg_up_data, net_total_down_data, net_total_up_data = get_net_data(
            file)
        net_total_down_data = nu.average([float(data) for data in net_total_down_data])
        net_total_up_data = nu.average([float(data) for data in net_total_up_data])
        down_avg_data_list.append(net_total_down_data)
        up_avg_data_list.append(net_total_up_data)
    return nu.average(down_avg_data_list), nu.average(up_avg_data_list)


def avg_start(base_path):
    path = base_path + "/start_stats/"
    avg_start_list = []
    if os.path.exists(path):
        files = file_list(path)
        for file in files:
            data = get_start_data(file)
            avg_start_list.append(int(data["avg_start_time"]))
        return nu.average(avg_start_list)
    else:
        return None


def avg_battery(base_path):
    avg_battery_list = []
    files = file_list(base_path + "/battery_stats/")
    for file in files:
        battery_stats, battery_time = get_battery_data(file)
        if battery_stats != "":
            time_battery = float(battery_stats) / float(battery_time)
            avg_battery_list.append(time_battery)
        else:
            avg_battery_list.append(0)
    return nu.average(avg_battery_list)


def tag_info_data(tag_dir_path):
    name = tag_dir_path.split("/")[-1]
    down_net, up_net = avg_net(tag_dir_path)
    return {"name": name, "cpu": avg_cpu(tag_dir_path), "mem": avg_mem(tag_dir_path), "fps": avg_fps(tag_dir_path),
            "buttery": avg_battery(tag_dir_path), "start": avg_start(tag_dir_path), "down_net": down_net,
            "up_net": up_net}


def diff_report(path_list=None):
    if path_list is None:
        the_dif_list = dir_list(PATH + "/../info/")
        path_list = the_dif_list[-2:]
    name_list = []
    data_list = []
    for path in path_list:
        data = tag_info_data(path)
        name = data["name"]
        data_list.append(data)
        name_list.append(name)
    report = Template(diff_template)
    result = report.render(data_list=data_list)
    make_dir(PATH + "/../report/")
    base_name = "_".join(name_list)
    with open(PATH + "/../report/" + base_name + "_" + str(int(time.time())) + "_report.html",
              "w") as f:
        f.write(result)


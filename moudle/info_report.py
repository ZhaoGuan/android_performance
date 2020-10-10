#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
from jinja2 import Template
import os
import csv
import time

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
<canvas id="cpuChart"></canvas>
<canvas id="memoryChart"></canvas>
<canvas id="fpsChart"></canvas>
<canvas id="netChart"></canvas>
<div>
    <table class="table table-bordered table-hover">
        <tr>
            <th>耗电量</th>
        </tr>

        <tr>
            <td>{{ battery_stats }} mAH</td>
        </tr>
    </table>
</div>

</body>
<script>
    const wh = document.body.clientHeight;
    const cpuChart = document.getElementById('cpuChart');
    const memoryChart = document.getElementById('memoryChart');
    const fpsChart = document.getElementById('fpsChart');
    const netChart = document.getElementById('netChart');
    cpuChart.height = wh / 2;
    memoryChart.height = wh / 2;
    fpsChart.height = wh / 2;
    netChart.height = wh / 2;
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


def make_dir(dirs):
    if not os.path.exists(dirs):
        os.makedirs(dirs)


def new_file(path):
    file_lists = os.listdir(path)
    file_lists.sort(key=lambda fn: os.path.getmtime(path + fn)
    if not os.path.isdir(path + fn) else 0)
    return path + file_lists[-1]


def info_report():
    file_path = PATH + "/../info/"
    cpu_file = new_file(file_path + "cpu_stats/")
    with open(cpu_file) as cpu_f:
        cpu_time_labels = []
        cpu_data = []
        data = csv.DictReader(cpu_f)
        for row in data:
            cpu_time = row["time"]
            rate = row["进程CPU占比(%)"]
            cpu_time_labels.append(cpu_time)
            cpu_data.append(rate)
    mem_file = new_file(file_path + "mem_stats/")
    with open(mem_file) as mem_f:
        mem_time_labels = []
        mem_data = []
        data = csv.DictReader(mem_f)
        for row in data:
            mem_time = row["time"]
            mem = row["Native Heap(MB)"]
            mem_time_labels.append(mem_time)
            mem_data.append(mem)
    fps_file = new_file(file_path + "fps_stats/")
    with open(fps_file) as fps_f:
        fps_time_labels = []
        fps_data = []
        data = csv.DictReader(fps_f)
        for row in data:
            fps_time = row["time"]
            fps = float(row["FPS"]) * 0.000000001
            fps_time_labels.append(fps_time)
            fps_data.append(fps)
    net_file = new_file(file_path + "net_stats/")
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
    report = Template(template)
    battery_file = new_file(file_path + "battery_stats/")
    with open(battery_file) as battery_f:
        data = csv.DictReader(battery_f)
        for row in data:
            battery_stats = row["battery(mAh)"]
    result = report.render(cpu_time_labels=cpu_time_labels, cpu_data=cpu_data, mem_time_labels=mem_time_labels,
                           mem_data=mem_data, fps_time_labels=fps_time_labels, fps_data=fps_data,
                           net_avg_down_data=net_avg_down_data, net_avg_up_data=net_avg_up_data,
                           net_total_down_data=net_total_down_data, net_total_up_data=net_total_up_data,
                           battery_stats=battery_stats)
    make_dir(PATH + "/../report/")
    with open(PATH + "/../report/" + str(int(time.time())) + "_report.html", "w") as f:
        f.write(result)


if __name__ == "__main__":
    info_report()

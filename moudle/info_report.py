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
    <meta name="viewport" content="initial-scale = 1, user-scalable = no">
    <meta charset="UTF-8">
</head>
<body>
<canvas id="cpuChart"></canvas>
<canvas id="memoryChart"></canvas>
</body>
<script>
    const wh = document.body.clientHeight;
    const cpuChart = document.getElementById('cpuChart');
    const memoryChart = document.getElementById('memoryChart');
    cpuChart.height = wh / 2;
    memoryChart.height = wh / 2;
    const cpu_ctx = cpuChart.getContext('2d');
    const mem_ctx = memoryChart.getContext('2d');
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
        options: {}
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
        options: {}
    });
</script>
"""


def new_file(path):
    file_lists = os.listdir(path)
    file_lists.sort(key=lambda fn: os.path.getmtime(path + fn)
    if not os.path.isdir(path + fn) else 0)
    return path + file_lists[-1]


def info_report():
    cpu_file = new_file(PATH + "/../info/cpu_stats/")
    with open(cpu_file) as cpu_f:
        cpu_time_labels = []
        cpu_data = []
        data = csv.DictReader(cpu_f)
        for row in data:
            cpu_time = row["time"]
            rate = row["进程CPU占比(%)"]
            cpu_time_labels.append(cpu_time)
            cpu_data.append(rate)
    mem_file = new_file(PATH + "/../info/mem_stats/")
    with open(mem_file) as mem_f:
        mem_time_labels = []
        mem_data = []
        data = csv.DictReader(mem_f)
        for row in data:
            mem_time = row["time"]
            mem = row["Native Heap(MB)"]
            mem_time_labels.append(mem_time)
            mem_data.append(mem)
    report = Template(template)
    result = report.render(cpu_time_labels=cpu_time_labels, cpu_data=cpu_data, mem_time_labels=mem_time_labels,
                           mem_data=mem_data)
    with open(PATH + "/../report/" + str(int(time.time())) + "_report.html", "w") as f:
        f.write(result)


if __name__ == "__main__":
    info_report()

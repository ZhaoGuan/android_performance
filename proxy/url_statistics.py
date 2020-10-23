#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
from mitmproxy import http
from jinja2 import Template
import csv
import os
import time
import yaml
import json

PATH = os.path.dirname(os.path.abspath(__file__))
info_path = os.path.abspath(PATH + "/../info")
recording_path = os.path.abspath(info_path + "/recording/")
report_path = os.path.abspath(info_path + "/../report/")
template = '''
<!DOCTYPE html>
<html lang="zh">

<head>
    <meta charset="UTF-8">
    <title>Url Statistics Report</title>
    <!-- 最新版本的 Bootstrap 核心 CSS 文件 -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.3.7/dist/css/bootstrap.min.css" crossorigin="anonymous">

    <style>
        table {
            margin: 0 auto;
            word-wrap: break-word;
            word-break: break-all;
        }

        .danger {
            color: #d9534f;
        }
        /* body {
            width: 80%;
            margin: 0 auto;
        } */
    </style>
</head>

<body >
    <!-- <details> -->
        <table class="table table-bordered table-hover">
            <tr>
                <th>时间</th>
                <th>url</th>
                <th>方法</th>
                <th>状态码</th>
                <th>大小 b</th>
                <th>响应时间 ms</th>
            </tr>

            {% for data in data_list %}
            <tr>
                <td>{{data.time}}</td>
                <td width="70%">
                    <a href={{data.url}}>{{data.url}}</a>
                </td>
                <td>{{data.method}}</td>
                <td class={{ data.status_code.class }} >{{data.status_code.data}}</td>
                <td>{{data.response_size}}</td>
                <td class={{ data.spend_time.class }} >{{data.spend_time.data}}</td>
            </tr>
            {% endfor %}
        </table>
    <!-- </details> -->
</body>

</html>
'''


def make_dir(dirs):
    if not os.path.exists(dirs):
        os.makedirs(dirs)


def make_file(path):
    if not os.path.exists(path):
        open(path, "w")


def new_dir(path):
    return dir_list(path)[-1]


def dir_list(path):
    if path[-1] != "/":
        path += "/"
    dir_lists = os.listdir(path)
    dir_lists.sort(key=lambda fn: os.path.getmtime(path + fn) if not os.path.isdir(path + fn) else 0, reverse=False)
    dir_lists = [path + the_dir for the_dir in dir_lists]
    return dir_lists


def make_report():
    make_dir(report_path)
    result = []
    new_path = new_dir(recording_path)
    with open(new_path)as f:
        data = csv.DictReader(f)
        for row in data:
            print(row)
            status_code = row["status_code"]
            response_header = row["response_header"]
            if 'json' in str(response_header):
                response = json.loads(row["response_body"])
                if "code" in response.keys() and str(response["code"]) != "1000":
                    code_result = True
                else:
                    code_result = False
            else:
                code_result = False
            if status_code[0] not in ["2", "3"] or code_result:
                status_code_class = "danger"
            else:
                status_code_class = ""
            spend_time = int(row["spend_time"])
            if spend_time > 200:
                the_class = "danger"
            else:
                the_class = ""
            row["status_code"] = {"class": status_code_class, "data": status_code}
            row["spend_time"] = {"class": the_class, "data": spend_time}
            result.append(row)
    report = Template(template)
    result = report.render(data_list=result)
    with open(report_path + "/" + str(int(time.time())) + "_url_report.html", "w") as f:
        f.write(result)


class UrlStatistics:
    def __init__(self):
        make_dir(info_path)
        make_dir(recording_path)
        make_file(PATH + "/config.yml")
        self.file_name = str(int(time.time())) + "_data"
        self.file_path = recording_path + "/" + self.file_name + ".csv"
        self.f = open(self.file_path, "w")
        self.writer = csv.DictWriter(self.f,
                                     fieldnames=["time", "url", "status_code", "method", "response_size", "spend_time",
                                                 "response_header", "response_body"])
        self.writer.writeheader()
        with open(PATH + "/config.yml") as f:
            self.config = yaml.safe_load(f)
        if self.config is None:
            self.config = []

    def response(self, flow: http.HTTPFlow):
        the_time = time.strftime("%H:%M:%S")
        request_host = flow.request.host
        method = flow.request.method
        url = flow.request.url
        response_body = flow.response.text
        response_header = json.dumps(dict(flow.response.headers))
        status_code = flow.response.status_code
        spend_time = int((flow.response.timestamp_end - flow.request.timestamp_start) * 1000)
        response_size = len(flow.response.raw_content) if flow.response.raw_content else 0
        if not self.config:
            data = {"time": the_time, "url": url, "status_code": status_code,
                    "method": method, "response_size": response_size, "spend_time": spend_time,
                    "response_body": response_body, "response_header": response_header}
            self.writer.writerow(data)
        else:
            for i in self.config:
                if i in request_host:
                    data = {"url": url, "status_code": status_code,
                            "method": method, "response_size": response_size, "spend_time": spend_time,
                            "response_body": response_body, "response_header": response_header}
                    self.writer.writerow(data)

    def done(self):
        self.f.close()
        make_report()


if __name__ == "__main__":
    make_report()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
import base64
import typing
from datetime import datetime
from datetime import timezone

import numpy
from mitmproxy import http
from jinja2 import Environment, FileSystemLoader, select_autoescape

import os
import time
import yaml
import json
from mitmproxy.utils import strutils
from mitmproxy import version

from moudle.utils import MOUDLE_PATH
from proxy.hardump import format_response_cookies, name_value, format_request_cookies
from urllib.parse import urlparse

PATH = os.path.dirname(os.path.abspath(__file__))
INFO_PATH = os.path.abspath(PATH + "/../info")
recording_path = os.path.abspath(INFO_PATH + "/recording/")
report_path = os.path.abspath(PATH + "/../report/")

JINJA2_ENV = Environment(loader=FileSystemLoader(PATH + "/template"))
JINJA2_ENV.variable_start_string = '{['  # 修改块开始符号
JINJA2_ENV.variable_end_string = ']}'
time_template = open(PATH + "/template/http_url_time_report.html").read()


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
    dir_lists.remove(".DS_Store")
    dir_lists = [path + the_dir for the_dir in dir_lists]
    return dir_lists


def http_row_data(data):
    request = data.get("request", {})
    response = data.get("response", {})
    data["startedDateTime"] = data["startedDateTime"].split(".")[0]
    data.update({"url": request.get("url", "")})
    data.update({"spend_time": format(data.get("time", 0) * 1000, '.2f')})
    data.update({"method": request.get("method", "")})
    data.update({"status_code": response.get("status", "")})
    data.update({"body_size": response.get("bodySize", 0)})
    return data


# 时序详情内容
def make_url_time_report():
    make_dir(report_path)
    result = []
    new_path = new_dir(recording_path)
    with open(new_path) as f:
        for index, data in enumerate(f.readlines()):
            row = http_row_data(json.loads(data))
            result.append(row)
    report = JINJA2_ENV.get_template("http_url_time_report.html")
    result = report.render(data_list=json.dumps(result, ensure_ascii=False))
    report_name = report_path + "/" + str(new_path.split("/")[-1].replace("_data.txt", "")) + "_url_report.html"
    with open(report_name, "w") as f:
        f.write(result)
    return report_name


def file_all_data(path):
    result = []
    for path in dir_list(path):
        with open(path) as f:
            result += f.readlines()
    return result


# 时间 参数
def make_url_statistics_report():
    make_dir(report_path)
    all_data = file_all_data(recording_path)
    temp_result = {}
    for index, data in enumerate(all_data):
        row = http_row_data(json.loads(data))
        url = row["url"]
        url_result = urlparse(url)
        host = url_result.hostname
        path = url_result.path
        scheme = url_result.scheme
        cost_time = float(row["spend_time"])
        body_size = row["body_size"]
        method = row["method"]
        tag = path + "|" + scheme + "|" + method
        if host_data := temp_result.get(host, None):
            if path_data := host_data.get(tag, None):
                path_data["cost_time"].append(cost_time)
                path_data["body_size"].append(body_size)
                path_data["path"] = path
                path_data["method"] = method
                path_data["scheme"] = scheme
            else:
                host_data.update({tag: {
                    "cost_time": [cost_time],
                    "body_size": [body_size],
                    "path": path,
                    "method": method,
                    "scheme": scheme
                }})
        else:
            temp_result.update({host:
                {tag: {
                    "cost_time": [cost_time],
                    "body_size": [body_size],
                    "path": path,
                    "method": method,
                    "scheme": scheme
                }}})
    result = {}
    for host, host_data in temp_result.items():
        temp_host_data = []
        for path, path_data in host_data.items():
            temp_host_data.append({
                "cost_time": format(numpy.mean(path_data["cost_time"]), '.2f'),
                "body_size": format(numpy.mean(path_data["body_size"]), '.2f'),
                "path": path_data["path"],
                "method": path_data["method"],
                "scheme": path_data["scheme"],
                "count": len(path_data["cost_time"])
            })
        result.update({host: temp_host_data})
    report = JINJA2_ENV.get_template("http_url_statistics_report.html")
    result = report.render(data_list=json.dumps(result, ensure_ascii=False))
    report_name = report_path + "/" + str("url_statistics_report.html")
    with open(report_name, "w") as f:
        f.write(result)
    return report_name


def make_har():
    make_dir(report_path)
    HAR: typing.Dict = {}
    HAR.update({
        "log": {
            "version": "1.2",
            "creator": {
                "name": "mitmproxy har_dump",
                "version": "0.1",
                "comment": "mitmproxy version %s" % version.MITMPROXY
            },
            "entries": []
        }
    })
    new_path = new_dir(recording_path)
    with open(new_path) as f:
        for entry in f.readlines():
            HAR["log"]["entries"].append(json.loads(entry))
    report_name = report_path + "/" + str(new_path.split("/")[-1].replace("_data.txt", "")) + "_data.har"
    with open(report_name, "w") as f:
        f.write(json.dumps(HAR, ensure_ascii=False, indent=2))
    return report_name


class UrlStatistics:
    def __init__(self):
        make_dir(INFO_PATH)
        make_dir(recording_path)
        make_file(PATH + "/config.yml")
        self.file_name = str(int(time.time())) + "_data"
        self.file_path = recording_path + "/" + self.file_name + ".txt"
        self.f = open(self.file_path, "w")
        self.writer = self.f
        with open(PATH + "/config.yml") as f:
            self.config = yaml.safe_load(f)
        if self.config is None:
            self.config = []

    def check_host(self, request_host):
        if not self.config:
            return True
        for i in self.config:
            if i in request_host:
                return True
            else:
                return False

    def _response(self, flow: http.HTTPFlow):
        the_time = time.strftime("%Y-%m-%d_%H:%M:%S")
        request_host = flow.request.host
        if "json" in str(dict(flow.request.headers)):
            request_body = str(flow.request.get_text(strict=False))
        else:
            request_body = None
        request_headers = dict(flow.request.headers)
        request_query = dict(flow.request.query)
        method = flow.request.method
        url = flow.request.url
        path = flow.request.path
        dict_response_header = dict(flow.response.headers)
        # json
        if "json" in str(dict(flow.response.headers)):
            response_type = "json"
            response_body = str(flow.response.get_text(strict=False))
        else:
            response_type = "other"
            response_body = None
        response_header = json.dumps(dict_response_header)
        status_code = flow.response.status_code
        spend_time = int((flow.response.timestamp_end - flow.request.timestamp_start) * 1000)
        response_size = len(flow.response.raw_content) if flow.response.raw_content else 0
        save_data = {"time": the_time,
                     "host": request_host,
                     "url": url,
                     "path": path,
                     "request_headers": request_headers,
                     "request_query": request_query,
                     "request_body": request_body,
                     "status_code": status_code,
                     "method": method,
                     "response_size": response_size,
                     "spend_time": spend_time,
                     "response_type": response_type,
                     "response_body": response_body,
                     "response_header": response_header}
        if self.check_host(request_host):
            self.writer.writerow(save_data)

    def response(self, flow: http.HTTPFlow):
        import typing  # noqa
        from mitmproxy import connection
        SERVERS_SEEN: typing.Set[connection.Server] = set()
        ssl_time = -1
        connect_time = -1

        if flow.server_conn and flow.server_conn not in SERVERS_SEEN:
            connect_time = (flow.server_conn.timestamp_tcp_setup -
                            flow.server_conn.timestamp_start)

            if flow.server_conn.timestamp_tls_setup is not None:
                ssl_time = (flow.server_conn.timestamp_tls_setup -
                            flow.server_conn.timestamp_tcp_setup)

            SERVERS_SEEN.add(flow.server_conn)
        response_body_size = len(flow.response.raw_content) if flow.response.raw_content else 0
        response_body_decoded_size = len(flow.response.content) if flow.response.content else 0
        response_body_compression = response_body_decoded_size - response_body_size
        # started_date_time = datetime.fromtimestamp(flow.request.timestamp_start, timezone.utc).isoformat()
        # 本地时间
        started_date_time = datetime.fromtimestamp(flow.request.timestamp_start).isoformat()
        timings = {
            'send': flow.request.timestamp_end - flow.request.timestamp_start,
            'receive': flow.response.timestamp_end - flow.response.timestamp_start,
            'wait': flow.response.timestamp_start - flow.request.timestamp_end,
            'connect': connect_time,
            'ssl': ssl_time,
        }
        full_time = sum(v for v in timings.values() if v > -1)
        entry = {
            "startedDateTime": started_date_time,
            "time": full_time,
            "request": {
                "method": flow.request.method,
                "url": flow.request.url,
                "httpVersion": flow.request.http_version,
                "cookies": format_request_cookies(flow.request.cookies.fields),
                "headers": name_value(flow.request.headers),
                "queryString": name_value(flow.request.query or {}),
                "headersSize": len(str(flow.request.headers)),
                "bodySize": len(flow.request.content),
            },
            "response": {
                "status": flow.response.status_code,
                "statusText": flow.response.reason,
                "httpVersion": flow.response.http_version,
                "cookies": format_response_cookies(flow.response.cookies.fields),
                "headers": name_value(flow.response.headers),
                "content": {
                    "size": response_body_size,
                    "compression": response_body_compression,
                    "mimeType": flow.response.headers.get('Content-Type', '')
                },
                "redirectURL": flow.response.headers.get('Location', ''),
                "headersSize": len(str(flow.response.headers)),
                "bodySize": response_body_size,
            },
            "cache": {},
            "timings": timings,
        }

        # Store binary data as base64
        if strutils.is_mostly_bin(flow.response.content):
            entry["response"]["content"]["text"] = base64.b64encode(flow.response.content).decode()
            entry["response"]["content"]["encoding"] = "base64"
        else:
            entry["response"]["content"]["text"] = flow.response.get_text(strict=False)

        if flow.request.method in ["POST", "PUT", "PATCH"]:
            params = [
                {"name": a, "value": b}
                for a, b in flow.request.urlencoded_form.items(multi=True)
            ]
            entry["request"]["postData"] = {
                "mimeType": flow.request.headers.get("Content-Type", ""),
                "text": flow.request.get_text(strict=False),
                "params": params
            }
        if flow.server_conn.connected:
            entry["serverIPAddress"] = str(flow.server_conn.ip_address[0])
        self.f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def done(self):
        self.f.close()


if __name__ == "__main__":
    make_url_statistics_report()
    make_url_time_report()
    make_har()

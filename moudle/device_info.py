#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
from moudle.info import CPUInfo, MemInfo, FPSInfo, NetInfo, LogCatInfo
from moudle.info_task import InfoTask
from moudle.task import Task
import os
import subprocess

PATH = os.path.dirname(os.path.abspath(__file__))


def run_command(command):
    p_obj = subprocess.Popen(
        args="adb shell " + command,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, shell=True, encoding="utf-8")
    result = p_obj.stdout.read()
    return result


def app_pid(package_name):
    result = run_command("ps |grep %s| awk '{ print $2 }'" % package_name).replace("\n", " ")
    result_list = result.split(" ")
    return result_list[0]


class DeviceInfoRun:
    def __init__(self, package_name):
        task = Task("myTest")
        task.shell = run_command
        task.pid = app_pid(package_name=package_name)
        task.interval = 1
        task.output = PATH + "/../info"
        task.add_info(CPUInfo())
        task.add_info(MemInfo())
        task.add_info(FPSInfo())
        task.add_info(NetInfo())
        task.add_info(LogCatInfo())
        self.info_task = InfoTask(task)

    def start(self):
        self.info_task.start()

    def end(self):
        self.info_task.end()

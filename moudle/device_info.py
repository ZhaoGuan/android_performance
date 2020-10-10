#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
from moudle.info import CPUInfo, MemInfo, FPSInfo, NetInfo, LogCatInfo, BatteryCatInfo
from moudle.info_task import InfoTask
from moudle.task import Task
from moudle.utils import run_command
import os

PATH = os.path.dirname(os.path.abspath(__file__))


def app_pid(package_name):
    result = run_command("ps |grep %s| awk '{ print $2 }'" % package_name).replace("\n", " ")
    result_list = result.split(" ")
    return result_list[0]


def app_uid(package_name):
    result = run_command("ps |grep %s| awk '{ print $1 }'" % package_name).replace("\n", " ")
    result_list = result.split(" ")
    return result_list[0]


class DeviceInfoRun:
    def __init__(self, package_name):
        task = Task("myTest")
        task.shell = run_command
        task.pid = app_pid(package_name=package_name)
        task.uid = app_uid(package_name=package_name)
        task.interval = 1
        task.output = PATH + "/../info"
        task.add_info(CPUInfo())
        task.add_info(MemInfo())
        task.add_info(FPSInfo())
        task.add_info(NetInfo())
        task.add_info(LogCatInfo())
        task.add_info(BatteryCatInfo())
        self.info_task = InfoTask(task)

    def start(self):
        self.info_task.start()

    def end(self):
        self.info_task.end()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
from moudle.performance.info import CPUInfo, MemInfo, FPSInfo, NetInfo, LogCatInfo, BatteryCatInfo
from moudle.performance.info_task import InfoTask
from moudle.performance.task import Task, AndroidTask
from moudle.utils import run_command, new_dir, make_dir, ADB
import os

PATH = os.path.dirname(os.path.abspath(__file__))
info_dir_path = os.path.abspath(PATH + "/../../info/")


class DeviceInfoRun:
    def __init__(self, the_version_name, package_name, duid=None):
        make_dir(info_dir_path)
        make_dir(os.path.abspath(info_dir_path + "/" + str(the_version_name)))
        task = AndroidTask(package_name, duid)
        task.shell = run_command
        task.interval = 2
        task.output = new_dir(info_dir_path)
        task.add_info(CPUInfo())
        task.add_info(MemInfo())
        task.add_info(FPSInfo())
        task.add_info(NetInfo())
        task.add_info((BatteryCatInfo()))
        self.info_task = InfoTask(task)

    def start(self):
        self.info_task.start()

    def end(self):
        self.info_task.end()

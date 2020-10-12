#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
from moudle.utils import run_command, get_csv_writer
import re
import numpy
import os

PATH = os.path.dirname(os.path.abspath(__file__))


class AppStart:
    def __init__(self, package_name, start_activity, run_time=5):
        self.package_name = package_name
        self.start_activity = start_activity
        self.run_time = run_time
        self.start_time_list = []

    def start_time(self):
        result = run_command('am start -W ' + self.package_name + '/' + self.start_activity + "| grep WaitTime")
        res = re.search(r"WaitTime:\s+(?P<cost_time>[^\s]+)\n", result)
        cost_time = res.groupdict()["cost_time"]
        return int(cost_time)

    def stop_app(self):
        run_command('am force-stop ' + self.package_name)

    def run(self):
        for i in range(0, self.run_time):
            self.stop_app()
            self.start_time_list.append(self.start_time())
        self.start_time_list.sort()
        new_list = self.start_time_list[1:-1]
        avg_start_time = int(numpy.average(new_list))
        dirs = PATH + "/../info/start_stats/"
        file_name = "start"
        field_names = ["package_name", "start_activity", "run_time", "avg_start_time"]
        writer = get_csv_writer(dirs, file_name, field_names)
        writer.writerow(
            {"package_name": self.package_name, "start_activity": self.start_activity, "run_time": self.run_time,
             "avg_start_time": avg_start_time})
        return avg_start_time


if __name__ == "__main__":
    ast = AppStart("com.yiding.jianhuo", "com.yiding.jianhuo.SplashActivity")
    print(ast.run())

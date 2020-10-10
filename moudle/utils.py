import csv
import os
import re
import time

the_time = time.time()


def get_csv_writer(dirs, file_name, field_names):
    if not os.path.exists(dirs):
        os.makedirs(dirs)
    file_path = dirs + file_name + "_" + format(the_time, ".0f") + ".csv"
    mem_csv = open(file_path, 'w', newline='', encoding="UTF-8")
    writer = csv.DictWriter(mem_csv, fieldnames=field_names)
    writer.writeheader()
    return writer


def get_log_writer(dirs, file_name):
    if not os.path.exists(dirs):
        os.makedirs(dirs)
    file_path = dirs + file_name + "_" + format(the_time, ".0f") + ".log"
    writer = open(file_path, 'w', newline='', encoding="UTF-8")
    return writer


def get_action_writer(dirs, file_name, field_names):
    if not os.path.exists(dirs):
        os.makedirs(dirs)
    file_path = dirs + file_name + "_" + format(the_time, ".0f") + ".csv"
    mem_csv = open(file_path, 'w', newline='', encoding="UTF-8")
    writer = csv.DictWriter(mem_csv, fieldnames=field_names)
    writer.writeheader()
    return writer


def get_applicationid_by_pid(d, pid):
    ps_info = re.findall("\S+", d._adb_shell("ps | grep " + pid))
    return ps_info[len(ps_info) - 1]


def get_pid_by_applicationid(d, applicationid):
    ps_info = re.findall("\S+", d._adb_shell("ps | grep " + applicationid))
    return ps_info[1]


def get_version_name_by_applicationid(d, applicationid):
    version_info = d._adb_shell("dumpsys package " + applicationid + " | grep versionName")
    return re.findall("\d+.+\d", version_info)[0]

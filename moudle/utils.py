import multiprocessing

multiprocessing.freeze_support()
import csv
import os
import re
import time
import subprocess
import sys
from mitmproxy.tools.main import mitmweb

the_time = time.time()
MOUDLE_PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.dirname(os.path.abspath(__file__))


def make_dir(dirs):
    if not os.path.exists(dirs):
        os.makedirs(dirs)


def new_file(path):
    '''
    不能用查询文件夹
    :param path:
    :return:
    '''
    return file_list(path)[-1]


def file_list(path):
    if path[-1] != "/":
        path += "/"
    file_lists = os.listdir(path)
    file_lists.sort(key=lambda fn: os.path.getmtime(path + fn)
    if not os.path.isdir(path + fn) else 0, reverse=False)
    file_lists = [path + file for file in file_lists]
    return file_lists


def new_dir(path):
    return dir_list(path)[-1]


def dir_list(path):
    if path[-1] != "/":
        path += "/"
    dir_lists = os.listdir(path)
    dir_lists.sort(key=lambda fn: os.path.getmtime(path + fn)
    if os.path.isdir(path + fn) else 0, reverse=False)
    dir_lists = [path + the_dir for the_dir in dir_lists]
    return dir_lists


def run_command(command):
    p_obj = subprocess.Popen(
        args="adb shell " + command,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, shell=True, encoding="utf-8")
    result = p_obj.stdout.read()
    return result


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


def get_applicationid_by_pid(pid):
    ps_info = re.findall("\S+", run_command("ps | grep " + pid))
    return ps_info[len(ps_info) - 1]


def get_pid_by_applicationid(applicationid):
    ps_info = re.findall("\S+", run_command("ps | grep " + applicationid))
    return ps_info[1]


def get_version_name_by_applicationid(applicationid):
    version_info = run_command("dumpsys package " + applicationid + " | grep versionName")
    return re.findall("\d+.+\d", version_info)[0]


def get_devices_name():
    return run_command("getprop ro.product.model")


def run_proxy(port):
    script_path = os.path.abspath(PATH + "/../proxy/proxy_run.py")
    sys.argv = ["", "-p", str(port), "-s", script_path]
    try:
        multiprocessing.set_start_method("fork")
    except:
        pass
    running = multiprocessing.Process(target=mitmweb)
    running.daemon = True
    running.start()
    pid = running.pid
    return running, pid

import multiprocessing

multiprocessing.freeze_support()
import csv
import os
import re
import time
import subprocess
import sys
import yaml
from mitmproxy.tools.main import mitmweb
from ppadb.client import Client as AdbClient

the_time = time.time()
MOUDLE_PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.dirname(os.path.abspath(__file__))


class MetaSingleton(type):
    __instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            cls.__instances[cls] = super(MetaSingleton, cls).__call__()
        return cls.__instances[cls]


class ADB(metaclass=MetaSingleton):
    adb_client = None
    device = None

    def __init__(self):
        if self.adb_client is None:
            self.adb_client = AdbClient()
        self.duid_list = [device.serial for device in self.adb_client.devices()]

    def shell(self, cmd, duid=None):
        assert len(self.duid_list) > 0, "未发现可用设备"
        if duid is None:
            if self.device is None:
                self.device = self.adb_client.device(self.duid_list[0])
        else:
            if duid not in self.duid_list:
                assert False, f"没有所指定设备{duid}"
            else:
                self.device = self.adb_client.device(duid)
        return self.device.shell(cmd)


def config_reader(yaml_file):
    yf = open(yaml_file)
    yx = yaml.safe_load(yf)
    yf.close()
    return yx


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
    file_lists.sort(key=lambda fn: os.path.getctime(path + fn)
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


def run_command(command, duid=None):
    adb = ADB()
    result = adb.shell(cmd=command, duid=duid)
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


def android_get_application_id_by_pid(pid, duid=None):
    ps_info = re.findall("\S+", run_command("ps | grep " + pid, duid))
    return ps_info[len(ps_info) - 1]


def android_get_pid_by_application_id(application_id, duid):
    ps_info = re.findall("\S+", run_command("ps | grep " + application_id, duid))
    return ps_info[1]


def android_get_version_name_by_application_id(application_id, duid=None):
    version_info = run_command("dumpsys package " + application_id + " | grep versionName", duid)
    return re.findall("\d+.+\d", version_info)[0]


def android_get_devices_name(duid=None):
    return run_command("getprop ro.product.model", duid).replace("\n", "")


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

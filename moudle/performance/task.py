import time
from moudle.utils import ADB


class Task(object):
    def __init__(self):
        self.period = None
        self.d = None
        self.applicationid = None
        self.version_name = None
        self.interval = None
        self.output = None
        self.info_list = set([])
        self.shell = None

    def execute(self):
        pass

    def add_info(self, info):
        self.info_list.add(info)
        info.task = self

    def set_device(self, d):
        self.d = d


class AndroidTask(Task):
    def __init__(self, package_name, duid):
        self.base_shell = ADB()
        self.duid = duid
        self.package_name = package_name
        self.pid = self.get_pid()
        self.uid = self.get_uid()
        super().__init__()

    def shell(self, cmd):
        return self.base_shell.shell(cmd, duid=self.duid)

    def get_pid(self):
        return self.base_shell.get_pid(self.package_name, self.duid)

    def get_uid(self):
        result = self.shell("ps |grep %s| awk '{ print $1 }'" % self.package_name).replace("\n", " ")
        result_list = result.split(" ")
        return result_list[0]

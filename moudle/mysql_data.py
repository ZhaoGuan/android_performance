#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
import pymysql
import os
from moudle.utils import config_reader

PATH = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.abspath(PATH + "/..") + "/mysql_config.yml"


class DataBase:
    def __init__(self):
        QA_DB_CONFIG = config_reader(config_path)
        ip = QA_DB_CONFIG["ip"]
        user = QA_DB_CONFIG["user"]
        password = QA_DB_CONFIG["password"]
        database = QA_DB_CONFIG["database"]
        self.db = pymysql.connect(host=ip, user=user, password=password, database=database)
        self.cursor = self.db.cursor()
        self.time_out = 18000
        self.create_table()

    def create_table(self):
        sql = '''CREATE TABLE `android_performance` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `tag` varchar(11) DEFAULT NULL,
  `avg_cpu` float DEFAULT NULL,
  `avg_mem` float DEFAULT NULL,
  `avg_battery` float DEFAULT NULL,
  `avg_start_app` float DEFAULT NULL,
  `upload_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;'''
        try:
            # 执行sql语句
            self.cursor.execute(sql)
            # 执行sql语句
            self.db.commit()
        except Exception as e:
            print("SQL ERROR:", e)
            # 发生错误时回滚
            self.db.rollback()

    def insert_data(self, app, avg_cpu, avg_mem, battery_stats, battery_time, avg_battery, avg_start_app):
        '''{'package_name': 'com.yiding.jianhuo', 'tag': '3.6.5', 'device': 'CLT-AL00'}'''
        tag = app["tag"]
        package_name = app['package_name']
        device = app['device']
        sql = "INSERT INTO android_performance" \
              "(tag,avg_cpu,avg_mem, battery_stats, battery_time,avg_battery,avg_start_app,package_name,device) " \
              "VALUES ('%s',%s,%s,%s,%s,%s,%s,'%s','%s')" \
              % (tag, avg_cpu, avg_mem, battery_stats, battery_time, avg_battery, avg_start_app, package_name, device)
        print(sql)
        try:
            # 执行sql语句
            self.cursor.execute(sql)
            # 执行sql语句
            self.db.commit()
            print("数据库连接正常并创建数据表格:android_performance")
            return True
        except Exception as e:
            # print("SQL ERROR:", e)
            print("数据库连接正常且已经有数据表")
            # 发生错误时回滚
            self.db.rollback()
            return False

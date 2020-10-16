#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
from proxy.url_statistics import UrlStatistics
import os

PATH = os.path.dirname(os.path.abspath(__file__))

addons = [
    UrlStatistics()
]

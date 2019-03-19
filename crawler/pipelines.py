# -*- coding: utf-8 -*-
import pymysql.cursors
from scrapy.exceptions import DropItem
from scrapy import signals
from datetime import datetime
from .MachineManager import *
from urllib3.util import parse_url
import random

#Receiver 추가 - Jeongsam / 2019.02.10
from .sender import ScrapySender


class CrawlerPipeline(object):

    def __init__(self):
        pass

    """
        When spider is created, called.
    """
    def open_spider(self, spider):
        pass

    @classmethod
    def from_crawler(cls, crawler):
        ins = cls()
        crawler.signals.connect(ins.customize_close_spider, signal=signals.spider_closed)
        return ins

    """
    크롤링이 끝날 때 호출되는 함수
    크롤링 목적 url 및 크롤링 메타에 대한 정보를 db 주입
    """
    def customize_close_spider(self, **kwargs):
        """
            You can customize close_spider method. This method is called when spider is close. so you can get close-reason.
        """
        pass

    """
     When item is yield, called.
    """
    def process_item(self, item, spider):
        pass
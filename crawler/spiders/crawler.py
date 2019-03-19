# -*- coding: utf-8 -*-
import scrapy
import scrapy.linkextractors as lnk
from ..items import Item
from scrapy_splash import SplashRequest
import urllib3.connectionpool
from urllib3.util import parse_url
from datetime import datetime
from dateutil.relativedelta import relativedelta
from scrapy.spiders import Rule, CrawlSpider

class crawler(CrawlSpider):
    name = 'crawler'
    allowed_domains = []
    start_urls = []
    rules = [
        Rule(
            lnk.LinkExtractor(
                canonicalize=True,
                unique=True,
            ),
            follow=True,
            callback="parse_items",
        )
    ]

    def __init__(self, url, Depth, MaxRunningTime):
        self.start_time = datetime.now()
        self.seen = set()
        self.DOMAIN = url
        self.Depth = Depth
        self.MaxRunningTime = MaxRunningTime
        self.start_urls.append(url)
        self.allowed_domains.append(parse_url(url).host.replace("www.", "")[:3])
        self.extension()
        self.meta = None
        self.end_time = None
        self.run_time = None
        self.error_count = 0
        self._compile_rules()

    """
        This method extends type of link that is crawled.
    """
    def extension(self):
        lnk.IGNORED_EXTENSIONS = [
            # images
            'mng', 'pct', 'bmp', 'gif', 'jpg', 'jpeg', 'png', 'pst', 'psp', 'tif',
            'tiff', 'ai', 'drw', 'dxf', 'eps', 'ps', 'svg',

            # audio
            'mp3', 'wma', 'ogg', 'wav', 'ra', 'aac', 'mid', 'au', 'aiff',

            # video
            '3gp', 'asf', 'asx', 'avi', 'mov', 'mp4', 'mpg', 'qt', 'rm', 'swf', 'wmv',
            'm4a', 'm4v',

            # other
            'css', 'exe', 'bin', 'rss', 'zip', 'rar', ]
    
    """
        Gets redirect url.
    """
    def redirect(self, url):
        request_time = 1
        try:
            redirect_url = ''
            http = urllib3.PoolManager()
            req = http.request('GET', url, redirect=False)
            if req.status == 200:
                p = parse_url(url)
                self.start_urls.append(url)
                self.allowed_domains.append(p.host.replace('www.', '')[:3])
                return

            while req.status != 200:
                if request_time == 10:
                    raise Exception
                redirect_url = req.headers['Location']
                req = http.request('GET', redirect_url, redirect=False)
                request_time += 1
            p = parse_url(redirect_url)
            self.start_urls.append(redirect_url)
            self.allowed_domains.append(p.host.replace('www.', '')[:3])
        except Exception:
            p = parse_url(url)
            self.start_urls.append(url)
            self.allowed_domains.append(p.host.replace('www.', '')[:3])

    def start_requests(self):
        for url in self.start_urls:
            #yield scrapy.Request(url, callback=self.parse, dont_filter=True)
            yield scrapy.Request(url, callback=self.parse, dont_filter=True)

    """
        extract item in html.
    """
    def parse_items(self, response):
        run_time = (datetime.now() - self.start_time).total_seconds()
        if run_time > self.MaxRunningTime:
            print("out of max running time")
            raise scrapy.exceptions.CloseSpider("max running time exceeded")
        #allow_domains=self.allowed_domains
        items = []
        extractor = lnk.LinkExtractor(canonicalize=True, unique=True)
        for link in extractor.extract_links(response):
            if not self.allowed_domains[0] in parse_url(link.url).host.replace("www.", "")[:3]:
                continue
            if link.url in self.seen:
                continue
            item = Item()
            item['URL'] = link.url
            yield item
            self.seen.add(link.url)
    
    """
        Classificates type of url
    """
    def classification(self, url):
        pdf_extensions = ['.pdf']
        word_extensions = ['.hwp', '.hwt', '.doc', '.docx', '.odt']
        excel_extensions = ['.xls', '.xlsx', '.ods']
        ppt_extensions = ['.odp', '.ppt', '.pptx', '.pps']
        for extension in pdf_extensions:
            if extension in url:
                return 'pdf'
        for extension in word_extensions:
            if extension in url:
                return 'word'
        for extension in excel_extensions:
            if extension in url:
                return 'excel'
        for extension in ppt_extensions:
            if extension in url:
                return 'ppt'
        return 'html'

    def closed(self, reason):
        print(reason)
        self.end_time = datetime.now()
        self.run_time = relativedelta(self.end_time, self.start_time)
        self.meta = {
            'END_TIME':(self.end_time).strftime("%y/%m/%d %H:%M:%S"),
            'START_TIME': (self.start_time).strftime("%y/%m/%d %H:%M:%S"),
            'RUN_TIME': '{H}:{M}:{S}'.format(H=self.run_time.hours, M=self.run_time.minutes, S=self.run_time.seconds),
            'CLOSE_REASON': reason,
        }
        return self.meta

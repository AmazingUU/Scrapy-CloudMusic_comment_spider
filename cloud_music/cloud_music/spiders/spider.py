# -*- coding: utf-8 -*-
import scrapy


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    allowed_domains = ['spider.com']
    start_urls = ['http://spider.com/']

    def parse(self, response):
        pass

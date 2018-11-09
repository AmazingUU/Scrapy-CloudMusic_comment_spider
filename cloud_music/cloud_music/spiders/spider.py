# -*- coding: utf-8 -*-
import json

import scrapy

from cloud_music.const import const
from cloud_music.items import DayHotSongItem


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    start_urls = [const.DAY_LIST_URL]

    def parse(self, response):
        res = json.loads(response.text)['result']
        day_hot_song_list = res['tracks']
        day_hot_song_item = DayHotSongItem()
        ranking = 0
        for song in day_hot_song_list:
            ranking += 1
            day_hot_song_item['ranking'] = ranking
            day_hot_song_item['song_id'] = song['id']
            day_hot_song_item['name'] = song['name']
            day_hot_song_item['singer'] = song['artists'][0]['name']
            print(day_hot_song_item)
            yield day_hot_song_item
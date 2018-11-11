# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from cloud_music.const import const
from cloud_music.db_helper import DbHelper
from cloud_music.items import DayHotSongItem, HotCommentItem, CommentItem


class CloudMusicPipeline(object):
    db = DbHelper()
    db.connenct(const.DB_CONFIGS)

    def insert_into_day_hot_song(self, item):
        self.db.save_one_data_to_day_hot_song(item)

    def insert_into_hot_comment(self,item):
        self.db.save_one_data_to_hot_comment(item)

    def insert_into_comment(self,item):
        self.db.save_one_data_to_comment(item)

    def process_item(self, item, spider):
        if isinstance(item, DayHotSongItem):
            self.insert_into_day_hot_song(item)
        elif isinstance(item,HotCommentItem):
            self.insert_into_hot_comment(item)
        elif isinstance(item,CommentItem):
            self.insert_into_comment(item)
        return item

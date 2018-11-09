# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DayHotSongItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    ranking = scrapy.Field()
    song_id = scrapy.Field()
    name = scrapy.Field()
    singer = scrapy.Field()


class HotCommentItem(scrapy.Item):
    song_id = scrapy.Field()
    username = scrapy.Field()
    content = scrapy.Field()
    like_count = scrapy.Field()
    comment_time = scrapy.Field()


class CommentItem(scrapy.Field):
    song_id = scrapy.Field()
    username = scrapy.Field()
    content = scrapy.Field()
    like_count = scrapy.Field()
    comment_time = scrapy.Field()
    beReplied_content = scrapy.Field()
    beReplied_user = scrapy.Field()

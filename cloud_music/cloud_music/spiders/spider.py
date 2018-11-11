# -*- coding: utf-8 -*-
import base64
import binascii
import datetime
import json
from random import random

import scrapy
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA

from cloud_music.const import const
from cloud_music.items import DayHotSongItem, CommentItem, HotCommentItem


def AES_encrypt(text, key):  # AES加密
    iv = '0102030405060708'
    pad = 16 - (len(text) % 16)  # 明文补足为16的倍数，如果正好是16的倍数，再补16位
    text += pad * chr(pad)  # chr()返回对应数值的ascii码，如果少一位，补充一个数值1对应的ascii，如果少两位，补充两个数字2对应的ascii，以此类推
    encryptor = AES.new(key, AES.MODE_CBC, iv)  # key为密钥，iv为初始偏移量
    encrypt_text = encryptor.encrypt(text)  # 加密
    encrypt_text = base64.b64encode(encrypt_text)  # 二级制编码，用64个字符来表示任意二进制数据
    return encrypt_text


def create_random_str(num):  # 生成num位随机字符串
    char_list = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    str = ''
    for i in range(num):
        index = int(random() * len(char_list))
        str += char_list[index]
    return str


def get_params(first_param, forth_param, random_str):  # 产生POST的第一个参数
    encText = AES_encrypt(first_param, forth_param).decode('utf-8')  # AES加密出来是byte类型，再次加密时需要先将其转为String
    params = AES_encrypt(encText, random_str)
    return params


def RSA_encrypt(n_str, e_str, random_str):  # RSA加密
    n = int(n_str, 16)  # RSA modulus,RSA算法中大素数相乘的结果，16进制
    e = int(e_str, 16)  # RSA算法中的e，和n一起组成公钥(n,e)，16进制
    cryptor = RSA.construct((n, e))  # 构造加密器
    # 网易云JS中的encryptedString()将16位随机字符串倒序了，所以要生成与JS一样的密文，这里也要倒序，而且下面加密时，要求为字节，所以编码为ascii码
    text = random_str[::-1].encode('ascii')
    encrypt_text = cryptor.encrypt(text, '')[0]  # 网易云JS中第二个参数为空，这里也为空。查看encrypt()源码发现会返回两个值，第一个是密文，第二个值总为空
    encrypt_text = binascii.b2a_hex(encrypt_text).decode('utf-8')  # encrypt_text为二进制，转为十六进制然后再解码成字符串才是最后要post的密文
    return encrypt_text


def get_encSecKey(random_str, second_params, third_params):  # 产生POST的第二个参数
    encSecKey = RSA_encrypt(third_params, second_params, random_str)
    return encSecKey


def get_hot_comment(response):  # 从返回的评论JSON中分析出热门评论的相关数据
    hot_comment_list = response['hotComments']
    for hot_comment in hot_comment_list:
        data = HotCommentItem()
        data['username'] = hot_comment['user']['nickname']
        data['content'] = hot_comment['content']
        data['like_count'] = hot_comment['likedCount']
        time = int(hot_comment['time'] / 1000)  # 返回的时间戳在python中后三位为毫秒数，可以舍弃
        dateArray = datetime.datetime.fromtimestamp(time)
        data['comment_time'] = dateArray.strftime("%Y-%m-%d %H:%M:%S")
        yield data


def get_comment(response):  # 从返回的评论JSON中分析出最新评论的相关数据
    comment_list = response['comments']
    for comment in comment_list:
        data = CommentItem()
        data['username'] = comment['user']['nickname']
        data['content'] = comment['content']
        data['like_count'] = comment['likedCount']
        time = int(comment['time'] / 1000)
        dateArray = datetime.datetime.fromtimestamp(time)
        data['comment_time'] = dateArray.strftime("%Y-%m-%d %H:%M:%S")
        try:
            data['beReplied_content'] = comment['beReplied'][0]['content']  # 最新评论中经常有回复别人评论的情况，所以记录下被回复的内容和用户名
            data['beReplied_user'] = comment['beReplied'][0]['user']['nickname']
        except:
            data['beReplied_content'] = '无'
            data['beReplied_user'] = '无'

        yield data

def post(response):
    song_id = response.meta['song_id']
    res = json.loads(response.text)
    for data in get_hot_comment(res):
        data['song_id'] = song_id
        # print(data)
        yield data
    for d in get_comment(res):
        d['song_id'] = song_id
        # print(d)
        yield d

class SpiderSpider(scrapy.Spider):
    name = 'spider'
    start_urls = [const.DAY_LIST_URL]

    def parse(self, response):
        res = json.loads(response.text)['result']
        day_hot_song_list = res['tracks']
        day_hot_song_item = DayHotSongItem()
        ranking = 0
        comment_url = 'https://music.163.com/weapi/v1/resource/comments/R_SO_4_{}?csrf_token='  # 评论接口
        for song in day_hot_song_list:
            ranking += 1
            day_hot_song_item['ranking'] = ranking
            day_hot_song_item['song_id'] = song['id']
            day_hot_song_item['name'] = song['name']
            day_hot_song_item['singer'] = song['artists'][0]['name']
            # print(day_hot_song_item)
            yield day_hot_song_item

            random_str = create_random_str(16)
            params = get_params(const.FIRST_PARAM, const.FORTH_PARAM, random_str)
            encSecKey = get_encSecKey(random_str, const.SECOND_PARAM, const.THIRD_PARAM)
            form_data = {'params': params,
                         'encSecKey': encSecKey}
            url = comment_url.format(song['id'])
            # print(form_data)
            yield scrapy.FormRequest(url=url,callback=post,formdata=form_data,meta={'song_id':song['id']},dont_filter=True)

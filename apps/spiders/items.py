# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ProxyItem(scrapy.Item):
    country = scrapy.Field()
    ip = scrapy.Field()
    port = scrapy.Field()
    location = scrapy.Field()
    anonymous = scrapy.Field()
    type = scrapy.Field()
    speed = scrapy.Field()
    time = scrapy.Field()
    pass

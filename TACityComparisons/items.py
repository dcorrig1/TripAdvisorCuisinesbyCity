# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TAcitycomparisonsItem(scrapy.Item):
    # define the fields for your item here like:
    CityCode = scrapy.Field()
    CityName = scrapy.Field()
    StateName = scrapy.Field()
    RegionName = scrapy.Field()
    CountryName = scrapy.Field()
    IsOutofCity = scrapy.Field()
    NumReviews = scrapy.Field()
    Price = scrapy.Field()
    CuisinesList = scrapy.Field()
    AvgRating = scrapy.Field()
    RestaurantName = scrapy.Field()
    RestaurantLink = scrapy.Field()
    RankBlurb = scrapy.Field()
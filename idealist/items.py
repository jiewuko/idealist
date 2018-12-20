# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class IdealistItems(scrapy.Item):
    url = scrapy.Field()
    organization = scrapy.Field()
    organization_URL = scrapy.Field()
    organization_WEB_SITE = scrapy.Field()
    job_posting_title = scrapy.Field()
    job_description = scrapy.Field()
    streetAddress = scrapy.Field()
    addressLocality = scrapy.Field()
    addressRegion = scrapy.Field()
    postalCode = scrapy.Field()
    addressCountry = scrapy.Field()
    details_at_a_glance = scrapy.Field()
    how_to_apply = scrapy.Field()
    list_emails_and_urls = scrapy.Field()
    salary = scrapy.Field()
    date_posted = scrapy.Field()

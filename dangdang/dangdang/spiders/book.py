# -*- coding: utf-8 -*-
import scrapy
import copy
import re


from urllib import parse
from scrapy_redis.spiders import RedisSpider

class BookSpider(RedisSpider):
    name = 'book'
    allowed_domains = ['dangdang.com']
    redis_key = 'dangdang'

    # def __init__(self, *args, **kwargs):
    #     # Dynamically define the allowed domains list.
    #     domain = kwargs.pop('domain', '')
    #     self.allowed_domains = filter(None, domain.split(','))
    #     super(MySpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        print('response')
        # print('*'*200)
        # print(response.body)
        div_list = response.xpath("//div[@class='con flq_body']/div")[2:12]

        for div in div_list:
            item = {}
            # 获取大分类
            item['b_cate'] = div.xpath("./dl/dt//text()").extract()
            item['b_cate'] = [i.strip() for i in item['b_cate'] if len(i.strip())>0][0]
            dl_list = div.xpath("./div//dl[@class='inner_dl']")
            for dl in dl_list:
                item['m_cate'] = dl.xpath("./dt//text()").extract()
                m_cate = [i.strip() for i in item['m_cate'] if len(i.strip())>0][0]
                item['m_cate'] = m_cate
                a_list = dl.xpath("./dd/a")
                for a in a_list:
                    item['s_cate'] = a.xpath("./@title").extract_first()
                    item['href'] = a.xpath("./@href").extract_first()
                    # print(item)
                    yield scrapy.Request(
                                item['href'],
                                callback=self.parse_book_list,
                                meta={'item': copy.deepcopy(item)}
                            )
                    # return

                # if m_cate != '下载APP':
                #     item['m_cate'] = m_cate
                #
                #     a_list = dl.xpath("./dd/a")
                #     for a in a_list:
                #         item['s_cate'] = a.xpath("./@title").extract_first()
                #         item['href'] = a.xpath("./@href").extract_first()
                #         print(item)
                #         # yield scrapy.Request(
                #         #     item['href'],
                #         #     callback=self.parse_book_list ,
                #         #     meta={'item':copy.deepcopy(item)}
                #         # )
                #         # return
                # else:
                #     continue

    def parse_book_list(self, response):
        print('#'*100)
        item = response.meta['item']
        li_list = response.xpath("//ul[@class='bigimg']/li")
        # print(len(li_list))
        for li in li_list:
            item['img'] = li.xpath("./a[@class='pic']/img/@src").extract_first()
            # print(item['img'])
            if item['img'] == 'images/model/guan/url_none.png':
                item['img'] = li.xpath("./a[@class]/img/@data-original").extract_first()

            # print(item['img'])

            item['book_name'] = li.xpath("./a/@title").extract_first()
            item['price'] = li.xpath("./p[@class='price']/span[@class='search_now_price']/text()").extract_first()
            item['desc'] = li.xpath("./p[@class='detail']/text()").extract()
            item['author'] = li.xpath("./p[@class='search_book_author']/span[1]/a/text()").extract()
            item['publish_date'] = li.xpath("./p[@class='search_book_author']/span[2]/text()").extract_first()
            item['press'] = li.xpath("./p[@class='search_book_author']/span[3]/a/text()").extract_first()
            # print(type(item['publish_date']))
            if item['publish_date'] is not None:
                item['publish_date'] = re.sub(r'[ |/]*', '', item['publish_date'])
            yield item

        next_url = response.xpath("./li[@class='next']/a/@href").extract_first()
        if next_url is not None:
            next_url = parse.urljoin(response.url, next_url)
            yield scrapy.Request(
                next_url,
                callback=self.parse_book_list,
                meta={'item':item}
            )
            # print(item)
            # item['book_href'] = li.xpath("./a/@href").extract_first()

    #         yield scrapy.Request(
    #             item['book_href'],
    #             callback=self.parse_book_detail,
    #             meta={'item':copy.deepcopy(item)}
    #         )
    #
    # def parse_book_detail(self, response):
    #     item = response.meta['item']
    #     item['author'] = response.xpath("//span[@id='author']//text()").extract()
    #     item['author'] = ''.join(item['author']) # \u3000
    #     item['press'] = response.xpath("//span[@dd_name='出版社']/a/text()").extract_first()
    #     item['publish_date'] = response.xpath("//div[@class='messbox_info']/span[3]/text()").extract_first() # 出版时间: \xa0
    #     item['price'] = response.xpath("//p[@id='dd-price']/text()").extract()
    #     item['price'] = ''.join(item['price']).strip()
    #     print(item)













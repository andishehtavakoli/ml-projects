import scrapy
import re
import requests
from bs4 import BeautifulSoup


def extract_tag_content(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'lxml')

    tag = soup.find_all(class_='bcn-ps-eyebrow eyebrow-category')
    if bool(tag) is True:
        tag = tag[0].text.strip()
    else:
        tag = 'N/A'
        raw_content = soup.find_all(class_='bcn-content--story__body bcn-body--l')

    if bool(raw_content) is True:
        raw_content =  raw_content[0].text
        content = re.sub(r'\s+', ' ', raw_content).strip()

    else:
        content = 'N/A'

    return tag, content


class InsightSpider(scrapy.Spider):
    name = 'insight'
    allowed_domains = ['www.schwab.com']
    #start_urls = ['https://www.schwab.com/resource-center/insights/?type%5Barticle%5D=article']
    start_urls = [f'https://www.schwab.com/resource-center/insights/?type%5Barticle%5D=article&page={page}' for page in range(1,47)]
    def parse(self, response):
        link_list = response.css("[class='main-content clearfix mq--t'] h4[class='icon icon-article'] a ::attr('href')").extract()
        date_list = response.css("[class='submitted submitted--article'] ::text").extract()
        abstract_list = response.css("[class='main-content clearfix mq--t'] [class='field field--name-body field--type-text-with-summary field--label-hidden field__item']::text").extract()
        title_list = response.xpath("//*[@class='icon icon-article']//span/text()").extract()


        schwab_list = []

        for link, date, abstract, title in zip(link_list, date_list, abstract_list, title_list):
            yield {
                "index": "",
                "company": "Charles Schwab",
                "topic": "Insight",
                "tag": extract_tag_content("https://www.schwab.com{link}")[0],
                "section": "",
                "title": title,
                "date": date.strip(),
                "link": link,
                "abstract": abstract,
                "content": ""}




        next_page = response.css("#block-schwabcog-content > div.taxonomy-landing-page.taxonomy-landing-page-section > div > div > div.content > div.listing > div > div > nav > ul > li.pager__item.pager__item--next > a").extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)










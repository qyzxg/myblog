#!/usr/bin/python
# -*- coding:utf-8 -*-
from .crawler import BaseCrawler
from lxml import etree
from bs4 import BeautifulSoup
import random
import datetime


class CrawlerXiaorui(BaseCrawler):
    def __init__(self):
        super(CrawlerXiaorui, self).__init__()
        self.site = 'xiaorui.cc'

    def fetch_page(self, *args, **kwargs):
        r = super(CrawlerXiaorui, self).fetch_page(*args, **kwargs)
        return r

    def get_total_page(self):
        url = 'http://xiaorui.cc/category/python/'
        r = self.fetch_page(url=url)
        tree = etree.HTML(r.text)
        total = tree.xpath('//ul[@class="pagination pull-right"]/li[last()]/a/text()')[0][2:-2]
        return int(total)

    def get_post_urls(self):
        total = self.get_total_page()
        for i in range(1, total + 1):
            print('第{}页'.format(i))
            r = self.fetch_page(url='http://xiaorui.cc/category/python/page/{}/'.format(i))
            if r.status_code != 200:
                continue
            tree = etree.HTML(r.text)
            urls = tree.xpath('//div[@class="title-article"]/h4/a/@href')
            for url in urls:
                year = int(url.split('/')[3])
                month = int(url.split('/')[4])
                day = int(url.split('/')[5])
                p_date = datetime.datetime(year, month, day).strftime('%Y-%m-%d')
                if p_date == self.today:
                    yield url
                else:
                    print('文章已过期')

    def parse(self):
        for url in self.get_post_urls():
            try:
                r = self.fetch_page(url=url)
                soup = BeautifulSoup(r.text, 'lxml')
                scripts = soup.find_all('script')
                for i in scripts:
                    i.decompose()
                foot = soup.find('div', style="font-family:'Helvetica Neue';font-size:14px;")
                next_ = soup.find('div', clas="zan-page bs-example")
                copy_right = soup.find('div', class_="copyright alert alert-success")
                foot.decompose()
                next_.decompose()
                copy_right.decompose()
                as_ = soup.find_all('a')
                for i in as_:
                    i.decompose()
                tree = etree.HTML(r.text)
                title = tree.xpath('//div[@class="title-article"]/h1/a/text()')[0]
                print(title)
                codes = soup.find_all('div',
                                      class_='crayon-syntax crayon-theme-solarized-light crayon-font-monaco crayon-os-pc print-yes notranslate')
                images = soup.find('div', class_='centent-article').find_all('img')
                img_list = []
                if images:
                    for i in images:
                        url = i.get('src')
                        if str(url).startswith('/wp-content'):
                            url = 'http://xiaorui.cc' + url
                            r = self.fetch_page(url)
                            url_ = self.upload_img(url.split('/')[-1], r.content, 'crawl/')
                            img_list.append(url_)
                            new_img = soup.new_tag('img')
                            new_img.attrs['width'] = '100%'
                            new_img.attrs['src'] = url_
                            i.replace_with(new_img)
                for i in codes:
                    crayon_code = i.find_all('td', class_='crayon-code')
                    for i_ in crayon_code:
                        l = []
                        for j in i_.find_all('div', class_='crayon-line'):
                            l.append(j.text + '\n')
                        pre = soup.new_tag('pre')
                        pre.attrs['class'] = 'language-python'
                        code = soup.new_tag('code')
                        pre.append(code)
                        code.string = ''.join(l)
                        i.replace_with(pre)
                soup1 = BeautifulSoup(str(soup.find(class_='centent-article')), 'lxml')
                source_ = soup1.new_tag('p')
                source_.string = '本文转载至{}'.format(self.site)
                soup1.html.unwrap()
                soup1.body.unwrap()
                soup1.append(source_)
                body = str(soup1)
                if img_list:
                    post_img = random.choice(img_list)
                    self.save(title=str(title), body=body, style='转载', post_img=post_img)
                else:
                    self.save(title=str(title), body=body, style='转载')
            except Exception as e:
                print(e)


if __name__ == '__main__':
    c = CrawlerXiaorui()
    c.parse()

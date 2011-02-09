#!/usr/bin/python

import os
import re
from urllib import unquote_plus

from lxml import etree as ET

from manga import Manga, App, urlopen, urlretrieve

class Doujins(Manga):
    SERIES_URL = '%(baseurl)s/search.php?series=%(series)s&page=1'
    CHAPTER_URL = '%(baseurl)s/doujin/%(chapter)s/'
    PAGE_URL = '%(baseurl)s/doujin/%(chapter)s/%(page)d.htm'

    CHAPTER_PATTERN = '%(series)s-%(chapter_label)s.cbz'
    PAGE_PATTERN = '%(series)s-%(chapter_label)s-%(page)02d'

    def __init__(self):
        Manga.__init__(self, 'http://www.doujins.org')

    def list_chapters(self, data):
        url = self.get_series_url(data)
        f = urlopen(url)
        doc = ET.HTML(f.read())
        chapters = self._list_chapters(doc)
        pages = [self.baseurl+n.attrib['href'] \
                 for n in filter(lambda n: n.attrib['href'].startswith('/search.php?series='),
                                 doc.xpath("//a"))]
        for url in pages:
            f = urlopen(url)
            doc = ET.HTML(f.read())
            chapters += self._list_chapters(doc)
        chapters.sort(lambda a, b: cmp(a['chapter'], b['chapter']))
        return chapters

    def download_page(self, data):
        url = self.get_page_url(data)
        f = urlopen(url)
        doc = ET.HTML(f.read())
        img_url = self._download_page(doc)
        filename = self.get_page_filename(data)
        filename += os.path.splitext(img_url)[-1].split('&')[0].lower()
        content = urlretrieve(img_url)
        fo = open(filename, 'wb')
        fo.write(content)
        fo.close()

    def _list_chapters(self, doc):
        chapters = doc.xpath("//div[@class='pdoujins']/a")
        chapters = [{'chapter': i.attrib['href'].split('/')[-2],
                     'chapter_label': unquote_plus(i.attrib['href'].split('/')[-2])} for i in chapters]
        return chapters

    def _list_pages(self, doc):
        pages = doc.xpath("//div[@id='ipage']/text()")[0].split(' of ')[-1]
        pages = range(1, int(pages)+1)
        return pages

    def _download_page(self, doc):
        url = doc.xpath("//div[@id='image']/a/img")[0].attrib['src']
        return url.replace(' ', '%20')

class DoujinsApp(App):
    def __init__(self):
        App.__init__(self, extract_range=False, chapter_func=str)
        self.manga = Doujins()

    def _parse_args(self, parser):
        App._parse_args(self, parser)

if __name__ == '__main__':
    app = DoujinsApp()
    app.run()

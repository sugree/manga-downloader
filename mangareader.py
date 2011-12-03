#!/usr/bin/python

import re

from manga import Manga, App

class MangaReader(Manga):
    SERIES_URL = '%(baseurl)s/%(series_id)d/%(series)s.html'
    CHAPTER_URL = '%(baseurl)s/%(series_id)d-%(chapter_id)d-1/%(series)s/chapter-%(chapter)d.html'
    PAGE_URL = '%(baseurl)s/%(series_id)d-%(chapter_id)d-%(page)d/%(series)s/chapter-%(chapter)d.html'

    NEW_SERIES_URL = '%(baseurl)s/%(series)s'
    NEW_CHAPTER_URL = '%(baseurl)s/%(series)s/%(chapter)d'
    NEW_PAGE_URL = '%(baseurl)s/%(series)s/%(chapter)d/%(page)d'

    CHAPTER_CRE_1 = re.compile(r'/(\d+)-(\d+)-(\d+)/[^/]+/chapter-(\d+).html')
    CHAPTER_CRE_2 = re.compile(r'/[^/]+/(\d+)')

    def __init__(self):
        Manga.__init__(self, 'http://www.mangareader.net')

    def get_series_url(self, data):
        if 'series_id' in data:
            return Manga.get_series_url(self, data)
        else:
            d = data
            d.update({'baseurl': self.baseurl})
            return self.NEW_SERIES_URL % d

    def get_chapter_url(self, data):
        if 'chapter_id' in data:
            return Manga.get_chapter_url(self, data)
        else:
            d = data
            d.update({'baseurl': self.baseurl})
            return self.NEW_CHAPTER_URL % d

    def get_page_url(self, data):
        if 'chapter_id' in data:
            return Manga.get_page_url(self, data)
        else:
            d = data
            d.update({'baseurl': self.baseurl})
            return self.NEW_PAGE_URL % d

    def _list_chapters(self, doc):
        chapters = []
        for n in doc.xpath("//table[@id='listing']/tr[position()>1]"):
            u = n.xpath("td[1]/a")[0].attrib['href']
            m = self.CHAPTER_CRE_1.match(u)
            if m:
                chapters.append({'series_id': int(m.group(1)),
                                 'chapter_id': int(m.group(2)),
                                 'chapter': int(m.group(4))})
                continue
            m = self.CHAPTER_CRE_2.match(u)
            if m:
                chapters.append({'chapter': int(m.group(1))})
        return chapters

    def _list_pages(self, doc):
        pages = doc.xpath("//select[@id='pageMenu']/option")
        pages = [int(i.text) for i in pages]
        return pages

    def _download_page(self, doc):
        url = doc.xpath("//img[@id='img']")[0].attrib['src']
        return url

class MangaReaderApp(App):
    def __init__(self):
        App.__init__(self)
        if self.options.series_id:
            self.data.update({'series_id': int(self.options.series_id)})
        if self.options.chapter_id:
            self.data.update({'chapter_id': int(self.options.chapter_id)})
        self.manga = MangaReader()

    def _parse_args(self, parser):
        App._parse_args(self, parser)
        parser.add_option('--series_id', dest='series_id', default='',
                          help='Series ID')
        parser.add_option('--chapter_id', dest='chapter_id', default='',
                          help='Chapter ID')

if __name__ == '__main__':
    #import sys
    #mr = MangaReader()
    #print mr.list_chapters({'series_id': 144, 'series': 'kekkaishi'})
    #print mr.list_pages({'series_id': 144, 'series': 'kekkaishi', 'chapter_id': 9422, 'chapter': 1})
    #mr.download_page({'series_id': 144, 'series': 'kekkaishi', 'chapter_id': 9422, 'chapter': 1, 'page': 1})
    #mr.download_chapter({'series_id': 144, 'series': 'kekkaishi', 'chapter_id': 9422, 'chapter': 1})
    #sys.exit(-1)
    app = MangaReaderApp()
    app.run()

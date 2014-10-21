#!/usr/bin/python

import re

from lxml import etree as ET

from manga import MangaWithVol, App, urlretrieve, smart_cmp

class MangaHere(MangaWithVol):
    SERIES_URL = '%(baseurl)s/manga/%(series)s/'
    CHAPTER_URL = '%(baseurl)s/manga/%(series)s/v%(volume)s/c%(chapter_id)s/'
    PAGE_URL = '%(baseurl)s/manga/%(series)s/v%(volume)s/c%(chapter_id)s/%(page)s.html'
    CHAPTER_CRE = re.compile(r'.*/[^/]+/v(?P<volume>[0-9-.]+)/c(?P<chapter_id>[0-9-.]+)/$')
    CHAPTER_PATTERN = '%(series)s-%(chapter_id)03s.cbz'
    PAGE_PATTERN = '%(series)s-%(chapter_id)03s-%(page)03s'

    NV_CHAPTER_URL = '%(baseurl)s/manga/%(series)s/c%(chapter_id)s/'
    NV_PAGE_URL = '%(baseurl)s/manga/%(series)s/c%(chapter_id)s/%(page)s.html'
    NV_CHAPTER_CRE = re.compile(r'.*/[^/]+/c(?P<chapter_id>[0-9-.]+)/$')

    NV_CHAPTER_PATTERN = CHAPTER_PATTERN
    NV_PAGE_PATTERN = PAGE_PATTERN

    def __init__(self):
        MangaWithVol.__init__(self, 'http://www.mangahere.co')

    def list_chapters(self, data):
        url = self.get_series_url(data)
        content = urlretrieve(url)
        doc = ET.HTML(content)
        chapters = self._list_chapters(doc)
        pages = set([n.attrib['href'] \
                 for n in doc.xpath("//ul[@class='pgg']/li/a")])
        for url in pages:
            content = urlretrieve(url)
            doc = ET.HTML(content)
            chapters += self._list_chapters(doc)
        chapters.sort(lambda a, b: smart_cmp(a['chapter_label'], b['chapter_label']))
        return chapters

    def _list_chapters(self, doc):
        chapters = []
        for n in doc.xpath("//div[@class='detail_list']/ul/li/span/a"):
            m = self.CHAPTER_CRE.match(n.attrib['href'])
            if m:
                chapters.append({'chapter_id': m.group('chapter_id'),
                             'chapter': m.group('chapter_id').zfill(3),
                             'volume': m.group('volume').zfill(2),
                             'chapter_label': m.group('chapter_id').zfill(3)})
                continue

            m = self.NV_CHAPTER_CRE.match(n.attrib['href'])
            if m:
                chapters.append({'chapter_id': m.group('chapter_id'),
                             'chapter': m.group('chapter_id').zfill(3),
                             'chapter_label': m.group('chapter_id').zfill(3)})
                continue
        return chapters

    def _list_pages(self, doc):
        pages = doc.xpath("//select[@class='wid60']/option")
        pages = set([i.text for i in pages])
        pages = list(pages)
        pages.sort()
        return pages


    def _download_page(self, doc):
        url = doc.xpath("//section[@class='read_img']/a/img")[0].attrib['src']
        url = url.replace(' ', '%20')
        return url

class MangaHereApp(App):
    def __init__(self):
        App.__init__(self, chapter_func=str)
        self.manga = MangaHere()

    def _parse_args(self, parser):
        App._parse_args(self, parser)
        parser.add_option('--volume', dest='volume', default='',
                          help='Volume')

    def _filter_chapter(self, data):
        if 'volume' in self.data and data['volume'] != self.data['volume']:
            return True
        return App._filter_chapter(self, data)
if __name__ == '__main__':
    #import sys
    #mr = MangaHere()
    #print mr.list_chapters({'series': 'madoka_x_nanoha'})
    #print mr.list_pages({'series': 'madoka_x_nanoha', 'chapter': 1, 'chapter_id': '001', 'chapter_label': '001'})
    #mr.download_page({'series': 'madoka_x_nanoha', 'chapter': 1,  'chapter_id': '001', 'chapter_label': '001', 'page': 1})
    #mr.download_chapter({'series': 'madoka_x_nanoha', 'chapter': 1, 'chapter_id': '001', 'chapter_label': '001'})
    #sys.exit(-1)
    app = MangaHereApp()
    app.run()

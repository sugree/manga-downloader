#!/usr/bin/python

import re

from lxml import etree as ET

from manga import Manga, App, urlretrieve, smart_cmp

class MangaHere(Manga):
    SERIES_URL = '%(baseurl)s/manga/%(series)s/'
    CHAPTER_URL = '%(baseurl)s/manga/%(series)s/c%(chapter_id)s/'
    PAGE_URL = '%(baseurl)s/manga/%(series)s/c%(chapter_id)s/%(page)s.html'

    CHAPTER_CRE = re.compile(r'.*/[^/]+/c(?P<chapter_id>[0-9-.]+)/$')

    CHAPTER_PATTERN = '%(series)s-%(chapter_id)03s.cbz'
    PAGE_PATTERN = '%(series)s-%(chapter_id)03s-%(page)03s'

    def __init__(self):
        Manga.__init__(self, 'http://www.mangahere.co')

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
            chapters.append({'chapter_id': m.group('chapter_id'),
                             'chapter': m.group('chapter_id').zfill(3),
                             'chapter_label': m.group('chapter_id').zfill(3)})
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

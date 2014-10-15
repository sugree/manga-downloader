#!/usr/bin/python

import re

from lxml import etree as ET

from manga import Manga, App, urlretrieve, smart_cmp

class NiceOppai(Manga):
    SERIES_URL = '%(baseurl)s/%(series)s/'
    CHAPTER_URL = '%(baseurl)s/%(series)s/%(chapter_id)s/'
    PAGE_URL = '%(baseurl)s/%(series)s/%(chapter_id)s/%(page)s/'

    CHAPTER_CRE = re.compile(r'.*/[^/]+/(?P<chapter_id>[0-9-.]+)/$')

    CHAPTER_PATTERN = '%(series)s-%(chapter_id)03s.cbz'
    PAGE_PATTERN = '%(series)s-%(chapter_id)03s-%(page)03s'

    def __init__(self):
        Manga.__init__(self, 'http://www.niceoppai.net')

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
        for n in doc.xpath("//div[@id='sct_content']/div/div/ul/li/a"):
            m = self.CHAPTER_CRE.match(n.attrib['href'])
            chapters.append({'chapter_id': m.group('chapter_id'),
                             'chapter': m.group('chapter_id').zfill(3),
                             'chapter_label': m.group('chapter_id').zfill(3)})
        return chapters

    def _list_pages(self, doc):
        pages = doc.xpath("//select[@class='cbo_wpm_pag']/option")
        pages = set([i.text for i in pages])
        pages = list(pages)
        pages.sort()
        return pages


    def _download_page(self, doc):
        url = doc.xpath("//div[@class='prw']/a/img")[0].attrib['src']
        url = url.replace(' ', '%20')
        return url

class NiceOppaiApp(App):
    def __init__(self):
        App.__init__(self, chapter_func=str)
        if self.options.series_id:
            self.data.update({'series_id': int(self.options.series_id)})
        if self.options.chapter_id:
            self.data.update({'chapter_id': int(self.options.chapter_id)})
        self.manga = NiceOppai()

    def _parse_args(self, parser):
        App._parse_args(self, parser)
        parser.add_option('--series_id', dest='series_id', default='',
                          help='Series ID')
        parser.add_option('--chapter_id', dest='chapter_id', default='',
                          help='Chapter ID')

if __name__ == '__main__':
    #import sys
    #mr = NiceOppai()
    #print mr.list_chapters({'series_id': 144, 'series': 'kekkaishi'})
    #print mr.list_pages({'series_id': 144, 'series': 'kekkaishi', 'chapter_id': 9422, 'chapter': 1})
    #mr.download_page({'series_id': 144, 'series': 'kekkaishi', 'chapter_id': 9422, 'chapter': 1, 'page': 1})
    #mr.download_chapter({'series_id': 144, 'series': 'kekkaishi', 'chapter_id': 9422, 'chapter': 1})
    #sys.exit(-1)
    app = NiceOppaiApp()
    app.run()

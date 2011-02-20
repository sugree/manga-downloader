#!/usr/bin/python

import re

from lxml import etree as ET

from manga import Manga, App, urlretrieve

class OtakuWorks(Manga):
    SERIES_URL = '%(baseurl)s/series/%(series_id)d/%(series)s'
    CHAPTER_URL = '%(baseurl)s/view/%(chapter_id)d/%(series)s/%(chapter_label)s/read'
    PAGE_URL = '%(baseurl)s/view/%(chapter_id)d/%(series)s/%(chapter_label)s/read/%(page)d'

    CHAPTER_CRE = re.compile(r'/view/(?P<chapter_id>\d+)/[^/]+/(?P<chapter_label>(vol-(?P<volume>\d+)-?)?(chp-(?P<chapter>[0-9-]+))?)$')
    PAGE_CRE = re.compile(r"create_jsnumsel2\('fpage1',(\d+),(\d+),\d+,\d+\);")

    CHAPTER_PATTERN = '%(series)s-%(chapter_label)s.cbz'
    PAGE_PATTERN = '%(series)s-%(chapter_label)s-%(page)02d'

    def __init__(self):
        Manga.__init__(self, 'http://www.otakuworks.com')

    def list_chapters(self, data):
        url = self.get_series_url(data)
        content = urlretrieve(url)
        doc = ET.HTML(content)
        chapters = self._list_chapters(doc)
        pages = [self.baseurl+n.attrib['href'] \
                 for n in filter(lambda n: n.attrib['href'].startswith('/series/'),
                                 doc.xpath("//div[@class='pagenav']/div/a"))]
        for url in pages:
            content = urlretrieve(url)
            doc = ET.HTML(content)
            chapters += self._list_chapters(doc)
        chapters.sort(lambda a, b: cmp(a['chapter_label'], b['chapter_label']))
        return chapters

    def _list_chapters(self, doc):
        chapters = []
        for n in doc.xpath("//div[@id='filelist']/div/a"):
            m = self.CHAPTER_CRE.match(n.attrib['href'])
            chapters.append({'chapter_id': int(m.group('chapter_id')),
                             'chapter_label': m.group('chapter_label'),
                             'chapter': m.group('chapter'),
                             'volume': m.group('volume')})
        return chapters

    def _list_pages(self, doc):
        script = doc.xpath("//script[7]")[0].text
        m = self.PAGE_CRE.search(script)
        start, end = int(m.group(1)), int(m.group(2))
        pages = range(start, end+1)
        return pages

    def _download_page(self, doc):
        url = doc.xpath("//div[@id='filelist']/a/img")[0].attrib['src']
        url = url.replace(' ', '%20')
        return url

class OtakuWorksApp(App):
    def __init__(self):
        App.__init__(self, chapter_func=str)
        if self.options.series_id:
            self.data.update({'series_id': int(self.options.series_id)})
        if self.options.chapter_id:
            self.data.update({'chapter_id': int(self.options.chapter_id)})
        self.manga = OtakuWorks()

    def _parse_args(self, parser):
        App._parse_args(self, parser)
        parser.add_option('--series_id', dest='series_id', default='',
                          help='Series ID')
        parser.add_option('--chapter_id', dest='chapter_id', default='',
                          help='Chapter ID')

if __name__ == '__main__':
    #import sys
    #mr = OtakuWorks()
    #print mr.list_chapters({'series_id': 144, 'series': 'kekkaishi'})
    #print mr.list_pages({'series_id': 144, 'series': 'kekkaishi', 'chapter_id': 9422, 'chapter': 1})
    #mr.download_page({'series_id': 144, 'series': 'kekkaishi', 'chapter_id': 9422, 'chapter': 1, 'page': 1})
    #mr.download_chapter({'series_id': 144, 'series': 'kekkaishi', 'chapter_id': 9422, 'chapter': 1})
    #sys.exit(-1)
    app = OtakuWorksApp()
    app.run()

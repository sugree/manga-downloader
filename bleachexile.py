#!/usr/bin/python

import re

from manga import Manga, App

class BleachExile(Manga):
    SERIES_URL = '%(baseurl)s/%(series)s.html'
    CHAPTER_URL = '%(baseurl)s/%(series)s-chapter-%(chapter)d.html'
    PAGE_URL = '%(baseurl)s/%(series)s-chapter-%(chapter)d-page-%(page)d.html'

    CHAPTER_PATTERN = '%(series)s-%(chapter_label)s.cbz'
    PAGE_PATTERN = '%(series)s-%(chapter_label)s-%(page)02d'

    def __init__(self):
        Manga.__init__(self, 'http://manga.bleachexile.com')

    def _list_chapters(self, doc):
        chapters = doc.xpath("//select[@name='chapter']/option")
        chapters = [{'chapter': int(i.attrib['value']),
                     'chapter_label': str(i.text).strip().split(' ')[1]} for i in chapters]
        return chapters

    def _list_pages(self, doc):
        pages = doc.xpath("//select[@name='pages']/option")
        pages = [int(i.attrib['value']) for i in pages]
        return list(set(pages))

    def _download_page(self, doc):
        url = doc.xpath("//td[@class='page_image']/a/img | //td[@class='page_image']/img")[0].attrib['src']
        return url.replace(' ', '%20')

class BleachExileApp(App):
    def __init__(self):
        App.__init__(self)
        self.manga = BleachExile()

    def _parse_args(self, parser):
        App._parse_args(self, parser)

if __name__ == '__main__':
    #import sys
    #mr = BleachExile()
    #print mr.list_chapters({'series': 'kekkaishi'})
    #print mr.list_pages({'series': 'kekkaishi', 'chapter': 1})
    #mr.download_page({'series': 'kekkaishi', 'chapter': 1, 'page': 1})
    #mr.download_chapter({'series': 'kekkaishi', 'chapter': 1})
    #sys.exit(-1)
    app = BleachExileApp()
    app.run()

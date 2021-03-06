#!/usr/bin/python

import re

from manga import Manga, App

class EcchiManga(Manga):
    SERIES_URL = '%(baseurl)s/Read/%(series)s'
    CHAPTER_URL = '%(baseurl)s/Read/%(series)s/%(chapter)s'
    PAGE_URL = '%(baseurl)s/Read/%(series)s/%(chapter)s/%(page)02d/'

    CHAPTER_CRE = re.compile(r'/Read/[^/]+/(?P<chapter>[0-9.]+)')
    PAGE_CRE = re.compile(r'/Read/[^/]+/(?P<chapter>[0-9.]+)/(?P<page>[0-9.]+)/')

    CHAPTER_PATTERN = '%(series)s-%(chapter)s.cbz'
    PAGE_PATTERN = '%(series)s-%(chapter)s-%(page)02d'

    def __init__(self):
        Manga.__init__(self, 'http://ecchi-manga.net')

        self.options['urlopen_args'].update({
            'ignore500': True,
        })

    def _list_chapters(self, doc):
        chapters = []
        for n in doc.xpath("//table[@id='updates']/tr/th/a"):
            m = self.CHAPTER_CRE.match(n.attrib['href'])
            chapters.append({'chapter': m.group('chapter'),
                             'chapter_label': m.group('chapter')})
        chapters.reverse()
        return chapters

    def _list_pages(self, doc):
        pages = []
        for n in doc.xpath("//select[@id='pages']/option"):
            m = self.PAGE_CRE.match(n.attrib['value'])
            if not m:
                pages.append(1)
            else:
                pages.append(int(m.group('page')))
        return list(set(pages))

    def _download_page(self, doc):
        url = doc.xpath("//img[@id='bigimage']")[0].attrib['src']
        return url.replace(' ', '%20')

class EcchiMangaApp(App):
    def __init__(self):
        App.__init__(self, extract_range=False, chapter_func=str)

        self.manga = EcchiManga()

    def _parse_args(self, parser):
        App._parse_args(self, parser)

if __name__ == '__main__':
    #import sys
    #mr = EcchiManga()
    #print mr.list_chapters({'series': 'kekkaishi'})
    #print mr.list_pages({'series': 'kekkaishi', 'chapter': 1})
    #mr.download_page({'series': 'kekkaishi', 'chapter': 1, 'page': 1})
    #mr.download_chapter({'series': 'kekkaishi', 'chapter': 1})
    #sys.exit(-1)
    app = EcchiMangaApp()
    app.run()

#!/usr/bin/python

import re

from manga import Manga, App

class Animea(Manga):

    SERIES_URL = '%(baseurl)s/%(series)s.html?skip=1'
    CHAPTER_URL = '%(baseurl)s/%(series)s-chapter-%(chapter)s-page-1.html'
    PAGE_URL = '%(baseurl)s/%(series)s-chapter-%(chapter)s-page-%(page)d.html'

    CHAPTER_PATTERN = '%(series)s-%(chapter)s.cbz'
    PAGE_PATTERN = '%(series)s-%(chapter)s-%(page)03d'

    CHAPTER_CRE = re.compile(r'-chapter-(?P<chapter>[^.]+)\.html$')

    def __init__(self):
        Manga.__init__(self, 'http://manga.animea.net')

    def _list_chapters(self, doc):
        chapters = []
        for n in doc.xpath("//table[@id='chapterslist']/tr[position()>1]")[:-1]:
            u = n.xpath("td[2]/a")[0].attrib['href']
            m = self.CHAPTER_CRE.search(u)
            chapters.append({'chapter': m.group('chapter')})
        return chapters

    def _list_pages(self, doc):
        pages = doc.xpath("//select[@name='page']/option")
        pages = [int(i.attrib['value']) for i in pages]
        return pages

    def _download_page(self, doc):
        url = doc.xpath("//img[@class='chapter_img']")[0].attrib['src']
        return url

class AnimeaApp(App):
    def __init__(self):
        App.__init__(self, chapter_func=str)
        self.manga = Animea()

    def _parse_args(self, parser):
        App._parse_args(self, parser)

if __name__ == '__main__':
    app = AnimeaApp()
    app.run()

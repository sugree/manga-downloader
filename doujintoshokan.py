#!/usr/bin/python

import re

from manga import Manga, App

class DoujinToshokan(Manga):
    SERIES_URL = '%(baseurl)s/series/%(series)s'
    CHAPTER_URL = '%(baseurl)s/read/%(series)s/%(scanlator)s/%(chapter)d'
    PAGE_URL = '%(baseurl)s/read/%(series)s/%(scanlator)s/%(chapter)d/%(page)d'

    CHAPTER_PATTERN = '%(series)s-%(chapter)s-%(scanlator)s.cbz'
    PAGE_PATTERN = '%(series)s-%(chapter)s-%(scanlator)s-%(page)02d'

    def __init__(self):
        Manga.__init__(self, 'http://www.doujintoshokan.com',
                       {'Cookie': 'filter=0'})

    def _list_chapters(self, doc):
        chapters = doc.xpath("//td[@class='cont_mid']/table/tr/td[2]/a")
        chapters = [{'chapter': int(i.attrib['href'].split('/')[-1]),
                     'scanlator': i.attrib['href'].split('/')[-2]} for i in chapters]
        return chapters

    def _list_pages(self, doc):
        pages = doc.xpath("//select[@class='headerSelect']/option")
        pages = [int(i.attrib['value'].split('/')[-1]) for i in pages]
        return list(set(pages))

    def _download_page(self, doc):
        url = doc.xpath("//img[@id='readerPage']")[0].attrib['src']
        return url.replace(' ', '%20')

class DoujinToshokanApp(App):
    def __init__(self):
        App.__init__(self)
        self.manga = DoujinToshokan()

    def _parse_args(self, parser):
        App._parse_args(self, parser)

if __name__ == '__main__':
    app = DoujinToshokanApp()
    app.run()

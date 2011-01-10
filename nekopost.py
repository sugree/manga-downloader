#!/usr/bin/python

import re
import os

from manga import Manga, App, urlopen

class NekoPost(Manga):

    SERIES_URL = '%(baseurl)s/content/%(series)s'
    CHAPTER_URL = '%(baseurl)s/content/%(series)s/%(chapter)03d'
    PAGE_URL = '%(baseurl)s/content/%(series)s/%(chapter)03d'

    CHAPTER_CRE = re.compile(r'content/[^/]+/(\d+)')
    PAGE_CRE = re.compile(r'document\.img_content\.src = "([^"]+)" \+ dropdown_value;')

    def __init__(self):
        Manga.__init__(self, 'http://www.nekopost.net')

    def _list_chapters(self, doc):
        chapters = []
        for n in doc.xpath("//ul[@class='chapter-list']/li[position()>1]/div[@class='service']"):
            u = n.xpath("a[text()='Read']")[0].attrib['href']
            m = self.CHAPTER_CRE.match(u)
            chapters.append({'chapter': int(m.group(1))})
        return chapters

    def _list_pages(self, doc):
        pages = doc.xpath("//select[@id='dropdown_page']/option")
        self.page_map = dict([(int(i.text), i.attrib['value']) for i in pages])
        pages = [int(i.text) for i in pages]
        m = self.PAGE_CRE.search(doc.xpath("//script[1]")[0].text)
        self.page_url = m.group(1)
        return pages

    def download_page(self, data):
        img_url = self.page_url+self.page_map[data['page']]
        filename = self.get_page_filename(data)
        filename += os.path.splitext(img_url)[-1].lower()
        fi = urlopen(img_url)
        fo = open(filename, 'wb')
        fo.write(fi.read())
        fo.close()

class NekoPostApp(App):
    def __init__(self):
        App.__init__(self)
        self.manga = NekoPost()

if __name__ == '__main__':
    app = NekoPostApp()
    app.run()

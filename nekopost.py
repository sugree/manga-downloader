#!/usr/bin/python

import re
import os

from manga import Manga, App, urlopen

class NekoPost(Manga):

    SERIES_URL = '%(baseurl)s/project/%(category)s/%(series)s'
    CHAPTER_URL = '%(baseurl)s/project/%(category)s/%(series)s/%(chapter)03d'
    PAGE_URL = '%(baseurl)s/project/%(category)s/%(series)s/%(chapter)03d'

    CHAPTER_CRE = re.compile(r'project/[^/]+/[^/]+/(\d+)')
    PAGE_CRE = re.compile(r'var file_path = "([^"]+)";')

    def __init__(self):
        Manga.__init__(self, 'http://www.nekopost.net')

    def _list_chapters(self, doc):
        chapters = []
        for n in doc.xpath("//ul[@class='list_chapter_ul']/li[position()>1]/div[@class='list_chapter_read']"):
            u = n.xpath("a[text()='Read']")[0].attrib['href']
            m = self.CHAPTER_CRE.match(u)
            chapters.append({'chapter': int(m.group(1))})
        return chapters

    def _list_pages(self, doc):
        pages = doc.xpath("//select[@id='dropdown_page']/option")
        self.page_map = dict([(int(i.text), i.attrib['value']) for i in pages])
        pages = [int(i.text) for i in pages]
        m = self.PAGE_CRE.search(doc.xpath("//script")[1].text)
        self.page_url = m.group(1)
        return pages

    def download_page(self, data):
        img_url = self.page_url+self.page_map[data['page']]
        filename = self.get_page_filename(data)
        filename += os.path.splitext(img_url)[-1].lower()
        content = urlretrieve(img_url)
        fo = open(filename, 'wb')
        fo.write(content)
        fo.close()

class NekoPostApp(App):
    def __init__(self):
        App.__init__(self)
        if self.options.category:
            self.data.update({'category': self.options.category})
        self.manga = NekoPost()

    def _parse_args(self, parser):
        App._parse_args(self, parser)
        parser.add_option('--category', dest='category', default='Manga',
                          help='Category e.g. manga, doujin, novel')

if __name__ == '__main__':
    app = NekoPostApp()
    app.run()

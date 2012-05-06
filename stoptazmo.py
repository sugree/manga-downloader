#!/usr/bin/python

from __future__ import print_function

import re
import os

from manga import Manga, App, urlretrieve

class StopTazmo(Manga):

    SERIES_URL = '%(baseurl)s/manga-series/%(series)s/'

    CHAPTER_PATTERN = '%(series)s-%(chapter)s.cbz'

    CHAPTER_CRE = re.compile(r'file_name=(?P<chapter_id>.*_(?P<chapter>[^.]+)\.zip)$')

    def __init__(self):
        Manga.__init__(self, 'http://stoptazmo.com')

    def _list_chapters(self, doc):
        chapters = []
        for n in doc.xpath("//div[@id='content']/table/tbody/tr[position()>1]"):
            u = n.xpath("td[2]/a")[0].attrib['href']
            m = self.CHAPTER_CRE.search(u)
            chapters.append({'chapter': m.group('chapter'),
                             'chapter_id': m.group('chapter_id'),
                             'chapter_url': u})
        return chapters

    def download_chapter(self, data):
        print(data)
        filename = self.get_chapter_filename(data)
        url = data['chapter_url']
        content = urlretrieve(url, headers=self.http_headers)
        fo = open(filename, 'wb')
        fo.write(content)
        fo.close()

    def chapter_exists(self, data):
        filename = self.get_chapter_filename(data)
        return os.path.exists(filename)

    def zip_chapter(self, pages, data):
        pass

    def remove_chapter(self, pages, data):
        pass

class StopTazmoApp(App):
    def __init__(self):
        App.__init__(self, chapter_func=str)
        self.manga = StopTazmo()

    def _parse_args(self, parser):
        App._parse_args(self, parser)

if __name__ == '__main__':
    app = StopTazmoApp()
    app.run()

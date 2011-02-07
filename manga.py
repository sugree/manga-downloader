import os
import re
from optparse import OptionParser
import urllib
import urllib2
import httplib
import zipfile

from lxml import etree as ET

user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'

def urlopen(*args):
    try:
        headers = {'User-Agent': user_agent,
                   'Referer': args[0],
                   'Accept': 'text/html,application/xhtml+xml,application/xml',
                   'Accept-Encoding': 'identity',
                   'Accept-Charset': 'utf-8',
                   'Connection': 'close'}
        req = urllib2.Request(*args, headers=headers)
        ret = urllib2.urlopen(req)
    except httplib.BadStatusLine, why:
        print httplib.BadStatusLine, args
        ret = urlopen(*args)
    except urllib2.URLError, why:
        print why, args
        ret = urlopen(*args)
    return ret

def extract_list(s, last, extract_range=True, func=int):
    l = []
    for i in s.split(','):
        if i.endswith('+'):
            l.extend(range(int(i[:-1]), last+1))
        elif extract_range and '-' in i:
            s, e = i.split('-')
            l.extend(range(int(s), int(e)+1))
        elif i:
            l.append(func(i))
    return l

class Manga:
    SERIES_URL = ''
    CHAPTER_URL = ''
    PAGE_URL = ''

    CHAPTER_PATTERN = '%(series)s-%(chapter)03d.cbz'
    PAGE_PATTERN = '%(series)s-%(chapter)03d-%(page)02d'

    def __init__(self, baseurl):
        self.baseurl = baseurl

    def get_series_url(self, data):
        d = data
        d.update({'baseurl': self.baseurl})
        return self.SERIES_URL % d

    def get_chapter_url(self, data):
        d = data
        d.update({'baseurl': self.baseurl})
        return self.CHAPTER_URL % d

    def get_page_url(self, data):
        d = data
        d.update({'baseurl': self.baseurl})
        return self.PAGE_URL % d

    def get_chapter_filename(self, data):
        d = data
        d.update({'baseurl': self.baseurl})
        return os.path.join(data['series'], self.CHAPTER_PATTERN % d)

    def get_page_filename(self, data):
        d = data
        d.update({'baseurl': self.baseurl})
        return os.path.join(data['series'], self.PAGE_PATTERN % d)

    def list_chapters(self, data):
        url = self.get_series_url(data)
        f = urlopen(url)
        doc = ET.HTML(f.read())
        chapters = self._list_chapters(doc)
        chapters.sort(lambda a, b: cmp(a['chapter'], b['chapter']))
        return chapters

    def list_pages(self, data):
        url = self.get_chapter_url(data)
        f = urlopen(url)
        doc = ET.HTML(f.read())
        pages = self._list_pages(doc)
        pages.sort()
        return pages

    def download_page(self, data):
        url = self.get_page_url(data)
        f = urlopen(url)
        doc = ET.HTML(f.read())
        img_url = self._download_page(doc)
        filename = self.get_page_filename(data)
        filename += os.path.splitext(img_url)[-1].lower()
        fi = urlopen(img_url)
        fo = open(filename, 'wb')
        fo.write(fi.read())
        fo.close()

    def download_chapter(self, data):
        pages = self.list_pages(data)
        for page in pages:
            data['page'] = page
            print data
            if not self.page_exists(data):
                self.download_page(data)
        return pages

    def chapter_exists(self, data):
        filename = self.get_chapter_filename(data)
        return os.path.exists(filename)

    def page_exists(self, data):
        filename = self.get_page_filename(data)
        return os.path.exists(filename+'.png') or os.path.exists(filename+'.jpg')

    def zip_chapter(self, pages, data):
        filename = self.get_chapter_filename(data)
        fo = zipfile.ZipFile(filename, 'w')
        for page in pages:
            data['page'] = page
            filename = self.get_page_filename(data)
            for ext in ['.png', '.jpg']:
                if os.path.exists(filename+ext):
                    filename += ext
                    break
            fo.write(filename, filename, zipfile.ZIP_STORED)

    def remove_chapter(self, pages, data):
        for page in pages:
            data['page'] = page
            filename = self.get_page_filename(data)
            for ext in ['.png', '.jpg']:
                if os.path.exists(filename+ext):
                    filename += ext
                    break
            os.unlink(filename)

class App:
    def __init__(self, extract_range=True, chapter_func=int):
        parser = OptionParser()
        self._parse_args(parser)
        self.options, self.args = parser.parse_args()
        self.series = self.args[0]
        self.extract_range = extract_range
        self.chapter_func = chapter_func

        self.data = {'series': self.series}

    def _parse_args(self, parser):
        parser.add_option('-C', '--chapter', dest='chapter', default='',
                          help='Chapter')

    def download_chapter(self, data):
        pages = self.manga.download_chapter(data)
        self.manga.zip_chapter(pages, data)
        self.manga.remove_chapter(pages, data)

    def run(self):
        if not os.path.exists(self.series):
            os.mkdir(self.series)
        chapters = self.manga.list_chapters(self.data)
        print chapters[0], chapters[-1]
        self.chapters = extract_list(self.options.chapter,
                                     chapters[-1]['chapter'],
                                     self.extract_range,
                                     self.chapter_func)
        for data in chapters:
            if self.chapters and data['chapter'] not in self.chapters:
                continue
            data.update(self.data)
            if not self.manga.chapter_exists(data):
                self.download_chapter(data)

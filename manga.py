import os
import re
from optparse import OptionParser
import urllib
import urllib2
import httplib
import zipfile
import socket
import gzip
import time

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from lxml import etree as ET

user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
http_timeout = 90
http_error_delay = 60

def urlopen(*args, **kwargs):
    ret = None
    while ret is None:
        ret = _urlopen(*args, **kwargs)
        if ret is None:
            time.sleep(http_error_delay)
    return ret

def urlretrieve(*args, **kwargs):
    ret = None
    while ret is None:
        ret = _urlretrieve(*args, **kwargs)
        if ret is None:
            time.sleep(http_error_delay)
    return ret

def _urlopen(*args, **kwargs):
    try:
        headers = {'User-Agent': user_agent,
                   'Referer': kwargs.get('referer', args[0]),
                   'Accept': 'text/html,application/xhtml+xml,application/xml,image/jpeg,image/png,image/gif',
                   'Accept-Encoding': 'identity',
                   'Accept-Charset': 'utf-8',
                   'Connection': 'close'}
        headers.update(kwargs.get('headers', {}))
        req = urllib2.Request(*args, headers=headers)
        ret = urllib2.urlopen(req, timeout=http_timeout)
    except httplib.BadStatusLine, why:
        print httplib.BadStatusLine, args
        ret = None
    except urllib2.HTTPError, why:
        print why, args
        ret = None
        if why.code == 404 and kwargs.get('raise404', False):
            raise why
    except urllib2.URLError, why:
        print why, args
        ret = None
    return ret

def _urlretrieve(*args, **kwargs):
    try:
        f = urlopen(*args, **kwargs)
        if f.info().get('Content-Encoding') == 'gzip':
            content = gzip.GzipFile(fileobj=StringIO(f.read())).read()
        else:
            content = f.read()
    except socket.error, why:
        print why, args
        content = None
    except socket.timeout, why:
        print why, args
        content = None
    return content

def smart_cmp(a, b):
    cre = re.compile(r'[^\d]')
    a = map(int, filter(lambda s: len(s) > 0, cre.split(str(a))))
    b = map(int, filter(lambda s: len(s) > 0, cre.split(str(b))))
    return cmp(a, b)

def extract_list(s, chapters, extract_range=True, func=int):
    l = []
    for i in s.split(','):
        if i.endswith('+'):
            try:
                s = chapters.index(func(i[:-1]))
                l.extend(chapters[s:])
#                l.extend(range(int(i[:-1]), int(last)+1))
            except ValueError:
                pass
        elif extract_range and '-' in i:
            try:
                s, e = i.split('-')
                s = chapters.index(func(s))
                e = chapters.index(func(e))
                l.extend(chapters[s:e+1])
#                l.extend(range(int(s), int(e)+1))
            except ValueError:
                pass
        elif i:
            l.append(func(i))
    return l

try:
    from PIL import Image
    def verify_image(s, uri):
        try:
            Image.open(StringIO(s)).load()
        except Exception, why:
            print why, uri
            return False
        return True
except ImportError:
    def verify_image(s, uri):
        return True

class Manga:
    SERIES_URL = ''
    CHAPTER_URL = ''
    PAGE_URL = ''

    CHAPTER_PATTERN = '%(series)s-%(chapter)03d.cbz'
    PAGE_PATTERN = '%(series)s-%(chapter)03d-%(page)02d'

    def __init__(self, baseurl, http_headers={}):
        self.baseurl = baseurl
        self.http_headers = http_headers

        self.options = {
            'ignore_empty': False,
            'max_retry': 60,
        }

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
        content = urlretrieve(url, headers=self.http_headers)
        doc = ET.HTML(content)
        chapters = self._list_chapters(doc)
        chapters.sort(lambda a, b: smart_cmp(a['chapter'], b['chapter']))
        return chapters

    def list_pages(self, data):
        url = self.get_chapter_url(data)
        content = urlretrieve(url, headers=self.http_headers)
        doc = ET.HTML(content)
        pages = self._list_pages(doc)
        pages.sort()
        return pages

    def download_page(self, data):
        url = self.get_page_url(data)
        content = urlretrieve(url, headers=self.http_headers)
        doc = ET.HTML(content)
        img_url = self._download_page(doc)
        filename = self.get_page_filename(data)
        ext = os.path.splitext(img_url)[-1].lower()
        if not ext:
            if img_url.lower().find('jpg') >= 0:
                ext = '.jpg'
            elif img_url.lower().find('png') >= 0:
                ext = '.png'
            else:
                ext = '.jpg'
        filename += ext
#        fi = urlopen(img_url, referer=url, headers=self.http_headers)
#        content = fi.read()

        count = 0
        while count < self.options['max_retry']:
            content = urlretrieve(img_url, referer=url, headers=self.http_headers)
            if verify_image(content, img_url):
                break
            if len(content) == 0 and self.options['ignore_empty']:
                print 'ignore empty', img_url
                break
            count += 1
        fo = open(filename, 'wb')
        fo.write(content)
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
        if not os.path.exists(filename):
            return False
        fi = zipfile.ZipFile(filename, 'r')
        for fname in fi.namelist():
            if fname.endswith('/'):
                continue
            if not verify_image(fi.open(fname, 'r').read(), fname):
                self.unzip_chapter(data)
                os.unlink(filename)
                return False
        return True

    def page_exists(self, data):
        filename = self.get_page_filename(data)
        for ext in ['.png', '.jpg', '.gif']:
            fname = filename+ext
            if os.path.exists(fname):
                if not verify_image(open(fname, 'rb').read(), fname):
                    os.unlink(fname)
                else:
                    return True
        return False

    def unzip_chapter(self, data):
        filename = self.get_chapter_filename(data)
        fi = zipfile.ZipFile(filename, 'r')
        for fname in fi.namelist():
            fi.extract(fname)

    def zip_chapter(self, pages, data):
        filename = self.get_chapter_filename(data)
        fo = zipfile.ZipFile(filename, 'w')
        for page in pages:
            data['page'] = page
            filename = self.get_page_filename(data)
            for ext in ['.png', '.jpg', '.gif']:
                if os.path.exists(filename+ext):
                    filename += ext
                    break
            fo.write(filename, filename, zipfile.ZIP_STORED)

    def remove_chapter(self, pages, data):
        for page in pages:
            data['page'] = page
            filename = self.get_page_filename(data)
            for ext in ['.png', '.jpg', '.gif']:
                if os.path.exists(filename+ext):
                    filename += ext
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
        parser.add_option('--ignore-empty', dest='ignore_empty', default=False,
                          action='store_true',
                          help='Ignore zero-size images')
        parser.add_option('--max-retry', dest='max_retry', default=60,
                          type='int',
                          help='Maximum retry for invalid images')

    def _filter_chapter(self, data):
        return (self.options.chapter or self.chapters) and \
               self.chapter_func(data['chapter']) not in self.chapters

    def download_chapter(self, data):
        pages = self.manga.download_chapter(data)
        self.manga.zip_chapter(pages, data)
        self.manga.remove_chapter(pages, data)

    def run(self):
        if not os.path.exists(self.series):
            os.mkdir(self.series)

        self.manga.options.update({
            'ignore_empty': self.options.ignore_empty,
            'max_retry': self.options.max_retry,
        })

        print self.series
        chapters = self.manga.list_chapters(self.data)
        print chapters[0], chapters[-1]
        self.chapters = extract_list(self.options.chapter,
                                     [c['chapter'] for c in chapters],
                                     self.extract_range,
                                     self.chapter_func)
        for data in chapters:
            if self._filter_chapter(data):
                continue
            data.update(self.data)
            if not self.manga.chapter_exists(data):
                self.download_chapter(data)

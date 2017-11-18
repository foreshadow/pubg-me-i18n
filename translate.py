from bs4 import BeautifulSoup as bs
from json import dumps, loads
from re import match
from urllib.request import Request, urlopen

class TranslateMap:

    def __init__(self, path):
        self.path = path
        self.map = {}
        json = '{}'
        try:
            f = open(path, encoding='u8')
            json = f.read()
            f.close()
        except Exception as e:
            print(e)
        self.map = loads(json)

    def _filter(self, key):
        return match('.*[A-Za-z].*', key)

    def _add(self, key):
        if not key in self.map:
            self.map[key] = key

    def tr(self, key):
        key = key.strip()
        if self._filter(key):
            self._add(key)
            return self.map[key]
        else:
            return key

    def dump(self):
        for key in sorted(self.map.keys()):
            print(key)

    def save(self):
        f = open(self.path, 'w', encoding='u8')
        f.write(dumps(self.map, sort_keys=True, indent='  ').encode('latin-1').decode('unicode_escape'))
        f.close()

lang = 'zh-CN'
subdir = '/pubg-me-i18n'
link_prefix = '{}/{}'.format(subdir, lang)

tm = TranslateMap('{}.json'.format(lang))

def translate(html):
    s = bs(html, 'html5lib')
    for item in s.find_all('script'):
        item.decompose()
    for item in s.find_all('link'):
        item.decompose()
    # s.find(attrs={'id': 'header'}).decompose()
    nav = s.find(attrs={'class': 'global-nav'}).find_all('li')
    nav[0].decompose()
    nav[3].decompose()
    s.find('form').decompose()
    s.find(attrs={'class': 'btn-signin'}).parent.parent.decompose()
    s.find(attrs={'id': 'footer'}).decompose()
    s.head.append(s.new_tag('link', href="{}/style.css".format(subdir), rel="stylesheet"))
    s.body.append(s.new_tag('script', src='https://cdn.bootcss.com/jquery/3.2.1/jquery.min.js'))
    s.body.append(s.new_tag('script', src='https://cdn.bootcss.com/popper.js/1.12.9/umd/popper.min.js'))
    s.body.append(s.new_tag('script', src='https://cdn.bootcss.com/bootstrap/4.0.0-beta.2/js/bootstrap.min.js'))
    for item in s.find_all('a'):
        if item['href'] and item['href'][0] == '/':
            item['href'] = link_prefix + item['href']

    for tag in ['h2', 'h5', 'span', 'th', 'td', 'div', 'p']:
        for item in s.find_all(tag):
            if item.string:
                item.string = tm.tr(item.string)
    for item in s.find_all(attrs={'class': 'label'}):
        if item.string:
            item.string = tm.tr(item.string)
    return s.prettify()

def crawl(url, file):
    print(url)
    request = Request(url, headers={'User-Agent': 'Infinity'})
    response = urlopen(request)
    html = translate(response.read())
    open(file, 'w', encoding='u8').write(html)

host = 'https://pubg.me'

for type in ['items', 'weapons']:
    url = '{}/{}'.format(host, type)
    file = 'docs/{}/{}/index.html'.format(lang, type)
    crawl(url, file)

for item in ['equipment', 'attachments', 'consumables', 'ammo']:
    url = '{}/items/{}'.format(host, item)
    file = 'docs/{}/items/{}.html'.format(lang, item)
    crawl(url, file)

for weapon in ['sniper-rifles', 'assault-rifles', 'submachine-guns', 'shotguns',
               'pistols', 'misc', 'melee', 'throwables']:
    url = '{}/weapons/{}'.format(host, weapon)
    file = 'docs/{}/weapons/{}.html'.format(lang, weapon)
    crawl(url, file)

tm.save()

from kodi_six import xbmc
import os, six, re
from packlib import client, kodi, dom_parser2, log_utils

from resources.lib.modules import local_utils
from resources.lib.modules import helper

buildDirectory = local_utils.buildDir
urljoin = six.moves.urllib.parse.urljoin

filename = os.path.basename(__file__).split('.')[0]
base_domain = 'https://spankbang.com'
base_name = base_domain.replace('www.', '');
base_name = re.findall('(?:\/\/|\.)([^.]+)\.', base_name)[0].title()
type = 'video'
menu_mode = 230
content_mode = 231
player_mode = 801

search_tag = 1
search_base = urljoin(base_domain, '/s/%s/')


@local_utils.url_dispatcher.register('%s' % menu_mode)
def menu():
    try:
        url = urljoin(base_domain, 'categories')
        c = client.request(url)
        r = dom_parser2.parse_dom(c, 'div', {'class': 'categories'})
        r = dom_parser2.parse_dom(r, 'a')
        r = [(i.attrs['href'], \
              dom_parser2.parse_dom(i, 'img', req='src')) \
             for i in r if i]
        r = [(urljoin(base_domain, i[0]), re.sub('<.+?>', '', i[1][0].content),
              urljoin(base_domain, i[1][0].attrs['src'])) for i in r]
        if (not r):
            log_utils.log('Scraping Error in %s:: Content of request: %s' % (base_name.title(), str(c)), xbmc.LOGERROR)
            kodi.notify(msg='Scraping Error: Info Added To Log File', duration=6000, sound=True)
            quit()
    except Exception as e:
        log_utils.log('Fatal Error in %s:: Error: %s' % (base_name.title(), str(e)), xbmc.LOGERROR)
        kodi.notify(msg='Fatal Error', duration=4000, sound=True)
        quit()

    dirlst = []

    for i in r:
        try:
            name = kodi.sortX(i[1].encode('utf-8'))
            fanarts = xbmc.translatePath(
                os.path.join('special://home/addons/script.adultflix.artwork', 'resources/art/%s/fanart.jpg' % filename))
            dirlst.append(
                {'name': name, 'url': i[0], 'mode': content_mode, 'icon': i[2], 'fanart': fanarts, 'folder': True})
        except Exception as e:
            log_utils.log('Error adding menu item %s in %s:: Error: %s' % (i[1].title(), base_name.title(), str(e)),
                          xbmc.LOGERROR)

    if dirlst:
        buildDirectory(dirlst)
    else:
        kodi.notify(msg='No Menu Items Found')
        quit()


@local_utils.url_dispatcher.register('%s' % content_mode, ['url'], ['searched'])
def content(url, searched=False):
    try:
        c = client.request(url)
        r = dom_parser2.parse_dom(c, 'div', {'class': 'video-item'})
        r = [(dom_parser2.parse_dom(i, 'a'), \
              dom_parser2.parse_dom(i, 'div', {'class': 'inf'}), \
              dom_parser2.parse_dom(i, 'img', req='src'), \
              dom_parser2.parse_dom(i, 'span', {'class': 'i-hd'})) \
             for i in r if i]
        r = [(urljoin(base_domain, i[0][0].attrs['href']), re.sub('<.+?>', '', i[1][0].content),
              urljoin(base_domain, i[2][0].attrs['src']), i[3][0].content if i[3] else 'SD') for i in r]
        if (not r) and (not searched):
            log_utils.log('Scraping Error in %s:: Content of request: %s' % (base_name.title(), str(c)), xbmc.LOGERROR)
            kodi.notify(msg='Scraping Error: Info Added To Log File', duration=6000, sound=True)
    except Exception as e:
        if (not searched):
            log_utils.log('Fatal Error in %s:: Error: %s' % (base_name.title(), str(e)), xbmc.LOGERROR)
            kodi.notify(msg='Fatal Error', duration=4000, sound=True)
            quit()
        else:
            pass

    dirlst = []

    for i in r:
        try:
            name = kodi.sortX(i[1].encode('utf-8')).title()
            name = name.title() + ' - [ %s ]' % i[3]
            if searched:
                description = 'Result provided by %s' % base_name.title()
            else:
                description = name
            content_url = i[0] + '|SPLIT|%s' % base_name
            fanarts = xbmc.translatePath(
                os.path.join('special://home/addons/script.adultflix.artwork', 'resources/art/%s/fanart.jpg' % filename))
            dirlst.append({'name': name, 'url': content_url, 'mode': player_mode, 'icon': i[2], 'fanart': fanarts,
                           'description': description, 'folder': False})
        except Exception as e:
            log_utils.log('Error adding menu item %s in %s:: Error: %s' % (i[1].title(), base_name.title(), str(e)),
                          xbmc.LOGERROR)

    if dirlst:
        buildDirectory(dirlst, stopend=True, isVideo=True, isDownloadable=True)
    else:
        if (not searched):
            kodi.notify(msg='No Content Found')
            quit()

    if searched: return str(len(r))

    if not searched:

        try:
            search_pattern = '''<li\s*class\=['"]next['"]\>\<a\s*href\=['"]([^'"]+)'''
            parse = base_domain
            helper.scraper().get_next_page(content_mode, url, search_pattern, filename, parse)
        except Exception as e:
            log_utils.log('Error getting next page for %s :: Error: %s' % (base_name.title(), str(e)), xbmc.LOGERROR)

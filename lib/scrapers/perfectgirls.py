from kodi_six import xbmc
import os, six, re
from packlib import client, kodi, dom_parser2, log_utils

from resources.lib.modules import local_utils
from resources.lib.modules import helper

buildDirectory = local_utils.buildDir
urljoin = six.moves.urllib.parse.urljoin

filename = os.path.basename(__file__).split('.')[0]
base_domain = 'http://www.perfectgirls.net'
base_name = base_domain.replace('www.', '');
base_name = re.findall('(?:\/\/|\.)([^.]+)\.', base_name)[0].title()
type = 'video'
menu_mode = 216
content_mode = 217
player_mode = 801

search_tag = 1
search_base = urljoin(base_domain, 'search/?q=%s')


@local_utils.url_dispatcher.register('%s' % menu_mode)
def menu():
    try:
        url = base_domain
        c = client.request(url)
        r = dom_parser2.parse_dom(c, 'li', {'class': 'header-submenu__item'})
        r = dom_parser2.parse_dom(r, 'a', req='href')
        r = [(i.attrs['href'], \
              i.content) for i in r if i]
        r = [(urljoin(base_domain, i[0]), i[1]) for i in r if i]
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
            name = kodi.sortX(i[1].encode('utf-8')).title()
            icon = xbmc.translatePath(
                os.path.join('special://home/addons/script.adultflix.artwork', 'resources/art/%s/icon.png' % filename))
            fanarts = xbmc.translatePath(
                os.path.join('special://home/addons/script.adultflix.artwork', 'resources/art/%s/fanart.jpg' % filename))
            dirlst.append(
                {'name': name, 'url': i[0], 'mode': content_mode, 'icon': icon, 'fanart': fanarts, 'folder': True})
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
        url = client.request(url, output='geturl')
        c = client.request(url)
        r = re.findall('<div class="list__item">(.*?)</div>', c, flags=re.DOTALL)
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
            name = re.findall('title="(.*?)"', i, flags=re.DOTALL)[0]
            if searched:
                description = 'Result provided by %s' % base_name.title()
            else:
                description = name
            content_url = re.findall('<a href="(.*?)"', i, flags=re.DOTALL)[0]
            if not base_domain in content_url: content_url = base_domain + content_url
            icon = re.findall('data-altsrc="(.*?)"', i, flags=re.DOTALL)[0]
            if not 'https' in icon: icon = 'https:' + icon
            fanarts = xbmc.translatePath(
                os.path.join('special://home/addons/script.adultflix.artwork', 'resources/art/%s/fanart.jpg' % filename))
            dirlst.append({'name': name, 'url': content_url, 'mode': player_mode, 'icon': icon, 'fanart': fanarts,
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
            pattern = r'''((?:http|https)(?:\:\/\/)(?:www)(?:\/\/|\.)(perfectgirls.net)\/(category\/)([0-9+]\/)(.+?\/))([0-9]+)'''
            r = re.search(pattern, url)
            base = r.group(1)
            search_pattern = '''<a\s*class=['"]btn_wrapper__btn['"]\s*href=['"]([^'"]+)['"]>Next'''
            parse = base
            helper.scraper().get_next_page(content_mode, url, search_pattern, filename, parse)
        except Exception as e:
            log_utils.log('Error getting next page for %s :: Error: %s' % (base_name.title(), str(e)), xbmc.LOGERROR)

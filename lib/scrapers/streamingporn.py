from kodi_six import xbmc
import os, six, re
from packlib import client, kodi, dom_parser2, log_utils
import xbmcgui

from resources.lib.modules import local_utils
from resources.lib.modules import helper

buildDirectory = local_utils.buildDir
urljoin = six.moves.urllib.parse.urljoin
dialog = xbmcgui.Dialog()
filename = os.path.basename(__file__).split('.')[0]
base_domain = 'http://streamingporn.xyz'
base_name = base_domain.replace('www.', '');
base_name = re.findall('(?:\/\/|\.)([^.]+)\.', base_name)[0].title()
type = 'movies'
menu_mode = 282
content_mode = 283
player_mode = 801

search_tag = 1
search_base = urljoin(base_domain, 'search/video/%s')


@local_utils.url_dispatcher.register('%s' % menu_mode)
def menu():
    url = 'http://streamingporn.xyz/category/movies/'

    content(url)


# try:
# url = base_domain
# c = client.request(url)
# r = re.findall('<header class="entry-header">(.*?)</h3>',c, flags=re.DOTALL)
# except Exception as e:
# log_utils.log('Fatal Error in %s:: Error: %s' % (base_name.title(),str(e)), xbmc.LOGERROR)
# kodi.notify(msg='Fatal Error', duration=4000, sound=True)
# quit()

# dirlst = []

# for i in r:
# try:
# name = re.findall('rel="bookmark">(.*?)</a>',i,flags=re.DOTALL)[0]
# url2 = re.findall('<a href="(.*?)"',i,flags=re.DOTALL)[0]
# icon = xbmc.translatePath(os.path.join('special://home/addons/script.adultflix.artwork', 'resources/art/%s/icon.png' % base_name))
# fanarts = xbmc.translatePath(os.path.join('special://home/addons/script.adultflix.artwork', 'resources/art/%s/fanart.jpg' % base_name))
# dirlst.append({'name': name, 'url': url2,'mode': content_mode, 'icon': icon, 'fanart': fanarts, 'folder': True})
# except Exception as e:
# log_utils.log('Error adding menu item. %s:: Error: %s' % (base_name.title(),str(e)), xbmc.LOGERROR)

# if dirlst: buildDirectory(dirlst)
# else:
# kodi.notify(msg='No Menu Items Found')
# quit()


@local_utils.url_dispatcher.register('%s' % content_mode, ['url'], ['searched'])
def content(url, searched=False):
    try:
        c = client.request(url)
        r = re.findall('<span class="overlay-img">(.*?)</h3>', c, flags=re.DOTALL)
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
            name = re.findall('rel="bookmark">(.*?)</a>', i, flags=re.DOTALL)[0]
            url2 = re.findall('<a href="(.*?)"', i, flags=re.DOTALL)[0]
            # icon = xbmc.translatePath(os.path.join('special://home/addons/script.adultflix.artwork', 'resources/art/%s/icon.png' % base_name))
            icon = re.findall('<img src="(.*?)"', i, flags=re.DOTALL)[0]
            fanarts = xbmc.translatePath(
                os.path.join('special://home/addons/script.adultflix.artwork', 'resources/art/%s/fanart.jpg' % filename))
            dirlst.append(
                {'name': name, 'url': url2, 'mode': player_mode, 'icon': icon, 'fanart': fanarts, 'folder': False})
        except Exception as e:
            log_utils.log('Error adding menu item. %s:: Error: %s' % (base_name.title(), str(e)), xbmc.LOGERROR)
    if dirlst:
        buildDirectory(dirlst, stopend=True, isVideo=True, isDownloadable=True)
    else:
        if (not searched):
            kodi.notify(msg='No Content Found')
            quit()

    if searched: return str(len(r))

    if not searched:
        search_pattern = '''<link\s+rel="next"\s+href=['"]([^'"]+)['"]'''
        parse = base_domain
        helper.scraper().get_next_page(content_mode, url, search_pattern, filename, parse)

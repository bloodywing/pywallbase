import re
import base64
import requests
from math import ceil
from random import randint
from HTMLParser import HTMLParser

#  Static stuff like Wallbase.cc URL

URL = "http://wallbase.cc/"
session = requests.Session()
jsonheaders = {"X-Requested-With": "XMLHttpRequest"}


class Wallbase(object):

    def __init__(self, username, password):
        """
        Args:
           username (str): a Wallbase.cc Login
           password (str): The Users Password
        """
        self.collections = CollectionsList()
        self.searchbags = SearchbagList()
        self._login(username, password)

    def _login(self, username, password):
        response = session.post("%suser/login" % URL,
                data={"usrname": username,"pass":password},
                allow_redirects=False)
        self.cookies = response.cookies
        return response.cookies

    def get_collections(self):
        response = session.get(
            "%suser/favorites/-1/%d" % (URL, randint(1, 1000)),
                headers=jsonheaders)
        if response.status_code == 200:
            json = response.json()

            self.collections.append(Collection())  # Adds 'Home'

            for c in json[0]:
                collection_dict = c.pop()
                self.collections.append(
                    Collection(cid=int(collection_dict["coll_id"]),
                        public=collection_dict["coll_permissions"],
                        name=collection_dict["coll_title"],
                        fav_count=int(collection_dict["fav_count"])))
        return self.collections

    def add_collection(self, collname, permission=0):
        response = session.post(
            "%suser/favorites_new/collection/%d" % (URL, randint(1,1000)), data={"title": collname, "permissions": permission}, headers=jsonheaders)
        if response.status_code == 200:
            return response.content.split("|")[1]
        else:
            return False

    def del_collection(self, coll_id):
        response = session.get("%suser/favorites_delete/coll/%d/%d" % (URL, coll_id, randint(1, 1000)), headers=jsonheaders)
        if response.status_code == 200:
            if response.content == "1":
                return True
        return False

    def add_to_favorites(self, wall_id, coll_id):
        response = session.get("%suser/favorites_new/thumb/%d/%d/%d" % (URL, wall_id, coll_id, randint(1, 1000)), headers=jsonheaders)
        if response.status_code == 200:
            return True
        return False

    def search(self, query, page=None, **kwargs):
        """Search for something on wallbase.cc this can be a normal String or a tag like "tag:12345"

        >>> search("batman", nsfw_nsfw=1, nsfw_sfw=1, nsfw_sketchy=1)
        """

        page_offset = 0
        data = dict(
            query=query,
            thpp=100
        )

        data.update(kwargs)

        searchbag = Searchbag(query)
        self.searchbags.append(searchbag)

        # determint how many wallpapers have been found
        response = session.post("%ssearch" % (URL), data=data)

        try:
            total_wp = int(re.search("Search\.vars\.results_count\s\=\s(\d+)", response.content).group(1))
        except:
            print "No wps :("
            total_wp = 0

        total_pages = int(ceil(total_wp / float(data.get('thpp'))))

        if page:
            page_range = [page]
        else:
            page_range = range(1, total_pages)

        for page in page_range:

            response = session.post(
                "%ssearch/%d" % (URL, page * data.get('thpp')), data=data, headers=jsonheaders
            )

            if len(response.json()):
                json = response.json()
                for w in json:
                    if w is not None:
                        
                        try:
                            tags = w["attrs"]["wall_tags"].split("|")[0::4]
                        except AttributeError:
                            tags = []
                        
                        searchbag.wallpapers.append(
                            Wallpaper(wid=int(w["id"]), 
                                      cid=int(w["attrs"]["wall_cat_id"]),
                                      wall_imgtype=int(w["attrs"]["wall_imgtype"]),
                                      tags=tags
                                      )
                        )
                    else:
                        return searchbag.wallpapers
        return searchbag.wallpapers


    def get_wallpapers_by_cid(self, cid):

        if not len(self.collections):
            raise RuntimeWarning("Please call get_collections() first")

        wallpapers = []
        page_offset = 0
        collection = self.collections.get_by_cid(cid)

        if not collection.wallpapers:
            while True:
                response = session.get("%suser/favorites/%d/%d/0/666" % (
                    URL, cid, page_offset), headers=jsonheaders)

                if not len(response.json()):
                    return collection.wallpapers
                else:
                    json = response.json().pop()
                    for wallpaper in json:
                        w = wallpaper.pop()
                        try:
                            tags = w["wall_tags"].split("|")[0::4]
                        except AttributeError:
                            tags = []
                        collection.wallpapers.append(
                                Wallpaper(wid=int(w[
                                          "wall_id"]), cid=cid, wall_cat_dir=w["wall_cat_dir"], wall_imgtype=int(w["wall_imgtype"]), tags=tags)
                        )
                    page_offset += 40
        return collection.wallpapers


class CollectionsList(list):

    """
    makes it easy to handle the collections
    """
    def get_by_cid(self, cid):
        for c in self:
            if c.cid == cid:
                return c

class SearchbagList(list):
    def get_by_query(self, query):
        for q in self:
            if q.query == query:
                return q

class Collection(object):

    def __init__(self, public=False, cid=-1, name="Home", fav_count=0):
        self.cid = cid
        self.name = name
        self.public = public
        self.fav_count = fav_count
        self.wallpapers = []

    def __repr__(self):
        return "<%d, %s>" % (self.cid, self.name)


class Searchbag(object):

    def __init__(self, query):
        self.query = query
        self.wallpapers = []

    @property
    def wallpaper_count(self):
        return len(self.wallpapers)

    def __repr__(self):
        return "<%s, %d>" % (self.query, self.wallpaper_count)


class Wallpaper(object):

    def __init__(self, wid, cid, wall_cat_dir="Unknown", wall_imgtype=1, tags=[]):
        self.wid = wid
        self.cid = cid
        self.wall_cat_dir = wall_cat_dir
        self.wall_imgtype = wall_imgtype
        self.tags = tags

    @property
    def extension(self):
        if self.wall_imgtype == 2:
            return "png"
        else:
            return "jpg"

    @property
    def blob(self):
        return session.get(self.url).content

    @property
    def url(self):
        parser = WallpaperParser()
        response = session.get("%swallpaper/%d" % (URL, self.wid))
        parser.feed(response.content)
        if parser.wallpaperurl:
            return parser.wallpaperurl

    @property
    def dict(self):
        return dict(
            wid=self.wid,
            cid=self.cid,
            wall_cat_dir=self.wall_cat_dir,
            wall_imgtype=self.wall_imgtype,
            tags=self.tags,
            url=self.url,
            extension=self.extension
        )

class WallpaperParser(HTMLParser):

    def handle_data(self, data):
        pattern = re.compile("(?<=\'\+B\(\')[\w\+\/\=]+")
        if pattern.search(data):
            self.wallpaperurl = base64.b64decode(pattern.search(data).group(0))

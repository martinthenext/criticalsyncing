import tornado.web
import tornado.gen
import logging
import json
import redis
from .fetcher import Fetcher

logger = logging.getLogger(__name__)


class SourceHandler(tornado.web.RequestHandler):
    rkey = "sources"

    def initialize(self):
        self.rclient = redis.Redis(
            connection_pool=self.application.settings["rpool"])

    def not_allowed(self, ident):
        if ident is None:
            self.set_status(405)
            self.set_header("Allow", "GET")
            self.finish()

    def get(self, ident=None):
        logger.debug(ident)
        if not self.rclient.exists(self.rkey):
            if ident:
                self.set_status(404)
            else:
                self.write({})
            self.finish()
        if not ident:
            sources = dict(
                map(lambda x: (x[0], json.loads(x[1])),
                    self.rclient.hgetall(self.rkey).items()))
            self.write(sources)
            self.finish()
        else:
            source = self.rclient.hget(self.rkey, ident)
            if source:
                self.write(json.loads(source))
            else:
                self.set_status(404)
            self.finish()

    def put(self, ident=None):
        self.not_allowed(ident)
        ctype = self.request.headers.get("Content-Type")
        if ctype != "application/json":
            self.set_status(415)
            self.finish()
        try:
            source = json.loads(self.request.body)
        except ValueError, error:
            logger.exception(error)
            self.set_status(406)
            self.finish()
        if not self.rclient.hexists(self.rkey, ident):
            logger.debug("resource created: %s", self.request.uri)
            self.set_status(201)
            self.set_header("Location", self.request.uri)
        self.rclient.hset(self.rkey, ident, json.dumps(source))
        self.finish()

    def delete(self, ident=None):
        self.not_allowed(ident)
        if self.rclient.hexists(self.rkey, ident):
            self.rclient.hdel(self.rkey, ident)
            logger.debug("resource deleted: %s", self.request.uri)
        else:
            self.set_status(404)
        self.finish()


class FetchArticleHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.fetcher = Fetcher()

    @tornado.gen.coroutine
    def get(self):
        url = self.get_query_argument("url")
        try:
            url, value = yield self.fetcher.fetch(url)
            self.write(value)
        except Fetcher.FetchException:
            self.set_status(500)


class CrawlHandler(tornado.web.RequestHandler):
    rkey = "sources"

    def initialize(self):
        self.rclient = redis.Redis(
            connection_pool=self.application.settings["rpool"])
        self.fetcher = Fetcher()

    @tornado.gen.coroutine
    def get(self, ident=None):
        if ident:
            source = self.rclient.hget(self.rkey, ident)
            if not source:
                self.set_status("404")
                self.finish()
            sources = {ident: source}
        else:
            sources = dict(
                map(lambda x: (x[0], json.loads(x[1])),
                    self.rclient.hgetall(self.rkey).items()))
        result = yield self.fetcher.crawl(self.rclient, sources)
        self.write(result)
        self.finish()

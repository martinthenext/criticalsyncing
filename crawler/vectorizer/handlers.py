import tornado.web
import tornado.gen
import logging
import json
import redis

logger = logging.getLogger(__name__)


class UpdateMatricesHandler(tornado.web.RequestHandler):
    rkey = "sources"

    def initialize(self):
        self.rclient = redis.Redis(
            connection_pool=self.application.settings["rpool"])
        self.fetcher = self.application.settings["fetcher"]

    @tornado.gen.coroutine
    def get(self, ident=None):
        logger.debug("source id: %s", ident)
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
        logger.debug("sources: \n%s", sources)
        urls = yield self.fetcher.crawl(self.rclient, sources)
        self.set_status(200)
        self.write(result)
        self.finish()


class RebuildMatricesHandler(tornado.web.RequestHandler):
    rkey = "sources"

    def initialize(self):
        self.rclient = redis.Redis(
            connection_pool=self.application.settings["rpool"])

    @tornado.gen.coroutine
    def get(self, ident=None):
        logger.debug("source id: %s", ident)
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
        logger.debug("sources: \n%s", sources)
        result = yield self.fetcher.crawl(self.rclient, sources)
        self.set_status(200)
        self.write(result)
        self.finish()

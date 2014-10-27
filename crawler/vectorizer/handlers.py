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
        self.vectorizer = self.application.settings["vectorizer"]

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
        logger.debug("urls: \n%s", urls)
        self.vectorizer.update(self.rclient, urls.iterkeys())
        self.set_status(200)
        self.write(urls)
        self.finish()


class RebuildMatricesHandler(tornado.web.RequestHandler):
    rkey = "sources"

    def initialize(self):
        self.rclient = redis.Redis(
            connection_pool=self.application.settings["rpool"])
        self.vectorizer = self.application.settings["vectorizer"]

    def get(self):
        self.vectorizer.rebuild(self.rclient)
        self.set_status(204)
        self.finish()

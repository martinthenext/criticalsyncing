import tornado.web
import tornado.gen
import logging
import json
import redis
from common.atomic import RedisLock

logger = logging.getLogger(__name__)


class UpdateMatricesHandler(tornado.web.RequestHandler):
    rkey = "sources"

    def initialize(self):
        self.rclient = redis.Redis(
            connection_pool=self.application.settings["rpool"])
        self.fetcher = self.application.settings["fetcher"]
        self.vectorizer = self.application.settings["vectorizer"]
        self.rlock = RedisLock(self.rclient, "write_lock")

    @tornado.gen.coroutine
    def post(self, ident=None):
        logger.debug("source id: %s", ident)
        if ident:
            source = json.loads(self.rclient.hget(self.rkey, int(ident)))
            if not source:
                self.set_status("404")
                self.finish()
            sources = {ident: source}
        else:
            sources = dict(
                map(lambda x: (x[0], json.loads(x[1])),
                    self.rclient.hgetall(self.rkey).items()))
        logger.debug("sources: \n%s", sources)
        if not self.rlock.acquire():
            logger.debug("updating process already started")
            self.set_status(202)
            self.finish()
        try:
            urls = yield self.fetcher.crawl(self.rclient, sources)
            logger.debug("urls: \n%s", urls)
            self.vectorizer.update(self.rclient, urls.iterkeys())
        finally:
            self.rlock.release()
        self.set_status(200)
        self.write(urls)
        self.finish()


class RebuildMatricesHandler(tornado.web.RequestHandler):
    rkey = "sources"

    def initialize(self):
        logger.debug("initialize")
        self.rclient = redis.Redis(
            connection_pool=self.application.settings["rpool"])
        self.vectorizer = self.application.settings["vectorizer"]
        try:
            self.rlock = RedisLock(self.rclient, "write_lock")
        except Exception, e:
            logger.exception(e)
        logger.debug(1)

    def post(self):
        logger.debug("get")
        if not self.rlock.acquire():
            logger.debug("updating process already started")
            self.set_status(202)
            self.finish()
        try:
            self.vectorizer.rebuild(self.rclient)
        finally:
            self.rlock.release()
        self.set_status(204)
        self.finish()


class MatchArticleHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.fetcher = self.application.settings["fetcher"]
        self.vectorizer = self.application.settings["vectorizer"]
        self.rclient = redis.Redis(
            connection_pool=self.application.settings["rpool"])

    @tornado.gen.coroutine
    def get(self):
        url = self.get_arguments("url")[0]
        code, url, value = yield self.fetcher.fetch(url)
        if code != 200:
            self.set_status(code, reason=value)
            self.finish()
        else:
            url = self.vectorizer.match(self.rclient, value)
            self.write({"url": url})

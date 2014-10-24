import tornado.ioloop
import tornado.web
import tornado.httpclient
from tornado.options import define, options
from logging.config import dictConfig
from argparse import ArgumentParser
import yaml
import os
import redis

from crawler.handlers import SourceHandler
from crawler.handlers import CrawlHandler
from crawler.handlers import FetchArticleHandler


def application():
    rpool = redis.ConnectionPool(
        **dict(zip(["host", "port", "db"], options.redis.split(":"))))
    app = tornado.web.Application([
        (r"/sources/?", SourceHandler),
        (r"/sources/(?P<ident>\d+)", SourceHandler),
        (r"/commands/fetch/?", FetchArticleHandler),
        (r"/commands/crawl/?", CrawlHandler),
        (r"/commands/crawl/(?P<ident>\d+)", CrawlHandler),
    ], compress_response=True, rpool=rpool, debug=True)
    return app

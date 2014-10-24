#!/usr/bin/env python
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


def get_args():
    parser = ArgumentParser()
    parser.add_argument("-c", "--config",
                        default=os.path.join(os.getcwd(), "crawler.cfg"))
    return parser.parse_args()


def config():
    args = get_args()
    define("redis",
           default="127.0.0.1:6379:0",
           help="redis database connection")
    define("log_settings",
           default=os.path.join(os.path.dirname(args.config), "logging.yaml"),
           help="logging settings file")
    define("crawler_port", default=8080, type=int,
           help="crawler incomming port")
    define("crawler_address", default="127.0.0.1",
           help="crawler bind address")
    options.logging = None
    if os.path.exists(args.config):
        tornado.options.parse_config_file(args.config)
    with open(options.log_settings) as h:
        dictConfig(yaml.load(h.read()))
    tornado.httpclient.AsyncHTTPClient.configure(
        "tornado.curl_httpclient.CurlAsyncHTTPClient")


def main():
    config()
    app = application()
    app.listen(options.crawler_port, address=options.crawler_address)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()

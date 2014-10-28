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
from vectorizer.handlers import UpdateMatricesHandler
from vectorizer.handlers import RebuildMatricesHandler
from crawler.fetcher import Fetcher
from vectorizer.vectorizer import Vectorizer


def application():
    rpool = redis.ConnectionPool(
        **dict(zip(["host", "port", "db"], options.redis.split(":"))))
    fetcher = Fetcher(options.fetcher_timeout, options.fetcher_threads,
                      options.fetcher_language, options.fetcher_max_articles,
                      options.fetcher_min_length, options.fetcher_max_length,
                      options.fetcher_user_agent, options.fetcher_expire)
    vectorizer = Vectorizer(options.vectorizer_pickles_directory,
                            options.vectorizer_max_features,
                            options.vectorizer_min_df,
                            options.vectorizer_max_df)
    app = tornado.web.Application([
        (r"/sources/?", SourceHandler),
        (r"/sources/(?P<ident>\d+)", SourceHandler),
        (r"/commands/fetch/?", FetchArticleHandler),
        (r"/commands/crawl/?", CrawlHandler),
        (r"/commands/update_matrices/?", UpdateMatricesHandler),
        (r"/commands/update_matrices/(?P<ident>\d+)", UpdateMatricesHandler),
        (r"/commands/rebuild_matrices/?", RebuildMatricesHandler),
    ], compress_response=True, rpool=rpool, debug=True, fetcher=fetcher,
        vectorizer=vectorizer)
    return app

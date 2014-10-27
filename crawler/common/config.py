from argparse import ArgumentParser
from logging.config import dictConfig
from tornado.options import define, options
import os
import tornado.httpclient
import yaml


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
    define("fetcher_timeout", default=30, type=int,
           help="each request timeout")
    define("fetcher_threads", default=10, type=int,
           help="fetcher threads count")
    define("fetcher_language", default="en",
           help="article language")
    define("fetcher_max_articles", default=500, type=int,
           help="max articles count from source")
    define("fetcher_max_length", default=200000, type=int,
           help="max text length")
    define("fetcher_min_length", default=200, type=int,
           help="min text length")
    define("fetcher_user_agent", default="criticalsyncing/crawler",
           help="user agent")
    define("fetcher_expire", default=2592000, type=int,
           help="article time to live")
    define("vectorizer_pickles_directory",
           default=os.path.join(os.path.dirname(args.config), "pickles"),
           help="directory with serialized tfidf matrices")
    define("vectorizer_max_features", default=200, type=int,
           help="max features count")
    define("vectorizer_max_df", default=1.0, type=float,
           help="max df")
    define("vectorizer_min_df", default=0.0, type=float,
           help="min df")
    options.logging = None
    if os.path.exists(args.config):
        tornado.options.parse_config_file(args.config)
    with open(options.log_settings) as h:
        dictConfig(yaml.load(h.read()))
    tornado.httpclient.AsyncHTTPClient.configure(
        "tornado.curl_httpclient.CurlAsyncHTTPClient")

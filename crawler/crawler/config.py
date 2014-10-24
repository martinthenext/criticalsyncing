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
    options.logging = None
    if os.path.exists(args.config):
        tornado.options.parse_config_file(args.config)
    with open(options.log_settings) as h:
        dictConfig(yaml.load(h.read()))
    tornado.httpclient.AsyncHTTPClient.configure(
        "tornado.curl_httpclient.CurlAsyncHTTPClient")

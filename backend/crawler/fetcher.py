import tornado.gen
import tornado.httpclient
import newspaper
import json
import logging
from itertools import ifilterfalse, imap


logger = logging.getLogger(__name__)


class Fetcher:
    def __init__(self, timeout=30, threads=10, language="en",
                 max_articles=500, min_length=200, max_length=200000,
                 user_agent="criticalsyncing/crawler",
                 expire=2592000):
        self.timeout = timeout
        logger.info("timeout: %s", timeout)
        self.threads = threads
        logger.info("threads: %s", threads)
        self.language = language
        logger.info("language: '%s'", language)
        self.max_articles = max_articles
        logger.info("max articles: %s", max_articles)
        self.min_length = min_length
        logger.info("min text length: %s", min_length)
        self.max_length = max_length
        logger.info("max text length: %s", max_length)
        self.hclient = tornado.httpclient.AsyncHTTPClient()
        self.user_agent = user_agent
        logger.info("user agent: '%s'", user_agent)
        self.expire = expire * 1000  # 1 month by defaut
        logger.info("articles TTL: %s seconds", expire)

    @tornado.gen.coroutine
    def fetch(self, url, source_url=None, title=None, **kwargs):
        logger.info("fetching url %s", url)
        article = newspaper.Article(
            url=url, title=title)
        html = None
        try:
            html = yield self.download_html(url)
        except Exception, error:
            logger.exception(error)
        if not html:
            raise tornado.gen.Return(
                (500, url, "could not download article"))
        article = self.parse_article(article, html)
        if not article:
            raise tornado.gen.Return(
                (500, url, "could not parse article"))
        article = self.check_article_length(article)
        if not article:
            raise tornado.gen.Return(
                (500, url, "article's text length not in range"))
        article = self.nlp(article)
        raise tornado.gen.Return(
            (200, url, self.make_value(article, **kwargs)))

    @tornado.gen.coroutine
    def crawl(self, rclient, sources):
        sources = imap(lambda x: (x[0], x[1].get("url")), sources.viewitems())
        result = {}

        for source_id, source_url in sources:
            if not source_url:
                logger.error("source %s does not contains 'url'", source_id)
                continue

            logger.info("crawling source: %s: %s", source_id, source_url)
            batch = []
            for url, title in self.get_article_urls(rclient, source_url):
                batch.append(self.fetch(
                    url, source_url=source_url,
                    title=title, source_id=source_id, valid=True))

                if len(batch) < self.threads:
                    continue

                keys = yield self.save_articles(rclient, source_id, batch)
                result.update(keys)
                batch = []

            if batch:
                keys = yield self.save_articles(rclient, source_id, batch)
                result.update(keys)

            logger.info("dump redis to disk")
            rclient.save()
        raise tornado.gen.Return(result)

    def get_article_urls(self, rclient, source_url):
        paper = newspaper.build(
            source_url, memoize_articles=False, fetch_images=False,
            request_timeout=self.timeout, number_threads=self.threads,
            language=self.language, browser_user_agent=self.user_agent)
        urls = ((a.url, a.title) for a in paper.articles[:self.max_articles])
        return ifilterfalse(lambda x: rclient.exists(x[0]), urls)

    @tornado.gen.coroutine
    def save_articles(self, rclient, source_id, chunk):
        keys = {}
        logger.info("waiting for chunk")
        results = yield chunk
        for code, url, value in results:
            if code != 200:
                logger.warning("url '%s' is invalid: code '%s': %s",
                               url, code, value)
                rclient.set(url, json.dumps({"valid": False}), self.expire)
                continue
            logger.info("save value for url '%s'", url)
            rclient.set(url, json.dumps(value), self.expire)
            keys[url] = source_id
        raise tornado.gen.Return(keys)

    @tornado.gen.coroutine
    def download_html(self, url):
        logger.debug("download url: %s", url)
        response = yield self.hclient.fetch(
            url, user_agent=self.user_agent,
            request_timeout=self.timeout,
            follow_redirects=True,
            validate_cert=True)
        if response.code != 200:
            logger.error("could not download article by url '%s': %s",
                         url, response.code)
            raise tornado.gen.Return()
        raise tornado.gen.Return(response.body)

    def parse_article(self, article, html):
        logger.debug("parse html on url: %s", article.url)
        try:
            article.set_html(html)
            article.parse()
        except Exception, error:
            logger.error("could not extract text from article: %s",
                         article.url)
            logger.exception(error)
            return
        return article

    def check_article_length(self, article):
        logger.debug("check text length on url: %s", article.url)
        if not (self.min_length < len(article.text) < self.max_length):
            logger.info("text length of article '%s' is not in range: %s",
                        article.url, len(article.text))
            return
        return article

    def nlp(self, article):
        logger.debug("perform nlp on url: %s", article.url)
        try:
            original = article.text
            # fix https://github.com/codelucas/newspaper/issues/77
            article.text = original.encode(errors='replace')
            article.nlp()
            article.text = original
        except Exception, error:
            logger.warning("could not extract keywords and authors "
                           "from article: %s", article.url)
            logger.exception(error)
        return article

    def make_value(self, article, **kwargs):
        value = dict(
            text=article.text, title=article.title, url=article.url,
            authors=article.authors, keywords=article.keywords,
            top_image=article.top_image, images=article.images, **kwargs)
        return value

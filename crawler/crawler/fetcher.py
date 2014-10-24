import tornado.gen
import tornado.httpclient
import newspaper
import json
import logging
from itertools import ifilterfalse


logger = logging.getLogger(__name__)


class Fetcher:

    class FetchException(RuntimeError):
        pass

    def __init__(self, timeout=10, threads=10, language="en",
                 max_articles=500, min_length=200, max_length=200000,
                 user_agent="criticalsyncing/crawler",
                 expire=2592000):
        self.timeout = timeout
        self.threads = threads
        self.language = language
        self.max_articles = max_articles
        self.min_length = min_length
        self.max_length = max_length
        self.hclient = tornado.httpclient.AsyncHTTPClient()
        self.user_agent = user_agent
        self.expire = expire  # 1 month by defaut

    @tornado.gen.coroutine
    def fetch(self, url, source_url=None, title=None, **kwargs):
        logger.info("fetching url %s", url)
        article = newspaper.Article(
            url=url, title=title)
        html = yield self.download(url)
        if not html:
            raise Fetcher.FetchException()
        article = self.parse(article, html)
        if not article:
            raise Fetcher.FetchException()
        article = self.check_length(article)
        if not article:
            raise Fetcher.FetchException()
        article = self.nlp(article)
        raise tornado.gen.Return((url, self.make_value(article, **kwargs)))

    @tornado.gen.coroutine
    def crawl(self, rclient, sources):
        sources = imap(lambda x: (x[0], x[1]["url"]), sources.itemsview())
        keys = {}
        for source_id, source_url in self.sources:
            logger.info("crawling source: %s: %s", source_id, source_url)
            paper = newspaper.build(source_url,
                                    memoize_articles=False,
                                    fetch_images=False,
                                    timeout=self.timeout,
                                    number_threads=self.threads,
                                    language=self.language)
            urls = ((a.url, a.title) for a in
                    paper.articles[:self.max_articles])
            new_urls = ifilterfalse(lambda x: rclient.exists(x[0]), urls)
            for url, title in new_urls:
                try:
                    url, value = yield self.fetch(
                        url, source_url=source_url,
                        title=title, source_id=source_id)
                    rclient.set(url, value, self.expire * 1000)
                    self.keys[url] = source_id
                except Fetcher.FetchException:
                    continue
        rclient.sync()
        raise tornado.gen.Return(self.keys)

    @tornado.gen.coroutine
    def download(self, url):
        logger.debug("download url: %s", url)
        response = yield self.hclient.fetch(
            url, user_agent=self.user_agent,
            request_timeout=self.timeout,
            validate_cert=True)
        if response.code != 200:
            logger.error("could not download article by url '%s': %s",
                         url, response.code)
            raise tornado.gen.Return()
        raise tornado.gen.Return(response.body)

    def parse(self, article, html):
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

    def check_length(self, article):
        logger.debug("check text length on url: %s", article.url)
        if not (self.min_length < len(article.text) < self.max_length):
            logger.info("text length of article '%s' is not in range",
                        article.url)
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

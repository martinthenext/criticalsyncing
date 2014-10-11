from django.db import models
from django.db.utils import IntegrityError
from django.conf import settings
import newspaper
import json
import logging


logger = logging.getLogger(__name__)

# have no get function in settings :(
NEWSPAPER_TIMEOUT = 10
if hasattr(settings, "NEWSPAPER_TIMEOUT"):
    NEWSPAPER_TIMEOUT = settings.NEWSPAPER_TIMEOUT
NEWSPAPER_MAX_ARTICLES = 100
if hasattr(settings, "NEWSPAPER_MAX_ARTICLES"):
    NEWSPAPER_MAX_ARTICLES = settings.NEWSPAPER_MAX_ARTICLES
NEWSPAPER_THREADS_COUNT = 10
if hasattr(settings, "NEWSPAPER_THREADS_COUNT"):
    NEWSPAPER_THREADS_COUNT = settings.NEWSPAPER_THREADS_COUNT
NEWSPAPER_LANGAUGE = 'en'
if hasattr(settings, "NEWSPAPER_LANGAUGE"):
    NEWSPAPER_LANGAUGE = settings.NEWSPAPER_LANGAUGE
NEWSPAPER_MIN_ARTICLE_LENGTH = 200
if hasattr(settings, "NEWSPAPER_MIN_ARTICLE_LENGTH"):
    NEWSPAPER_MIN_ARTICLE_LENGTH = settings.NEWSPAPER_MIN_ARTICLE_LENGTH
NEWSPAPER_MAX_ARTICLE_LENGTH = 200000
if hasattr(settings, "NEWSPAPER_MAX_ARTICLE_LENGTH"):
    NEWSPAPER_MAX_ARTICLE_LENGTH = settings.NEWSPAPER_MAX_ARTICLE_LENGTH


class ArticleDownloadManager(models.Manager):
    def download_from(self, source):
        paper = newspaper.build(source.url,
                                memoize_articles=False,
                                fetch_images=False,
                                timeout=NEWSPAPER_TIMEOUT,
                                number_threads=NEWSPAPER_THREADS_COUNT,
                                language=NEWSPAPER_LANGAUGE)
        logger.debug("paper %s size: %d", source.url, paper.size())
        articles = paper.articles[:NEWSPAPER_MAX_ARTICLES]
        fetched_urls = [a.url for a in articles]
        known_urls = self.filter(source=source).values_list("url", flat=True)
        unknown_urls = set(fetched_urls) - set(known_urls)
        for article in filter(lambda a: a.url in unknown_urls, articles):
            try:
                article.download()
                article.parse()
                original = article.text
                # fix https://github.com/codelucas/newspaper/issues/77
                article.text = original.encode(errors='replace')
                article.nlp()
                article.text = original
            except Exception, error:
                logger.exception(error)
                continue

            if len(article.text) < NEWSPAPER_MIN_ARTICLE_LENGTH:
                logger.info("article '%s'(%s) is too short: %s",
                            article.title, article.url, len(article.text))
                continue
            if len(article.text) > NEWSPAPER_MAX_ARTICLE_LENGTH:
                logger.info("article '%s'(%s) is too long: %s",
                            article.title, article.url, len(article.text))
                continue

            record = self.model(url=article.url, title=article.title,
                                text=article.text, summary=article.summary,
                                source=source,
                                keywords=json.dumps(article.keywords),
                                authors=json.dumps(article.authors),
                                top_image_url=article.top_image,
                                all_images_urls=json.dumps(article.images))
            try:
                record.save()
                logger.info("article %s(%s) is added",
                            record.title, record.url)
            except IntegrityError, error:
                logger.exception(error)
                continue

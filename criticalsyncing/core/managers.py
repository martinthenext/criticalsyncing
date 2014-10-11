from django.db import models
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


class ArticleDownloadManager(models.Manager):
    def download_from(self, source):
        paper = newspaper.build(source.url,
                                memoize_articles=False,
                                fetch_images=False,
                                timeout=NEWSPAPER_TIMEOUT,
                                number_threads=NEWSPAPER_THREADS_COUNT,
                                language=NEWSPAPER_LANGAUGE)
        logger.debug("paper %s size: %d", source.url, paper.size())
        known = set(self.values_list("url", flat=True))
        for article in filter(lambda a: a.url not in known,
                              paper.articles[:NEWSPAPER_MAX_ARTICLES]):
            try:
                article.download()
                article.parse()
                article.nlp()
            except Exception, error:
                logger.exception(error)
                continue

            record = self.model(url=article.url, title=article.title,
                                text=article.text, summary=article.summary,
                                source=source,
                                keywords=json.dumps(article.keywords),
                                authors=json.dumps(article.authors))
            record.save()
            logger.info("article %s(%s) is added", record.title, record.url)

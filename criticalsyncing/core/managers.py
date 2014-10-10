from django.db import models
from django.conf import settings
import newspaper
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
        for article in paper.articles[:NEWSPAPER_MAX_ARTICLES]:
            if self.filter(url=article.url):  # TODO: OPTIMIZE IT!!!1111
                continue
            try:
                article.download()
                article.parse()
                article.nlp()
            except Exception, error:
                logger.exception(error)
                continue

            record = self.model(url=article.url, title=article.title,
                                text=article.title, summary=article.summary)
            record.save()

            for keyword_ in article.keywords:
                from .models import ArticleKeyword
                keyword, isnew = \
                    ArticleKeyword.objects.get_or_create(name=keyword_)
                if isnew:
                    logger.info("new keyword: %s", keyword.name)
                    keyword.save()
                record.keywords.add(keyword)

            for author_ in article.authors:
                from .models import ArticleAuthor
                author, isnew = \
                    ArticleAuthor.objects.get_or_create(name=author_)
                if isnew:
                    logger.info("new author: %s", author.name)
                    author.save()
                record.authors.add(author)

            record.save()
            logger.info("article %s(%s) is added", record.title, record.url)

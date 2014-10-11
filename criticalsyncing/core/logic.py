"""

If the article is from Western media and mentions some other country, find a source for that country
    and search for the similar article on that source
Otherwize, look at the source of the article and find an opposite source,
    and search for the similar article on that source

"""
from .models import Source, SourceTag, Article
from urlparse import urlparse
import newspaper
import logging
from sklearn.feature_extraction.text import Tfidfvectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.externals import joblib

logger = logging.getLogger(__name__)


class LogicError(RuntimeError):
    pass


def get_sources(article):
    WESTTAG, _ = SourceTag.objects.get_or_create(name="Western")
    MIDDLEEAST = ["bahrain", "cyprus", "egypt", "iran", "iraq", "jordan",
                  "kuwait", "lebanon", "oman", "palestine", "qatar"
                  "arabia", "syria", "emirates", "yemen", "israel"]

    # matching by keywords
    if set(article.keywords) & set(MIDDLEEAST):
        article.keywords.append("middle east")
    tags = SourceTag.objects\
        .filter(name__in=map(lambda x: x.title(), article.keywords))\
        .exclude(name=WESTTAG.name)
    sources = Source.objects.filter(tag__in=tags)
    if sources:
        logger.info("sources are matched by keywords: %s", sources)
        return sources

    # matching western
    domain = "{uri.netloc}".format(uri=urlparse(article.url))
    parts = -2
    if domain.endswith("co.uk"):
        parts = -3
    domain = ".".join(domain.split(".")[parts:])  # top level domain
    logger.info("domain: %s", domain)
    sources = Source.objects.filter(tag=WESTTAG, url__contains=domain)
    if sources:
        bias = sources[0].bias
        logger.info("bias: %s", bias)
        sources = Source.objects.filter(tag=WESTTAG).exclude(bias=bias)
        if sources:
            logger.info("western sources: %s", sources)
            return sources

    return Source.objects.all()


def get_article(input_url):
    try:
        article = newspaper.Article(url=input_url)
        article.download()
        article.parse()
        article.nlp()
        logger.info("keywords: %s", article.keywords)
    except Exception, error:
        logger.exception(error)
        raise LogicError("Could not parse article")
    return article


def get_url_from_sources(sources):
    return Article.objects.filter(source__in=sources)[0].url


def get_matching_url(input_url):
    article = get_article(input_url)
    sources = get_sources(article)
    return get_url_from_sources(sources)


def fetch_pickled_vectorizer():
    # This should be replaced by something which we unpickled
    return joblib.load('pickles/globaltfidf.pkl')

def return_matching_document_index(text, tf_idf_matrix):
    vectorizer =  fetch_pickled_vectorizer()
    transformed = vectorizer.transform(text)
    similarity = cosine_similarity(transformed[0:1], tf_idf_matrix)
    return similarity.index(max(similarity))



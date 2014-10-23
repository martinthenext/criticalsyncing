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
import operator
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.externals import joblib
from django.conf import settings
import os

PICKLES_DIRECTORY = os.path.join(os.getcwd(), "pickles")
if hasattr(settings, "PICKLES_DIRECTORY"):
    PICKLES_DIRECTORY = settings.PICKLES_DIRECTORY

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

    return None


def get_article(input_url):
    try:
        article = newspaper.Article(url=input_url)
        article.download()
        article.parse()
        original = article.text
        # fix https://github.com/codelucas/newspaper/issues/77
        article.text = original.encode(errors='replace')
        article.nlp()
        article.text = original
        logger.info("keywords: %s", article.keywords)
    except Exception, error:
        logger.exception(error)
        raise LogicError("Could not parse article")
    return article


def get_url_from_sources(sources):
    return Article.objects.filter(source__in=sources)[0].url


def fetch_pickled_tfidf(source=None):
    if not source:
        pickle_file = os.path.join(
            PICKLES_DIRECTORY, "tfidf_global.pkl")
    else:
        pickle_file = os.path.join(
            PICKLES_DIRECTORY, "tfidf_" + str(source.id) + ".pkl")

    # This should be replaced by something which we unpickled
    return joblib.load(pickle_file)


def get_matching_article(text, sources):
    vectorizer = joblib.load(
        os.path.join(PICKLES_DIRECTORY, "vectorizer_global.pkl"))
    transformed = vectorizer.transform([text])
    if sources is None:
        _, best_article_index = find_max_similarity(transformed)
        return list(Article.objects.all())[best_article_index]
    else:
        similarities = []
        for source in sources:
            similarity, similarity_index = \
                find_max_similarity(transformed, source)
            similarities.append([similarity, similarity_index, source.id])
        similarities = sorted(similarities, key=operator.itemgetter(0))
        _, best_index, best_source = similarities[-1]
        return list(Source.objects.get(id=best_source).article_set.all())[best_index]


def find_max_similarity(transformed, source=None):
    similarity = cosine_similarity(transformed, fetch_pickled_tfidf(source))
    similarity = similarity.flatten()
    similarity_ranked = sorted(enumerate(similarity), key=lambda x: x[1], reverse=True)
    best_match_index, best_match = filter(lambda x: x[1] != 1, similarity_ranked)[0]
    return best_match, best_match_index


def get_matching_url(input_url):
    article = get_article(input_url)
    sources = get_sources(article)
    matching_article = get_matching_article(' '.join(article.keywords), sources)
    return matching_article.url

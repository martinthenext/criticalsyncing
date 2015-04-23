import newspaper
import logging
import operator
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.externals import joblib
from sklearn.metrics.pairwise import cosine_similarity
import os
import json
from array import array
import scipy.sparse as sp
from urlparse import urlparse
from common.atomic import TmpDirectory
from .mixin import PicklesMixin

logger = logging.getLogger(__name__)


class Vectorizer(PicklesMixin):
    def __init__(self, pickles_directory, max_features, min_df, max_df):
        self.pickles_directory = pickles_directory
        logger.info("pickles directory: %s", pickles_directory)
        if max_features == 0:
            max_features = None
        logger.info("max features count: %s", max_features)
        self.max_features = max_features
        logger.info("max df: %s", max_df)
        self.max_df = max_df
        logger.info("min df: %s", min_df)
        self.min_df = min_df
        self.prefix = "current"
        self.tmp_prefix = "building"
        self.vectorizer_name = "vectorizer.pkl"
        self.urls_name = "url_{suffix}.pkl"
        self.tfidf_name = "tfidf_{suffix}.pkl"
        self.prepare_directory()

    def rebuild(self, rclient):
        texts = []
        urls = []
        sources = {}
        dst = os.path.join(self.pickles_directory, self.prefix)
        tmp = os.path.join(self.pickles_directory, self.tmp_prefix)
        with TmpDirectory(dst, tmp):
            logger.info("extrating data")
            for i, (text, url, source) in enumerate(self.extract_data(
                    rclient, rclient.scan_iter(match="http*"))):
                texts.append(text)
                urls.append(url)
                sources.setdefault(source, array('I')).append(i)
            logger.info("create global vectorizer")
            vectorizer = TfidfVectorizer(max_features=self.max_features,
                                         min_df=self.min_df,
                                         max_df=self.max_df)
            tfidf = vectorizer.fit_transform(texts)
            logger.info("features: %d", len(vectorizer.get_feature_names()))
            self.save_vectorizer(vectorizer)
            self.save_tfidf(tfidf, "global")
            self.save_urls(urls, "global")
            for source, indices in sources.iteritems():
                logger.info("create %s vectorizer", source)
                source_texts = (texts[i] for i in indices)
                source_urls = (urls[i] for i in indices)
                tfidf = vectorizer.transform(source_texts)
                self.save_tfidf(tfidf, source)
                self.save_urls(source_urls, source)

    def update(self, rclient, new):
        texts = []
        urls = self.load_urls("global")
        url_length = len(urls)
        sources = {}
        vectorizer = self.load_vectorizer()
        dst = os.path.join(self.pickles_directory, self.prefix)
        tmp = os.path.join(self.pickles_directory, self.tmp_prefix)
        with TmpDirectory(dst, tmp):
            logger.info("extrating data")
            for i, (text, url, source) in enumerate(
                    self.extract_data(rclient, new)):
                texts.append(text)
                urls.append(url)
                sources.setdefault(source, array('I')).append(i)
            logger.info("update global vectorizer")
            tfidf = vectorizer.transform(texts)
            tfidf = sp.vstack((self.load_tfidf("global"), tfidf), format='csr')
            self.save_tfidf(tfidf, "global")
            self.save_urls(urls, "global")
            for source, indices in sources.iteritems():
                logger.info("update %s vectorizer", source)
                source_texts = (texts[i] for i in indices)
                source_urls = self.load_urls(source) + \
                    [urls[i + url_length] for i in indices]
                tfidf = vectorizer.transform(source_texts)
                tfidf = sp.vstack((self.load_tfidf(source), tfidf),
                                  format='csr')
                self.save_tfidf(tfidf, source)
                self.save_urls(source_urls, source)

    def match(self, rclient, article):
        sources = self.get_sources(rclient, article)
        return self.get_matching_url(article, sources)

    def get_matching_url(self, article, sources):
        text = article["text"]
        vectorizer = self.load_vectorizer()
        transformed = vectorizer.transform([text])
        if sources is None:
            _, best_article_index = self.find_max_similarity(transformed)
            return self.load_urls("global")[best_article_index]
        else:
            similarities = []
        for source in sources:
            similarity, similarity_index = \
                self.find_max_similarity(transformed, source)
            similarities.append((similarity, similarity_index, source))
        similarities = sorted(similarities, key=operator.itemgetter(0))
        _, best_index, source = similarities[-1]
        return self.load_urls(source)[best_index]

    def find_max_similarity(self, transformed, source=None):
        similarity = cosine_similarity(
            transformed, self.load_tfidf(source or "global"))
        similarity = similarity.flatten()
        similarity_ranked = sorted(enumerate(similarity),
                                   key=lambda x: x[1], reverse=True)
        best_match_index, best_match = filter(
            lambda x: x[1] != 1, similarity_ranked)[0]
        return best_match, best_match_index

    def get_sources(self, rclient, article):
        WESTTAG = "western"
        MIDDLEEASTTAG = "middle east"
        MIDDLEEAST = ["bahrain", "cyprus", "egypt", "iran", "iraq", "jordan",
                      "kuwait", "lebanon", "oman", "palestine", "qatar"
                      "arabia", "syria", "emirates", "yemen", "israel"]
        allsources = [
          json.loads(v).items() + [("id", k)]
          for k, v in rclient.hgetall("sources").items()
        ]
        allsources = map(lambda x: dict(x), allsources)
        keywords = article.get("keywords", [])
        url = article.get("url")

        # matching by keywords
        if set(keywords) & set(MIDDLEEAST):
            keywords.append(MIDDLEEASTTAG)
        sources = filter(
            lambda x: (set(x.get("tags", [])) - set([WESTTAG])) & set(keywords),
            allsources)
        if sources:
            logger.info("sources are matched by keywords: %s", sources)
            return map(lambda x: x["id"], sources)

        # matching western
        domain = "{uri.netloc}".format(uri=urlparse(url))
        parts = -2
        if domain.endswith("co.uk"):
            parts = -3
        domain = ".".join(domain.split(".")[parts:])  # top level domain
        logger.info("domain: %s", domain)
        sources = filter(
            lambda x: set(x.get("tags", [])) & set([WESTTAG]) and
            x.get("url", "").find(domain) >= 0, allsources)
        if sources:
            bias = sources[0].get("bias")
            logger.info("bias: %s", bias)
            sources = filter(
                lambda x: (set(x.get("tags")) & set([WESTTAG])) and
                x.get("bias", bias) != bias,
                allsources)
            if sources:
                logger.info("western sources: %s", sources)
                return map(lambda x: x["id"], sources)

        return None

    def extract_data(self, rclient, urls):
        for url in urls:
            data = rclient.get(url)
            if not data:
                logger.warning("unknown article on url %s", url)
                continue
            data = json.loads(data)
            text = data.get("text")
            valid = data.get("valid")
            source_id = data.get("source_id")
            if not valid or not text:
                logger.debug("skipping invalid %s: valid: %s", url, valid)
                continue
            logger.info("rebuilding: url: %s", url)
            yield (text, url, source_id)

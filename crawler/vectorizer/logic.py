import newspaper
import logging
import operator
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.externals import joblib
import os
import json
from array import array
import scipy.sparse as sp
from common.atomic import TmpDirectory

logger = logging.getLogger(__name__)


class Vectorizer:
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
        self.create_directory(pickles_directory)

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

    def create_directory(self, directory):
        if not os.path.isdir(directory):
            logger.info("creating directory: %s", directory)
            if os.path.exists(directory):
                os.remove(directory)
            os.makedirs(directory)

    def save_vectorizer(self, vectorizer):
        filename = os.path.join(
            self.pickles_directory, self.tmp_prefix,
            self.vectorizer_name)
        logger.info("saving vectorizer: %s", filename)
        joblib.dump(vectorizer, filename)

    def save_tfidf(self, tfidf, suffix):
        filename = os.path.join(
            self.pickles_directory, self.tmp_prefix,
            self.tfidf_name.format(suffix=suffix))
        logger.info("saving tfidf: %s", filename)
        joblib.dump(tfidf, filename)

    def save_urls(self, urls, suffix):
        filename = os.path.join(
            self.pickles_directory, self.tmp_prefix,
            self.urls_name.format(suffix=suffix))
        logger.info("saving urls: %s", filename)
        joblib.dump(list(urls), filename)

    def load_vectorizer(self):
        filename = os.path.join(
            self.pickles_directory, self.prefix,
            self.vectorizer_name)
        logger.info("loading vectorizer: %s", filename)
        return joblib.load(filename)

    def load_tfidf(self, suffix):
        filename = os.path.join(
            self.pickles_directory, self.prefix,
            self.tfidf_name.format(suffix=suffix))
        logger.info("loading tfidf: %s", filename)
        return joblib.load(filename)

    def load_urls(self, suffix):
        filename = os.path.join(
            self.pickles_directory, self.prefix,
            self.urls_name.format(suffix=suffix))
        logger.info("loading urls: %s", filename)
        return joblib.load(filename)

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

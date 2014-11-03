import os
from sklearn.externals import joblib
import logging

logger = logging.getLogger(__name__)


class PicklesMixin:
    """
    required:
        self.pickles_directory
        self.tmp_prefix
        self.prefix
        self.vectorizer_name
        self.tfidf_name
        self.urls_name
    """
    def prepare_directory(self):
        if not os.path.isdir(self.pickles_directory):
            logger.info("creating directory: %s", self.pickles_directory)
            if os.path.exists(self.pickles_directory):
                os.remove(self.pickles_directory)
            os.makedirs(self.pickles_directory)

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

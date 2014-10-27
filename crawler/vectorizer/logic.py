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


class Vectorizer:
    def __init__(self, rclient, pickles_directory):
        self.pickles_directory = pickles_directory
        self.rclient = rclient
        self.prepare_directory(pickles_directory)

    def update(self, urls):
        pass

    def prepare_directory(self):
        if not os.path.isdir(self.pickles_directory):
            if os.path.exists(self.pickles_directory):
                os.remove(self.pickles_directory)
            os.makedirs(self.pickles_directory)

    def extract_data(self, urls):
        for url in urls:
            data = rclient.get(url)
            if not data:
                logger.warning("unknown article on url %s", url)
                continue
            text = data.get("text")
            valid = data.get("valid")
            if not valid or not text:
                logget.debug("skipping invalid %s: valid: %s", url, valid)
                continue
            yield (text, url)

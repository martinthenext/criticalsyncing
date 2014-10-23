from django.core.management.base import BaseCommand, CommandError
from criticalsyncing.core.models import Source, Article
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.externals import joblib
from django.conf import settings
import os

PICKLES_DIRECTORY = os.path.join(os.getcwd(), "pickles")
if hasattr(settings, "PICKLES_DIRECTORY"):
    PICKLES_DIRECTORY = settings.PICKLES_DIRECTORY


class Command(BaseCommand):
    args = '<Source Name> | all'

    def prepare_directory(self):
        if not os.path.isdir(PICKLES_DIRECTORY):
            if os.path.exists(PICKLES_DIRECTORY):
                os.remove(PICKLES_DIRECTORY)
            os.makedirs(PICKLES_DIRECTORY)

    def handle(self, *args, **options):
        self.prepare_directory()
        texts = [a.get_text_to_vectorize() for a in Article.objects.all()]
        vectorizer = TfidfVectorizer()
        text_fit = vectorizer.fit_transform(texts)
        joblib.dump(vectorizer,
                    os.path.join(PICKLES_DIRECTORY, 'vectorizer_global.pkl'))
        joblib.dump(text_fit,
                    os.path.join(PICKLES_DIRECTORY, 'tfidf_global.pkl'))
        for s in Source.objects.all():
            texts = [a.get_text_to_vectorize() for a in s.article_set.all()]
            if len(texts) == 0:
                continue
            text_fit = vectorizer.transform(texts)
            pickle_name = os.path.join(PICKLES_DIRECTORY,
                                       "tfidf_" + str(s.id) + ".pkl")
            joblib.dump(text_fit, pickle_name)

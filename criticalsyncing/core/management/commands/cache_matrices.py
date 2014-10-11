from django.core.management.base import BaseCommand, CommandError
from criticalsyncing.core.models import Source, Article
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.externals import joblib


class Command(BaseCommand):
    args = '<Source Name> | all'

    def handle(self, *args, **options):
        texts = [a.get_text_to_vectorize() for a in Article.objects.all()]
        vectorizer = TfidfVectorizer()
        text_fit = vectorizer.fit_transform(texts)
        joblib.dump(vectorizer,'pickles/vectorizer_global.pkl')
        joblib.dump(text_fit, 'pickles/tfidf_global.pkl')
        for s in Source.objects.all():
            texts = [a.get_text_to_vectorize() for a in s.article_set.all()]
            if len(texts) == 0:
                continue
            text_fit = vectorizer.transform(texts)
            pickle_name = "pickles/tfidf_" + str(s.id) + ".pkl"
            joblib.dump(text_fit, pickle_name)

        #name = args[0] if args else "all"
        #if name == 'all':
        #    sources = Source.objects.all()
        #else:
        #    sources = Source.objects.filter(name=name)
        #for source in sources:
        #    Article.objects.download_from(source)


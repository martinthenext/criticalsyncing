from models import Article, Source


if __name__ == "__main__":
    for s in Source.objects.all():
        Article.objects.download_from(s)

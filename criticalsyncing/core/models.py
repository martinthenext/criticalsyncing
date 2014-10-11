from django.db import models
from .managers import ArticleDownloadManager


class SourceTag(models.Model):
    name = models.CharField(max_length=50,
                            unique=True,
                            blank=False)


class Source(models.Model):
    name = models.CharField(max_length=200,
                            unique=True,
                            blank=False)
    url = models.URLField(max_length=200,
                          unique=True,
                          blank=False)
    tag = models.ManyToManyField(SourceTag)


class Article(models.Model):
    url = models.URLField(max_length=200,
                          blank=False,
                          unique=True)
    title = models.CharField(max_length=200,
                             blank=False)
    text = models.CharField(max_length=100000,
                            blank=False)
    summary = models.CharField(max_length=5000)
    authors = models.CharField(max_length=400)
    keywords = models.CharField(max_length=400)
    source = models.ForeignKey(Source, blank=False)

    objects = ArticleDownloadManager()

from django.db import models
from .managers import ArticleDownloadManager


class SourceTag(models.Model):
    name = models.CharField(max_length=50,
                            unique=True,
                            blank=False)
    def __unicode__(self):
        return self.name


class Source(models.Model):
    POLITICAL_BIAS = (
        ('L', 'Left wing'),
        ('R', 'Right wing'),
    )

    name = models.CharField(max_length=200,
                            unique=True,
                            blank=False)
    url = models.URLField(max_length=200,
                          unique=True,
                          blank=False)
    tag = models.ManyToManyField(SourceTag, blank=True)
    bias = models.CharField(max_length=1, choices=POLITICAL_BIAS, blank=True, null=True)
    haters = models.ManyToManyField("self", blank=True) # symmetrical by default
    def __unicode__(self):
        return self.name


class Article(models.Model):
    url = models.URLField(max_length=200,
                          blank=False,
                          unique=True)
    title = models.CharField(max_length=200,
                             blank=False)
    text = models.TextField(blank=False)
    summary = models.TextField(blank=True, null=True)
    authors = models.CharField(max_length=400, blank=True, null=True)
    keywords = models.CharField(max_length=400, blank=True, null=True)
    source = models.ForeignKey(Source, blank=True)
    category = models.CharField(max_length=100, blank=True, null=True)

    objects = ArticleDownloadManager()
    def __unicode__(self):
        return self.title


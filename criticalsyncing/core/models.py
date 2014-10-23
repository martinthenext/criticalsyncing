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
    url = models.URLField(max_length=2048,
                          unique=True,
                          blank=False)
    tag = models.ManyToManyField(SourceTag, blank=True)
    bias = models.CharField(max_length=1,
                            choices=POLITICAL_BIAS,
                            blank=True, null=True)
    haters = models.ManyToManyField("self", blank=True)  # symmetrical by default

    def __unicode__(self):
        return self.name


class Article(models.Model):
    url = models.URLField(max_length=2048,
                          blank=False,
                          unique=True)
    title = models.CharField(max_length=1024,
                             blank=False)
    text = models.TextField(blank=False)
    summary = models.TextField(blank=True, null=True)
    authors = models.TextField(blank=True, null=True)
    keywords = models.CharField(max_length=1024, blank=True, null=True)
    source = models.ForeignKey(Source, blank=True)
    category = models.TextField(blank=True, null=True)
    top_image_url = models.URLField(max_length=2048, null=True, default=None)
    all_images_urls = models.TextField(blank=True, null=True, default=None)

    objects = ArticleDownloadManager()

    def __unicode__(self):
        return self.title

    def get_text_to_vectorize(self):
        return self.text


class Cache(models.Model):
    input_url = models.URLField(max_length=2048, unique=True)
    output_url = models.URLField(max_length=2048)

    def __unicode__(self):
        return 'Cached for %s' % self.input_url

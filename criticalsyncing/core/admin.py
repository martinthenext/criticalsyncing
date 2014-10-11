from django.contrib import admin
from .models import SourceTag, Source, Article, Cache

admin.site.register(SourceTag)
admin.site.register(Source)
admin.site.register(Article)
admin.site.register(Cache)

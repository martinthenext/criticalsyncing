from django.contrib import admin
from .models import SourceTag, Source, Article

admin.site.register(SourceTag)
admin.site.register(Source)
admin.site.register(Article)

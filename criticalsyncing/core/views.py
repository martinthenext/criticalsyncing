from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View


class Index(View):
    template_name = "index.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        pass

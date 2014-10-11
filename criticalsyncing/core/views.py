from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View
import json


class Index(View):
    template_name = "index.html"

    def get(self, request):
        return render(request, self.template_name)

    def error(self, request, error):
        context = {"error": error}
        if request.is_ajax():
            return HttpResponse(json.dumps(context),
                                content_type="application/json")
        else:
            return render(request, self.template_name, context)

    def redirect(self, request, url):
        if request.is_ajax():
            return HttpResponse(json.dumps({"url": url}),
                                content_type="application/json")
        else:
            return redirect(url)

    def post(self, request):
        url = request.POST.get("url")
        if not url:
            return self.error(request, "have no url")
        # get new url
        return self.redirect(request, url)

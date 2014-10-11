from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View
import json
from logic import get_matching_url
import logging

logger = logging.getLogger(__name__)


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
        input_url = request.POST.get("url")
        if not input_url:
            return self.error(request, "have no url")
        logger.info("input url: %s", input_url)
        try:
            output_url = get_matching_url(input_url)
            logger.info("output url: %s", output_url)
            return self.redirect(request, output_url)
        except Exception, error:
            logger.exception(error)
            return self.error(request, str(error))

from django.shortcuts import render
from django.views.generic import View

# Create your views here.
class post_list(View):
    def get(self, request):
        context_dict = {}
        return render(request, "blog/base.html", context_dict)

class about(View):
    def get(self, request):
        context_dict = {}
        return render(request, "blog/about.html", context_dict)
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from . import models
from . import forms
from pathlib import Path


app_name = Path(__file__).parent.name

# Create your views here.
# class post_list(View):
#     def get(self, request):
#         context_dict = {}
#         return render(request, APP_NAME/"base.html", context_dict)

# class about(View):
#     def get(self, request):
#         context_dict = {}
#         return render(request, APP_NAME/"about.html", context_dict)


class About(TemplateView):
    # print(f"dbg:{(APP_NAME_POSIX / "about.html").as_posix()}")
    # template_name = (APP_NAME_POSIX / "about.html").as_posix()
    template_name = (Path(app_name)/"about.html").as_posix()


class PostList(ListView):
    model = models.Post

    def get_queryset(self):
        return PostList.model.objects.filter(published_date__lte=timezone.now()).order_by("-published_date")


class PostDetail(DetailView):
    model = models.Post


class PostCreate(CreateView, LoginRequiredMixin):
    login_url = "/login/" #page to send users to for logging in
    redirect_field_name = (Path(app_name) / "post_detail.html").as_posix() #redirect to this page after loggin in

    form_class = forms.PostForm

    model = models.Post


class PostUpdate(UpdateView, LoginRequiredMixin):
    login_url = "/login/" #page to send users to for logging in
    redirect_field_name = (Path(app_name) / "post_detail.html").as_posix() #redirect to this page after loggin in

    form_class = forms.PostForm

    model = models.Post


class PostDelete(DeleteView, LoginRequiredMixin):
    model = models.Post

    success_url = reverse_lazy("post_list") # page to send users to after deleting a record


class DraftList(ListView, LoginRequiredMixin):
    login_url = "/login/"  # page to send users to for logging in
    redirect_field_name = (Path(app_name) / "post_list.html").as_posix()  # redirect to this page after logging in

    model = models.Post

    def get_queryset(self):
        return DraftList.model.objects.filter(published_date__isnull=True).order_by("created_date")


@login_required
def post_publish(request, pk):
    post = get_object_or_404(models.Post, pk=pk)
    post.publish()
    return redirect("post_detail", pk=pk)


@login_required
def add_comment_to_post(request, pk):
    post = get_object_or_404(models.Post, pk=pk)
    if request.method == "POST":
        form = forms.CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect("post_detail", pk=post.pk)
    else:
        form = forms.CommentForm()
    return render(request, (Path(app_name) / "comment_form.html").as_posix(), {"form":form})


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(models.Comment, pk=pk)
    comment.approve()
    return redirect("post_detail", pk=comment.post.pk)


@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(models.Comment, pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect("post_detail", pk=post_pk)



from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.conf import settings

from . import models
from . import forms
from pathlib import Path


app_name = Path(__file__).parent.name

class About(TemplateView):
    template_name = (Path(app_name)/"about.html").as_posix()


class PostList(ListView):
    model = models.Post

    def get_queryset(self):
        # return PostList.model.objects.filter(published_date__lte=timezone.now()).order_by("-published_date")
        # return PostList.model.objects.order_by("-published_date")
        return PostList.model.objects.filter(published_date__isnull=False).order_by("-published_date")


class PostDetail(DetailView):
    model = models.Post


class PostCreate(LoginRequiredMixin, CreateView):
    # login_url = "/accounts/login/?next=post/create" #page to send users to for logging in
    # redirect_field_name = (Path(app_name) / "post_detail.html").as_posix() #redirect to this page after logging in
    form_class = forms.PostForm
    model = models.Post

    def get_login_url(self):
        return f"""{reverse_lazy("login")}?next={reverse_lazy("blog:post_create")}"""



class PostUpdate(LoginRequiredMixin, UpdateView):
    # login_url = "/login/" #page to send users to for logging in
    login_url = "/accounts/login/?next=post/<pk>/update" #need to get the post.pk and add it here properly
    redirect_field_name = (Path(app_name) / "post_detail.html").as_posix() #redirect to this page after logging in

    form_class = forms.PostForm

    model = models.Post


class PostDelete(LoginRequiredMixin, DeleteView):
    model = models.Post

    success_url = reverse_lazy("post_list") # page to send users to after deleting a record


class DraftList(LoginRequiredMixin, ListView):
    login_url = "/login/"  # page to send users to for logging in
    # redirect_field_name = (Path(app_name) / "post_list.html").as_posix()  # redirect to this page after logging in

    template_name = (Path(app_name) / "post_draft_list.html").as_posix()

    model = models.Post

    def get_queryset(self):
        return DraftList.model.objects.filter(published_date__isnull=True).order_by("-created_date")


@login_required
def post_publish(request, pk):
    post = get_object_or_404(models.Post, pk=pk)
    post.publish()
    return redirect("blog:post_list")


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



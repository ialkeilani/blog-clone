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
    queryset = models.Post.objects.filter(published_date__isnull=False).order_by("-published_date")
    # queryset = models.Post.objects.filter(published_date__isnull=False)

    # def get_queryset(self):
    #     # return PostList.model.objects.order_by("-published_date")
    #     return models.Post.objects.filter(published_date__isnull=False).order_by("-published_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["app_name"] = app_name
        return context


class PostDetail(DetailView):
    model = models.Post


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context["post_comments"] = post.get_comments_ordered("approved_comment", "created_date")
        return context



class PostCreate(LoginRequiredMixin, CreateView):
    form_class = forms.PostForm
    model = models.Post

    # current url that unauthenticated user was trying to access is by default passed to the get url "next" parameter as the user gets redircted to the login url. so the code below is not needed as "LoginRequiredMixin" already does it for us
    # def get_login_url(self):
    #     return f"""{reverse_lazy("login")}?next={reverse_lazy("blog:post_create")}"""

    def get_success_url(self):
        print("dbg:self.object.pk:", self.object.pk)
        return reverse_lazy(f"{app_name}:post_detail", kwargs={"pk": self.object.pk})




class PostUpdate(LoginRequiredMixin, UpdateView):
    form_class = forms.PostForm
    model = models.Post

    # current url that unauthenticated user was trying to access is by default passed to the get url "next" parameter as the user gets redircted to the login url. so the code below is not needed as "LoginRequiredMixin" already does it for us
    # def get_login_url(self):
    #     return f"""{reverse_lazy("login")}?next={reverse_lazy("blog:post_update", kwargs={"pk": self.kwargs["pk"]})}"""


class PostDelete(LoginRequiredMixin, DeleteView):
    model = models.Post
    success_url = reverse_lazy(f"{app_name}:post_list") # page to send users to after deleting a record


class DraftList(LoginRequiredMixin, ListView):
    template_name = (Path(app_name) / "post_draft_list.html").as_posix()
    # model = models.Post

    def get_queryset(self):
        return models.Post.objects.filter(published_date__isnull=True).order_by("-created_date")


@login_required
def post_publish(request, pk):
    post = get_object_or_404(models.Post, pk=pk)
    post.publish()
    return redirect(f"{app_name}:post_list")


# @login_required
# def add_comment_to_post(request, post_pk):
#     post = get_object_or_404(models.Post, pk=post_pk)
#     if request.method == "POST":
#         form = forms.CommentForm(request.POST)
#         if form.is_valid():
#             comment = form.save(commit=False)
#             comment.post = post
#             comment.save()
#             return redirect(f"{app_name}:post_detail", pk=post.pk)
#     else:
#         form = forms.CommentForm()
#     return render(request, (Path(app_name) / "comment_form.html").as_posix(), {"form":form})


class CommentCreate(LoginRequiredMixin, CreateView):
    form_class = forms.CommentForm
    model = models.Comment


    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.post = get_object_or_404(models.Post, pk=self.kwargs["post_pk"])
        comment.save()
        return super().form_valid(form)


    def get_success_url(self):
        return reverse_lazy(f"{app_name}:post_detail", kwargs={"pk": self.kwargs["post_pk"]})




@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(models.Comment, pk=pk)
    comment.approve()
    return redirect(f"{app_name}:post_detail", pk=comment.post.pk)


@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(models.Comment, pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect(f"{app_name}:post_detail", pk=post_pk)



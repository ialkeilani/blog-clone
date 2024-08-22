from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, edit
from django.utils import timezone
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.conf import settings

from django.contrib import auth

from . import models
from . import forms
from pathlib import Path


app_name = Path(__file__).parent.name

class Registration(UserPassesTestMixin, CreateView):
    template_name = "registration/registration.html"
    form_class = forms.CustomUserCreationForm
    success_url = reverse_lazy(f"{app_name}:post_list")


    def test_func(self):
        return not auth.get_user(self.request).is_authenticated #only available if no user is currently logged in

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save()
        login(self.request, self.object)
        return HttpResponseRedirect(self.get_success_url())

class About(TemplateView):
    template_name = (Path(app_name)/"about.html").as_posix()


class Message(TemplateView):
    template_name = (Path(app_name)/"message.html").as_posix()


class PostList(ListView):
    # model = models.Post
    queryset = models.Post.objects.filter(published_date__isnull=False).order_by("-published_date")
    extra_context = {"app_name": app_name}

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["app_name"] = app_name
    #     return context


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
        return reverse_lazy(f"{app_name}:post_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        post = form.save(commit=False) #get submitted form data but don't save yet
        post.author = auth.get_user(self.request) #set username
        post.save()
        self.object = post
        return super(edit.ModelFormMixin, self).form_valid(form)

    # def get(self, request, *args, **kwargs):
    #     # user = auth.get_user(request)
    #     # get_object_or_404(auth.User, username=request.user.username)
    #     # print("dbg:user.username", user.username, user.pk)
    #     # print("dbg:dir(request.user):", request.user.username)
    #     # print("dbg:dir(self):", dir(self.request))
    #     return super().get(request, *args, **kwargs)




class PostUpdate(LoginRequiredMixin, UpdateView):
    form_class = forms.PostForm
    model = models.Post

    def get_success_url(self):
        return reverse_lazy(f"{app_name}:post_detail", kwargs={"pk": self.object.pk})

    # current url that unauthenticated user was trying to access is by default passed to the get url "next" parameter as the user gets redircted to the login url. so the code below is not needed as "LoginRequiredMixin" already does it for us
    # def get_login_url(self):
    #     return f"""{reverse_lazy("login")}?next={reverse_lazy("blog:post_update", kwargs={"pk": self.kwargs["pk"]})}"""


class PostDelete(LoginRequiredMixin, DeleteView):
    model = models.Post
    success_url = reverse_lazy(f"{app_name}:post_list") # page to send users to after deleting a record

    # def get_queryset(self):
    #     if self.request.user.is_superuser:
    #         return models.Post.objects.all()
    #     else:
    #         return models.Post.objects.filter(author=self.request.user.pk)

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser or self.get_queryset().get(pk=kwargs["pk"]).author.pk == request.user.pk:
            # continue normally
            self.object = self.get_object()
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)
        else:
            # communicate error
            return redirect(f"{app_name}:message", msg="!!! ERR: UNAUTHORIZED ACTION !!!")


class DraftList(LoginRequiredMixin, ListView):
    template_name = (Path(app_name) / "post_draft_list.html").as_posix()
    # model = models.Post

    def get_queryset(self):
        if self.request.user.is_superuser:
            return models.Post.objects.filter(published_date__isnull=True).order_by("-created_date")
        else:
            return models.Post.objects.filter(published_date__isnull=True, author=self.request.user.pk).order_by("-created_date")


@login_required
def post_publish(request, pk):
    post = get_object_or_404(models.Post, pk=pk)
    print("dbg:", post.author.pk, request.user.pk, request.user.is_superuser)
    if post.author.pk == request.user.pk or request.user.is_superuser:
        post.publish()
        redirect_view = "post_list"
        context = {}
        return redirect(f"{app_name}:{redirect_view}", **context)
    else:
        # redirect_view = "message"
        # context = {"msg": "!!! ERR: UNAUTHORIZED ACTION !!!"}
    # return redirect(f"{app_name}:{redirect_view}", **context)
        return redirect(f"{app_name}:forbidden")


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


class CommentCreate(UserPassesTestMixin, LoginRequiredMixin, CreateView):
    form_class = forms.CommentForm
    model = models.Comment

    def test_func(self):
        post = models.Post.objects.get(pk=self.kwargs["post_pk"])
        current_user = auth.get_user(self.request)
        return post.published_date or post.author == current_user or current_user.is_superuser #comments can be added only to published posts or only if commentator is the post author, or he is superusuer


    def form_valid(self, form):
        # comment = form.save(commit=False)
        # comment.post = get_object_or_404(models.Post, pk=self.kwargs["post_pk"])
        # comment.save()
        # return super().form_valid(form)

        comment = form.save(commit=False)  # get submitted form data but don't save yet
        comment.post = get_object_or_404(models.Post, pk=self.kwargs["post_pk"])
        comment.author = auth.get_user(self.request)
        comment.save()
        self.object = comment
        return super(edit.ModelFormMixin, self).form_valid(form)


    def get_success_url(self):
        return reverse_lazy(f"{app_name}:post_detail", kwargs={"pk": self.kwargs["post_pk"]})




@user_passes_test(lambda u: u.is_superuser, login_url=reverse_lazy("admin:login"))
def comment_approve(request, pk):
    comment = get_object_or_404(models.Comment, pk=pk)
    comment.approve()
    return redirect(f"{app_name}:post_detail", pk=comment.post.pk)


@user_passes_test(lambda u: u.is_superuser, login_url=reverse_lazy(f"{app_name}:forbidden"))
def comment_remove(request, pk):
    comment = get_object_or_404(models.Comment, pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect(f"{app_name}:post_detail", pk=post_pk)


def forbidden(request):
    return HttpResponseForbidden("You don't have permission to access this page.")



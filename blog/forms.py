from django import forms

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Post, Comment


class PostForm(forms.ModelForm):
    author = forms.ModelChoiceField(queryset=User.objects.all(), required=False)
    class Meta():
        model = Post
        fields = ('author', 'title', 'text')
        # fields = ('title', 'text') #author and published_date will be set by the views


class CommentForm(forms.ModelForm):
    class Meta():
        model = Comment
        # fields = ('author' , 'text')
        fields = ('text',)


# class UserForm(forms.ModelForm):
#     # password = forms.CharField(widget=forms.PasswordInput())
#     class Meta():
#         model = User
#         fields = "__all__"
#         # fields = ('username', 'password')


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].help_text = 'Optional'
        self.fields['first_name'].help_text = 'Optional'
        self.fields['last_name'].help_text = 'Optional'
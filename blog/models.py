from django.db import models
from django.utils import timezone
# from django.core.urlrsolvers import reverse
from django.urls import reverse

# Create your models here.
class Post(models.Model):
    author = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    title = models.CharField(max_length=264)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    # class Meta:
    #     ordering = ["-published_date"]

    def publish(self):
        self.published_date = timezone.now()
        self.save()


    def get_comments_ordered(self, *order_by_clause):
        clause = order_by_clause or ("-created_date",)
        return self.comments.order_by(*clause)


    def get_approved_comments_count(self):
        return self.comments.filter(approved_comment=True).count()


    # def get_absolute_url(self):
    #     return reverse(f"{self.app_label}:post_detail", kwargs={"pk": self.pk})



    def __str__(self):
        return f"{self.pk} -> {self.title} by {self.author.username} on ({self.created_date})"


class Comment(models.Model):
    post = models.ForeignKey("Post", related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    approved_comment = models.BooleanField(default=False)

    def approve(self):
        self.approved_comment = True
        self.save()

    # def get_absolute_url(self):
    #     return reverse("blog:post_detail", kwargs={"pk": self.post.pk})

    def __str__(self):
        return f"{self.pk}/{self.post.pk} -> by {self.author.username} on ({self.created_date})"

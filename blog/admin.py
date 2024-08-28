from django.contrib import admin

from django.conf import settings
# from blog_clone import settings

from . import models

# Register your models here.
# admin.site.register(models.Post)
# admin.site.register(models.Comment)


@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    # fields = [] # fields and their order when a single record is viewed
    readonly_fields = ('pk',)
    pass


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    readonly_fields = ('pk',)
    fields = ["pk", "post", "author", "created_date", "approved_comment", "text",] # fields and their order when a single record is viewed
    # search_fields = ["pk", "post", "author", "created_date", "approved_comment", "text",]
    search_fields = ["pk", "post__title", "post__text", "author__username", "created_date", "approved_comment", "text",]
    list_filter = ["id", "post__id", "author__username", "created_date", "approved_comment",]
    list_display = ["id", "post", "author", "created_date", "approved_comment"] # grid view of entire table
    list_editable = ["post", "author", "created_date", "approved_comment"]


admin.site.site_header = f"{settings.BASE_DIR.name.replace('_', ' ').title()} administration"


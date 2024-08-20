from django.contrib import admin
from . import models

# Register your models here.
# admin.site.register(models.Post)
# admin.site.register(models.Comment)


@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    readonly_fields = ('pk',)

@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    readonly_fields = ('pk',)


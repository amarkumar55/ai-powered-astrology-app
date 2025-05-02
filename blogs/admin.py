from django.contrib import admin
from .models import Blog

# Register your models here.


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
  
    list_display=('id','title','slug','feature_img','is_published','publish_by','published_at','created_at','updated_at')
    list_filter=('title','slug','is_published','publish_by','published_at','created_at','updated_at')
    search_fields=('title','slug','is_published','publish_by','published_at','created_at','updated_at')
    
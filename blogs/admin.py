from django.contrib import admin
from .models import Blog

# Register your models here.


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'publish_by', 'is_published', 'published_at', 'created_at', 'updated_at')
    list_filter = ('is_published', 'published_at', 'created_at')
    search_fields = ('title', 'description', 'publish_by__email', 'publish_by__username')
    readonly_fields = ('slug', 'created_at', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-published_at', '-created_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'feature_img')
        }),
        ('Publication', {
            'fields': ('is_published', 'published_at')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
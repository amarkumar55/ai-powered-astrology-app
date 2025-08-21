from rest_framework import serializers
from blogs.models import BlogCategory, BlogPost

class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ['id', 'name', 'slug', 'description']

class BlogPostSerializer(serializers.ModelSerializer):
    category = BlogCategorySerializer(read_only=True)
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'category', 'author_name', 'excerpt', 'featured_image',
            'status', 'meta_title', 'meta_description', 'tags', 'views', 'published_at', 'created_at', 'updated_at'
        ] 
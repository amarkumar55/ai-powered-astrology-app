from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from home.models import TimeStampMixin

# Create your models here.

class SystemMetrics(TimeStampMixin):
    timestamp = models.DateTimeField(auto_now_add=True)
    cpu_usage = models.FloatField(default=0)
    memory_usage = models.FloatField(default=0)
    api_calls = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    
    class Meta:
        app_label = 'core'
        verbose_name = 'System Metric'
        verbose_name_plural = 'System Metrics'
        ordering = ['-timestamp']



class SiteSettings(TimeStampMixin):
    site_name = models.CharField(max_length=255)
    site_description = models.TextField(blank=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    social_facebook = models.URLField(blank=True)
    social_twitter = models.URLField(blank=True)
    social_instagram = models.URLField(blank=True)
    social_youtube = models.URLField(blank=True)
    maintenance_mode = models.BooleanField(default=False)

    def __str__(self):
        return self.site_name
    
    class Meta:
        app_label = 'core'
    

class AppLog(TimeStampMixin):
    LEVEL_CHOICES = [
        ('ERROR', 'Error'),
        ('WARNING', 'Warning'),
        ('INFO', 'Info'),
        ('DEBUG', 'Debug'),
    ]

    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    message = models.TextField()
    traceback = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.level} @ {self.timestamp}: {self.message[:50]}"

    class Meta:
        app_label = 'core'
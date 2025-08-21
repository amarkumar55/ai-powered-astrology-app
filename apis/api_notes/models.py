from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from home.models import TimeStampMixin
# Create your models here.

class Note(TimeStampMixin):
    NOTE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('live_audio', 'Live Audio'),
        ('uploaded_audio', 'Uploaded Audio'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content = models.TextField(blank=True)
    tag = models.CharField(max_length=50, blank=True, null=True)  
    public = models.BooleanField(default=False)  # New field
    type = models.CharField(max_length=20, choices=NOTE_TYPE_CHOICES, default='text')
    views = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.title
    
    class Meta:
        app_label = 'smartnotes'
    
    
    
class NoteLike(TimeStampMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='likes')
    
    class Meta:
        app_label = 'smartnotes'
        unique_together = ('user', 'note')  # Prevent double-like

class NoteComment(TimeStampMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    class Meta:
        app_label = 'smartnotes'
        unique_together = ('user', 'note')  # Prevent double-like



class NoteChatLog(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='chat_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_message = models.TextField()
    ai_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'smartnotes'
        ordering = ['created_at']
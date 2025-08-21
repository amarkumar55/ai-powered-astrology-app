from rest_framework import serializers
from .models import Note, NoteComment,NoteChatLog

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'title', 'slug', 'content', 'type', 'tag', 'public', 'created_at']
        read_only_fields = ['id', 'created_at']  # ✅ Remove 'slug' from here

    is_shareable = serializers.SerializerMethodField()

    def get_is_shareable(self, obj):
        return obj.public  # Only public notes can be shared
    
    def create(self, validated_data):
        # This will allow slug to be passed in validated_data
        return super().create(validated_data)
        

class NoteCommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_avatar = serializers.SerializerMethodField()

    class Meta:
        model = NoteComment
        fields = ['user', 'note', 'content', 'created_at']
        read_only_fields = ['user', 'note', 'created_at']

    def get_author_avatar(self, obj):
        # If your user model has avatar/profile image
        if hasattr(obj.author, 'avatar') and obj.author.avatar:
            return obj.author.avatar.url
        return None
    
class NoteSummarySerializer(serializers.Serializer):
    title = serializers.CharField()
    summary = serializers.CharField()


class NoteChatSerializer(serializers.Serializer):
    user_message = serializers.CharField()
    ai_response = serializers.CharField(read_only=True)



class NoteChatLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteChatLog
        fields = ['id', 'user_message', 'ai_response', 'created_at']
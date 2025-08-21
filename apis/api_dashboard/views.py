from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from .serializers import UserProfileSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from authentication.models import Follow
from apis.api_notes.models import Note
from apis.api_notes.serializers import NoteSerializer
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from rest_framework.authentication import TokenAuthentication


User = get_user_model()

class UserProfileListPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 100

class UserProfileListView(generics.ListAPIView):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = UserProfileListPagination

class UserProfileDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = 'id'
    permission_classes = [permissions.AllowAny] 



class FeedPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 50


class FeedView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    pagination_class = FeedPagination

    def get(self, request):
        user = request.user

        # Get list of users this user follows
        following_users = Follow.objects.filter(follower=user).values_list('following', flat=True)

        # Base queryset: public notes from users the current user follows
        notes = Note.objects.filter(user__in=following_users, is_public=True)

        # Optional filters
        tag = request.query_params.get('tag')
        search = request.query_params.get('search')

        if tag:
            notes = notes.filter(tags__icontains=tag)  # assuming tags is a CharField or JSON field
        if search:
            notes = notes.filter(
                Q(title__icontains=search) | Q(summary__icontains=search)
            )

        # Sort by newest first
        notes = notes.order_by('-created_at')

        # Pagination
        paginator = self.pagination_class()
        paginated_notes = paginator.paginate_queryset(notes, request)
        serializer = NoteSerializer(paginated_notes, many=True)

        return paginator.get_paginated_response(serializer.data)


class TrendingPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 50

class TrendingNotesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        tags_param = request.query_params.get('tags')  # comma-separated tags
        period_param = request.query_params.get('period')  # e.g., '7d', '30d'

        # Base queryset: only public notes
        notes = Note.objects.filter(public=True).annotate(
            comment_count=Count('comments')  # Assuming Note has related_name='comments'
        )

        # Filter by tags if provided
        if tags_param:
            tags_list = [tag.strip() for tag in tags_param.split(',')]
            tag_q = Q()
            for tag in tags_list:
                # For ManyToManyField: tag_q |= Q(tags__name__icontains=tag)
                tag_q |= Q(tags__icontains=tag)
            notes = notes.filter(tag_q)

        # Filter by period
        if period_param:
            try:
                num = int(period_param[:-1])
                unit = period_param[-1]
                if unit == 'd':
                    since = timezone.now() - timedelta(days=num)
                    notes = notes.filter(created_at__gte=since)
                # Could add weeks/months if needed
            except Exception:
                pass  # invalid period ignored

        # Sort by most commented first, then most views
        notes = notes.order_by('-comment_count', '-views')

        # Paginate
        paginator = TrendingPagination()
        paginated_notes = paginator.paginate_queryset(notes, request)
        serialized = NoteSerializer(paginated_notes, many=True)

        return paginator.get_paginated_response(serialized.data)
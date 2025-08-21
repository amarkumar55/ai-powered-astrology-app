from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from django_ratelimit.decorators import ratelimit
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from django.utils.dateparse import parse_date
from django.utils.decorators import method_decorator
from django.utils.text import slugify
import traceback
from .models import Note, NoteLike, NoteComment,NoteChatLog
from .serializers import NoteSerializer,NoteCommentSerializer,NoteSummarySerializer, NoteChatLogSerializer
from .permissions import IsOwnerOrReadOnly
from .note_processor import process_audio_and_generate_note,ask_ai_with_note,  summarize_chunks, process_image_and_generate_note, summarize_text  # ✅ Add image processor
from rest_framework.generics import ListAPIView
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound
class NoteListPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 100


@method_decorator(ratelimit(key='ip', rate='5/m', block=True), name='dispatch')
class NoteListCreate(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]
    authentication_classes = [TokenAuthentication]
    pagination_class = NoteListPagination

    def get(self, request):
        user = request.user
        notes = Note.objects.filter(user=user)

        # Filters
        title = request.query_params.get('title')
        note_type = request.query_params.get('type')
        created_after = request.query_params.get('created_after')
        created_before = request.query_params.get('created_before')
        sort_by = request.query_params.get('sort_by', '-created_at')

        if title:
            notes = notes.filter(title__icontains=title)
        if note_type:
            notes = notes.filter(type=note_type)
        if created_after:
            notes = notes.filter(created_at__gte=parse_date(created_after))
        if created_before:
            notes = notes.filter(created_at__lte=parse_date(created_before))

        valid_sort_fields = ['created_at', '-created_at', 'title', '-title']
        if sort_by not in valid_sort_fields:
            sort_by = '-created_at'
        notes = notes.order_by(sort_by)

        paginator = self.pagination_class()
        paginated_notes = paginator.paginate_queryset(notes, request)
        serialized = NoteSerializer(paginated_notes, many=True)
        return paginator.get_paginated_response(serialized.data)

    def post(self, request):
        note_type = request.data.get('type', 'text')
        audio = request.data.get('audio')
        image = request.data.get('image')
        title = request.data.get('title', '').strip()
        tag = request.data.get('tag', '')
        public = request.data.get('public', False)

        # ✅ Only one type of input allowed at a time
        provided_inputs = sum(bool(x) for x in [title, audio, image])
        if provided_inputs != 1:
            return Response({"error": "Provide only one of: text, audio, or image."}, status=400)

        try:
            # ---- TEXT NOTE ----
            if note_type == 'text' and title:
                slug = slugify(title) or 'note'
                base_slug = slug
                counter = 1
                while Note.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                data = request.data.copy()
                data['slug'] = slug
                serializer = NoteSerializer(data=data)
                if serializer.is_valid():
                    serializer.save(user=request.user)
                    return Response(serializer.data, status=201)
                return Response(serializer.errors, status=400)

            # ---- AUDIO NOTE ----
            elif note_type in ['live_audio', 'uploaded_audio'] and audio:
                note_data = process_audio_and_generate_note(audio, "hi")
                slug = slugify(note_data["title"]) or 'note'
                base_slug = slug
                counter = 1
            
                while Note.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                note = Note.objects.create(
                    user=request.user,
                    slug=slug,
                    title=note_data["title"],
                    content=note_data["summary"],
                    type=note_type,
                    tag=tag,
                    public=public
                )
                return Response(NoteSerializer(note).data, status=201)

            # ---- IMAGE NOTE ----
            elif note_type == 'image' and image:
                note_data = process_image_and_generate_note(image)
                slug = slugify(note_data["title"]) or 'note'
                base_slug = slug
                counter = 1
                while Note.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                note = Note.objects.create(
                    user=request.user,
                    slug=slug,
                    title=note_data["title"],
                    content=note_data["summary"],
                    type='image',
                    tag=tag,
                    public=public
                )
                return Response(NoteSerializer(note).data, status=201)

            else:
                return Response({"error": "Invalid note type or missing file."}, status=400)

        except Exception as e:
            print("Processing failed:", e)
            print(traceback.format_exc())
            return Response({"error": "Note processing failed."}, status=500)


class NoteDetail(RetrieveUpdateDestroyAPIView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    authentication_classes = [TokenAuthentication]
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        note = self.get_object()
        note.views = note.views + 1
        note.save(update_fields=['views'])
        serializer = self.get_serializer(note)
        return Response(serializer.data)




class NoteLikeToggle(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        note = Note.objects.get(slug=slug)
        like, created = NoteLike.objects.get_or_create(user=request.user, note=note)
        if not created:
            like.delete()  # Toggle unlike
            return Response({"liked": False})
        return Response({"liked": True})
    

class NoteCommentCreate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        note = Note.objects.get(slug=slug)
        content = request.data.get('content')
        if not content:
            return Response({"error": "Content required"}, status=400)
        comment = NoteComment.objects.create(user=request.user, note=note, content=content)
        return Response({"id": comment.id, "content": comment.content, "user": comment.user.username})

class NoteCommentPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 50

class NoteCommentList(ListAPIView):
    serializer_class = NoteCommentSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    pagination_class = NoteCommentPagination

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        try:
            note = Note.objects.get(slug=slug)
        except Note.DoesNotExist:
            raise NotFound("Note not found")
        
        # Only return comments for this note
        return NoteComment.objects.filter(note=note).order_by('-created_at')
    

class NoteShare(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, slug):
        note = get_object_or_404(Note, slug=slug)

        # Increment share count
        note.shares_count = note.shares_count + 1 if note.shares_count else 1
        note.save(update_fields=['shares_count'])

        # Generate shareable link (assuming frontend will use it)
        shareable_link = request.build_absolute_uri(f'/notes/{note.slug}/')

        return Response({
            "message": "Note shared successfully",
            "shareable_link": shareable_link,
            "shares_count": note.shares_count
        }, status=status.HTTP_200_OK)


class NoteSummarizeView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, slug):
        try:
            note = Note.objects.get(slug=slug, user=request.user)
        except Note.DoesNotExist:
            return Response({"error": "Note not found."}, status=404)

        result = summarize_text(note.content)
        serializer = NoteSummarySerializer(result)
        return Response(serializer.data, status=200)
    

class NoteChatView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, slug):
        try:
            note = Note.objects.get(slug=slug)
        except Note.DoesNotExist:
            return Response({"error": "Note not found."}, status=status.HTTP_404_NOT_FOUND)

        # Restrict private notes
        if note.type == "private" and note.user != request.user:
            return Response({"error": "You cannot chat with this private note."}, status=status.HTTP_403_FORBIDDEN)

        user_message = request.data.get("message")
        if not user_message:
            return Response({"error": "Message is required."}, status=status.HTTP_400_BAD_REQUEST)

        note_content = note.content or ""
        if len(note_content.split()) > 2000:
            note_content = summarize_chunks(note_content, max_chunk_size=2000)

        chat_history = [
            {'user': c['user_message'], 'ai': c['ai_response']} 
            for c in note.chat_logs.values('user_message', 'ai_response')
        ]

        try:
            ai_response = ask_ai_with_note(note_content, user_message, chat_history=chat_history)
        except Exception as e:
            return Response({"error": f"AI processing failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        chat_log = NoteChatLog.objects.create(
            note=note,
            user=request.user,
            user_message=user_message,
            ai_response=ai_response
        )

        serializer = NoteChatLogSerializer(chat_log)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NoteChatHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, slug):
        try:
            note = Note.objects.get(slug=slug)
        except Note.DoesNotExist:
            return Response({"error": "Note not found."}, status=404)

        if note.type == "private" and note.user != request.user:
            return Response({"error": "Access denied."}, status=403)

        logs = note.chat_logs.all()
        serializer = NoteChatLogSerializer(logs, many=True)
        return Response(serializer.data)
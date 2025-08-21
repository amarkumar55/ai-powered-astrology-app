from . import views
from django.urls import path

urlpatterns = [
    path("process_note/", views.NoteListCreate().as_view(), name="api.process_notes"),
    path("<slug:slug>/", views.NoteDetail().as_view(), name="api.note_details"),
    path('<slug:slug>/like/', views.NoteLikeToggle.as_view(), name='note-like-toggle'),
    path('notes/<slug:slug>/share/',views.NoteShare.as_view(), name='note-share'),
    path('<slug:slug>/comment/', views.NoteCommentCreate.as_view(), name='note-comment-create'),
    path('notes/<slug:slug>/comments/',views.NoteCommentList.as_view(), name='note-comment-list'),
    path("notes/<slug:slug>/summarize/", views.NoteSummarizeView.as_view(), name="note-summarize"),
    path("notes/<slug:slug>/chat/", views.NoteChatView.as_view(), name="note-chat"),
    path('notes/<slug:slug>/chat/history/', views.NoteChatHistoryView.as_view(), name='note-chat-history'),
]
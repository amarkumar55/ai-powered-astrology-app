from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<chat_id>\w+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/video-call/(?P<room_id>\w+)/$', consumers.VideoCallConsumer.as_asgi()),
    re_path(r'ws/vendor/(?P<vendor_id>\w+)/status/$', consumers.VendorStatusConsumer.as_asgi()),
    re_path(r'ws/user/(?P<user_id>\w+)/notifications/$', consumers.NotificationConsumer.as_asgi()),
] 
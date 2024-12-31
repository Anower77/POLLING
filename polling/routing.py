from django.urls import re_path
from polls.consumers import PollConsumer

websocket_urlpatterns = [
    re_path(r'ws/poll/(?P<poll_id>\w+)/$', PollConsumer.as_asgi()),
] 
from django.urls import path
from .views import ChatListView, ChatCreateView, ChatDetailView, SendMessageView, StartChatView
from . import views

app_name = 'chat'
urlpatterns = [
    path('chats/', ChatListView.as_view(), name='chat_list'),
    path('chats/create/<str:username>/', ChatCreateView.as_view(), name='chat_create'),
    path('chats/<int:chat_id>/', ChatDetailView.as_view(), name='chat_detail'),
    path('start-chat/<str:username>/', StartChatView.as_view(), name='start_chat'),
    path('chats/<int:chat_id>/send/', SendMessageView.as_view(), name='send_message'),

]

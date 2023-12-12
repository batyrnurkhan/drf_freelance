from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ChatSerializer, MessageSerializer
from .models import Chat, Message
from accounts.models import CustomUser


class StartChatView(APIView):
    def post(self, request, username):
        client = get_object_or_404(CustomUser, username=username)
        if request.user.user_type == 'freelancer' and client.user_type == 'client':
            chat = Chat.get_or_create_with_participants(request.user, client)
            serializer = ChatSerializer(chat)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ChatListView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        chats = request.user.chats.all()
        serializer = ChatSerializer(chats, many=True)
        return Response(serializer.data)





class ChatDetailView(APIView):
    def get(self, request, chat_id):
        chat = get_object_or_404(Chat, id=chat_id)
        serializer = ChatSerializer(chat)
        return Response(serializer.data)

    def post(self, request, chat_id):
        chat = get_object_or_404(Chat, id=chat_id)
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, chat=chat)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatCreateView(APIView):
    def get(self, request, username):
        client = get_object_or_404(CustomUser, username=username)
        if request.user.user_type == 'freelancer' and client.user_type == 'client':
            chat, created = Chat.objects.get_or_create()
            chat.participants.add(request.user, client)
            serializer = ChatSerializer(chat)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


from rest_framework.permissions import IsAuthenticated


class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, chat_id):
        chat = get_object_or_404(Chat, pk=chat_id)
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, chat=chat)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

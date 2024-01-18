from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ChatSerializer
from .models import Chat
from accounts.models import CustomUser
import logging

logger = logging.getLogger(__name__)

class StartChatView(APIView):
    def post(self, request, username):
        try:
            client = get_object_or_404(CustomUser, username=username)
            logger.debug(f'Request User Role: {request.user.role}, Client Role: {client.role}')

            if request.user.role == 'freelancer' and client.role == 'client':
                chat = Chat.get_or_create_with_participants(request.user, client)
                serializer = ChatSerializer(chat)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                logger.debug('Role condition failed')
                return Response({'error': 'Invalid user roles or user not found'}, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            logger.debug('User not found')
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f'Error in StartChatView: {e}')
            return Response({'error': 'Server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
    def post(self, request, username):
        client = get_object_or_404(CustomUser, username=username)
        if request.user.role == 'client' and client.role == 'freelancer':
            # Use get_or_create_with_participants class method to handle chat creation
            chat = Chat.get_or_create_with_participants(request.user, client)
            serializer = ChatSerializer(chat)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Invalid user roles or user not found'}, status=status.HTTP_400_BAD_REQUEST)



from rest_framework.permissions import IsAuthenticated

from .serializers import MessageSerializer
class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, chat_id):
        chat = get_object_or_404(Chat, pk=chat_id)
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, chat=chat)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

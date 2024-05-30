from rest_framework import serializers
from .models import Chat, Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

class ChatSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    participant_usernames = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ['id', 'participant_usernames', 'messages']  # Include 'participant_usernames' here

    def get_participant_usernames(self, obj):
        try:
            participants = obj.participants.all()
            return [user.username for user in participants]
        except AttributeError as e:
            # Log the error or print it. Adjust logging based on your project setup
            print(f"Error in get_participant_usernames: {str(e)}")
            # Optionally, inspect the object type
            print(f"Object type passed: {type(obj)}")
            return []
from django.db import models
from accounts.models import CustomUser

class Chat(models.Model):
    participants = models.ManyToManyField(CustomUser, related_name='chats')

    @classmethod
    def get_or_create_with_participants(cls, user1, user2):
        chat = cls.objects.filter(participants=user1).filter(participants=user2).first()
        if chat is None:
            chat = cls.objects.create()
            chat.participants.add(user1, user2)
            chat.save()
        return chat

    def __str__(self):
        return "{}".format(self.pk)

    def get_other_participant(self, current_user):
        return self.participants.exclude(id=current_user.id).first()

class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    author = models.ForeignKey(CustomUser, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Chat {} - Author {}".format(self.chat.pk, self.author.email)

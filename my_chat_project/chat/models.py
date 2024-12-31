from django.db import models
from django.contrib.auth import get_user_model
CustomUser = get_user_model()

class GroupChat(models.Model):
    group_name = models.CharField(max_length=130, unique=True)

    def __str__(self) -> str:
        return self.group_name
    

class GroupMessage(models.Model):
    group = models.ForeignKey(GroupChat, related_name='chat_messages', on_delete=models.CASCADE)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    body = models.CharField(max_length=400)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.author.username} : {self.body}'
    
    class Meta:
        ordering = ['-created']
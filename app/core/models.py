from django.db import models

# Create your models here.

class Message(models.Model):
        text = models.TextField()
        chat_id = models.CharField(max_length=100)
        date = models.DateTimeField()
        message_id = models.CharField(max_length=100)
        user_id = models.CharField(max_length=100)
        username = models.CharField(max_length=100)
        first_name = models.CharField(max_length=100)
        last_name = models.CharField(max_length=100)
        language_code = models.CharField(max_length=100)
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)
        
        def __str__(self):
                return self.text
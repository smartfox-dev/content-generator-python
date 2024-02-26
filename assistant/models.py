from django.db import models
from django.utils import timezone

# Create your models here.
class Articles(models.Model):
    title = models.CharField(max_length=1000, default='')
    topic = models.CharField(max_length=1000, default='')
    keyword = models.CharField(max_length=1000, default='')
    content = models.CharField(max_length=10000000000, default='')
    word_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Title: {self.title}, Topic: {self.topic}, Content: {self.content}, Keyword: {self.keyword}, Word Count: {self.word_count}, Created At: {self.created_at}"
    
    class Meta:
            db_table = 'articles'
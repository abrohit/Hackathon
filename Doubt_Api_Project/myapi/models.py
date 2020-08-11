from django.db import models


class Questions(models.Model):
    Question = models.TextField()
    StudentID = models.CharField(max_length=20)
    SessionID = models.CharField(max_length=20)
    Upvote = models.TextField()
    Downvote = models.TextField()

    def __str__(self):
        return self.Question

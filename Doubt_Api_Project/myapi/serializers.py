from rest_framework import serializers

from .models import Questions

class QuestionsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Questions
        fields = ('id','Question', 'StudentID','SessionID','Upvote','Downvote')

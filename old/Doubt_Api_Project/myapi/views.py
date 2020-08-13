from django.shortcuts import render
from googlesearch import search
from rest_framework import viewsets
from .serializers import QuestionsSerializer
from .models import Questions

class QuestionsViewSet(viewsets.ModelViewSet):
    queryset = Questions.objects.all().order_by('id')
    serializer_class = QuestionsSerializer

def check_question(request):

    question = request.GET.get('checkquestion')

    for item in search(question, tld="com",lang='en', num=1, start=0,stop=1, pause=2):
        search_result = item
    return()

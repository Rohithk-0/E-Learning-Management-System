from django.db import models
from django.conf import settings
from courses.models import Course, Video

class Quiz(models.Model):
    title = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, null=True, blank=True)
    duration = models.IntegerField(default=10)
    max_attempts = models.PositiveIntegerField(default=3)

    def __str__(self):
        return f"{self.title} ({self.course.title})"

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500)

    def __str__(self):
        return self.text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class QuizAttempt(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.PositiveIntegerField()
    total = models.PositiveIntegerField()
    taken_at = models.DateTimeField(auto_now_add=True)
    attempts = models.PositiveIntegerField(default=1)
    last_attempt = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'quiz')

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} - {self.score}/{self.total}"


# quiz/models.py

from django.db import models
from django.conf import settings

class QuizLog(models.Model):
    ACTION_CHOICES = [
        ('added', 'Added'),
        ('edited', 'Edited'),
        ('deleted', 'Deleted'),
    ]

    quiz = models.ForeignKey('Quiz', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quiz} - {self.action} by {self.user}"

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Quiz, QuizLog
from threading import local

_user = local()

def set_current_user(user):
    _user.value = user

def get_current_user():
    return getattr(_user, 'value', None)

@receiver(post_save, sender=Quiz)
def log_quiz_save(sender, instance, created, **kwargs):
    user = get_current_user()
    if user:
        action = 'create' if created else 'update'
        QuizLog.objects.create(quiz=instance, user=user, action=action)

@receiver(pre_delete, sender=Quiz)
def log_quiz_delete(sender, instance, **kwargs):
    user = get_current_user()
    if user:
        QuizLog.objects.create(quiz=instance, user=user, action='delete')

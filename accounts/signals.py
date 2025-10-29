from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import StudentProfile
from courses.models import TrainerProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profiles(sender, instance, created, **kwargs):
    if created:
        if instance.is_student and not hasattr(instance, 'studentprofile'):
            StudentProfile.objects.create(user=instance)
        elif instance.is_trainer and not hasattr(instance, 'trainerprofile'):
            TrainerProfile.objects.create(user=instance)

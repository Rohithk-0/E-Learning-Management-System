
from django.db import models
from django.conf import settings



class TrainerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    skype = models.CharField(max_length=100, blank=True)
    whatsapp = models.CharField(max_length=15, blank=True)
    profile_pic = models.ImageField(upload_to='trainer_profiles/', default='default_profile.png')

    def __str__(self):
        return self.user.username
    
    def average_rating(self):
        avg = self.feedbacks.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else None


class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    trainer = models.ForeignKey(TrainerProfile, on_delete=models.SET_NULL, null=True, related_name='courses')
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.title
    
    def average_course_rating(self):
        avg = self.course_ratings.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0

from django.db.models import Avg

class VideoQuerySet(models.QuerySet):
    def with_avg_rating(self):
        return self.annotate(avg_rating=Avg('ratings__rating'))

class VideoManager(models.Manager):
    def get_queryset(self):
        return VideoQuerySet(self.model, using=self._db)

    def with_avg_rating(self):
        return self.get_queryset().with_avg_rating()


from django.db import models
from django.core.validators import FileExtensionValidator
from django.db.models import Avg
from accounts.models import User


class Video(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='videos/')
    video_url = models.URLField(blank=True, null=True) 
    duration_minutes = models.IntegerField(null=True, blank=True)
    trainer = models.ForeignKey(User, on_delete=models.CASCADE)

    resource = models.FileField(
        upload_to='resources/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=[
            'pdf', 'zip', 'ppt', 'pptx', 'doc', 'docx', 'txt'
        ])]
    )
    
    objects = VideoManager()

    def __str__(self):
        return self.title

    def average_rating(self):
        avg = self.ratings.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else None

    def rating_count(self):
        return self.ratings.count()
    
    def is_youtube(self):
        return self.video_url and "youtube.com" in self.video_url or "youtu.be" in self.video_url



class CourseProgress(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    completed_videos = models.ManyToManyField(Video, blank=True)

    def progress_percent(self):
        total = self.course.videos.count()
        completed = self.completed_videos.count()
        return round((completed / total) * 100, 1) if total > 0 else 0


from django.db import models
from django.conf import settings

class VideoRating(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    video = models.ForeignKey('Video', on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # 1 to 5 stars
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'video')  # Prevent duplicate ratings

    def __str__(self):
        return f'{self.student.username} - {self.video.title} - {self.rating}★'


from django.db import models
from django.conf import settings

class TrainerFeedback(models.Model):
    trainer = models.ForeignKey('TrainerProfile', on_delete=models.CASCADE, related_name='feedbacks')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('trainer', 'student', 'course')  # Prevent duplicate feedback

    def __str__(self):
        return f"{self.student.username} rated {self.trainer.user.username} - {self.rating}⭐"
    
    
class CourseRating(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='course_ratings', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} rated {self.course.title} - {self.rating}"

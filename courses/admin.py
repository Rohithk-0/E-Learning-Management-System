from django.contrib import admin
from .models import TrainerProfile, Course, Video, CourseProgress, CourseRating

admin.site.register(TrainerProfile)
admin.site.register(Course)
admin.site.register(Video)
admin.site.register(CourseProgress)
admin.site.register(CourseRating)

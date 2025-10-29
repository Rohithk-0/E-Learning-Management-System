# forms.py
from django import forms
from .models import Video, Course

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['course', 'title', 'video_file', 'duration_minutes', 'resource']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(VideoForm, self).__init__(*args, **kwargs)

        if user and hasattr(user, 'trainerprofile'):
            self.fields['course'].queryset = Course.objects.filter(trainer=user.trainerprofile)
        else:
            self.fields['course'].queryset = Course.objects.none()
            

from django import forms
from .models import VideoRating

class VideoRatingForm(forms.ModelForm):
    class Meta:
        model = VideoRating
        fields = ['rating','feedback']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, f'{i} Stars') for i in range(1, 6)]),
            'feedback': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Optional feedback...'}),
        }

from django import forms
from .models import TrainerProfile

class TrainerProfileForm(forms.ModelForm):
    class Meta:
        model = TrainerProfile
        fields = ['skype', 'whatsapp', 'profile_pic']


from django import forms
from .models import TrainerFeedback, TrainerProfile

from django import forms
from .models import TrainerFeedback, TrainerProfile
from accounts.models import User  # adjust import based on your app



class TrainerFeedbackForm(forms.ModelForm):
    class Meta:
        model = TrainerFeedback
        fields = ['trainer', 'rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, f"{i} Star") for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ✅ Filter TrainerProfiles whose linked user is marked as a trainer
        self.fields['trainer'].queryset = TrainerProfile.objects.filter(user__is_trainer=True)



from django import forms
from .models import Course

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'price']
        
        

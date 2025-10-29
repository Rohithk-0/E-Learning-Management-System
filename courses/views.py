from django.shortcuts import render, redirect, get_object_or_404
from .models import Course, Video, CourseProgress
from .forms import VideoForm
from django.contrib.auth.decorators import login_required
from payments.models import Payment

def course_list(request):
    courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses})

from .models import VideoRating
from .forms import VideoRatingForm
from collections import defaultdict

@login_required
def course_videos(request, course_id):
    if not hasattr(request.user, 'studentprofile'):
        messages.error(request, "Access denied. Only students can view this page.")
        return redirect('index')  # or home/dashboard

    course = get_object_or_404(Course, pk=course_id)

    # ✅ Payment check
    has_paid = Payment.objects.filter(student=request.user, course=course, status='SUCCESS').exists()
    if not has_paid:
        messages.warning(request, "Please purchase this course to access its videos.")
        return redirect('buy_course', course_id=course_id)

    videos = course.videos.all()
    progress, created = CourseProgress.objects.get_or_create(student=request.user, course=course)

    # ✅ Handle video complete & rating
    if request.method == "POST":
        video_id = request.POST.get("video_id")
        rating_value = request.POST.get("rating")
        video = get_object_or_404(Video, pk=video_id)
        progress.completed_videos.add(video)

        if rating_value:
            VideoRating.objects.update_or_create(
                video=video,
                student=request.user,
                defaults={'rating': rating_value}
            )

    ratings = defaultdict(lambda: None)
    for video in videos:
        video.rating_obj = VideoRating.objects.filter(video=video, student=request.user).first()


    percent = progress.progress_percent()
    return render(request, 'courses/course_videos.html', {
        'course': course,
        'videos': videos,
        'progress': int(percent),
        'ratings': ratings,
        'form': VideoRatingForm()
    })


@login_required
def add_video(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        video_url = request.POST.get('video_url')
        video_file = request.FILES.get('video_file')
        duration = request.POST.get('duration_minutes')
        course_id = request.POST.get('course')

        if not title or not duration or not course_id:
            messages.error(request, "Please fill all required fields.")
            return redirect('add_video')

        if not video_file and not video_url:
            messages.error(request, "Please provide either a YouTube URL or upload a video file.")
            return redirect('add_video')

        if video_file and video_url:
            messages.error(request, "Please provide only one: YouTube URL OR video file.")
            return redirect('add_video')

        course = get_object_or_404(Course, id=course_id)

        Video.objects.create(
            title=title,
            video_url=video_url if video_url else None,
            video_file=video_file if video_file else None,
            duration_minutes=duration,
            course=course
        )

        messages.success(request, "Video uploaded successfully.")
        return redirect('manage_courses')

    courses = Course.objects.all()
    return render(request, 'courses/add_video.html', {'courses': courses})



from django.contrib import messages

@login_required
def trainer_all_videos(request):
    if not hasattr(request.user, 'trainerprofile'):
        return redirect('course_list')

    trainer = request.user.trainerprofile
    videos = Video.objects.filter(course__trainer=trainer)

    return render(request, 'courses/trainer_video_list.html', {
        'videos': videos,
        'course': None
    })
    
@login_required
def trainer_course_videos(request, course_id):
    if not hasattr(request.user, 'trainerprofile'):
        return redirect('index')

    course = get_object_or_404(Course, id=course_id, trainer=request.user.trainerprofile)
    videos = course.videos.all()
    
    return render(request, 'courses/trainer_video_list.html', {
        'course': course,
        'videos': videos
    })



@login_required
def edit_video(request, video_id):
    video = get_object_or_404(Video, pk=video_id)

    if video.course.trainer != request.user.trainerprofile:
        messages.error(request, "You don't have permission to edit this video.")
        return redirect('trainer_video_list')

    if request.method == 'POST':
        form = VideoForm(request.POST, instance=video, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Video updated successfully.")
            return redirect('trainer_video_list')
    else:
        form = VideoForm(instance=video, user=request.user)

    return render(request, 'courses/edit_video.html', {'form': form, 'video': video})


@login_required
def delete_video(request, video_id):
    video = get_object_or_404(Video, pk=video_id)

    if video.course.trainer != request.user.trainerprofile:
        messages.error(request, "You don't have permission to delete this video.")
        return redirect('trainer_video_list')

    if request.method == 'POST':
        video.delete()
        messages.success(request, "Video deleted successfully.")
        return redirect('trainer_video_list')

    return render(request, 'courses/delete_video.html', {'video': video})

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import Course, CourseProgress

@login_required
def trainer_student_progress(request):
    if not hasattr(request.user, 'trainerprofile'):
        return redirect('index')

    trainer = request.user.trainerprofile
    courses = Course.objects.filter(trainer=trainer)

    data = []
    for course in courses:
        progress_records = CourseProgress.objects.filter(course=course)
        students = []
        for progress in progress_records:
            students.append({
                'student': progress.student,
                'percent': int(progress.progress_percent()),
            })
        data.append({
            'course': course,
            'students': students
        })

    return render(request, 'trainer/student_progress.html', {'data': data})

@login_required
def trainer_feedback_view(request):
    if not hasattr(request.user, 'trainerprofile'):
        return redirect('index')

    trainer = request.user.trainerprofile
    videos = Video.objects.filter(course__trainer=trainer).prefetch_related('ratings')

    video_data = []
    for video in videos:
        feedbacks = video.ratings.all()
        avg_rating = video.average_rating()
        video_data.append({
            'video': video,
            'avg': avg_rating,
            'feedbacks': feedbacks
        })

    return render(request, 'trainer/video_feedback.html', {'video_data': video_data})




    
from django.contrib.auth.decorators import login_required
from .forms import TrainerProfileForm
from .models import TrainerProfile

@login_required
def edit_trainer_profile(request):
    profile, _ = TrainerProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = TrainerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('trainer')  # or your dashboard
    else:
        form = TrainerProfileForm(instance=profile)

    return render(request, 'courses/edit_trainer_profile.html', {'form': form})



from django.contrib.auth import get_user_model
from .models import TrainerProfile

User = get_user_model()

@login_required
def trainer_list(request):
    trainers = TrainerProfile.objects.filter(user__is_trainer=True)
    return render(request, 'courses/trainer_list.html', {'trainers': trainers})


def trainer_detail(request, trainer_id):
    trainer = get_object_or_404(TrainerProfile, pk=trainer_id)
    courses = Course.objects.filter(trainer=trainer)
    return render(request, 'courses/trainer_detail.html', {
        'trainer': trainer,
        'courses': courses,
    })

from .forms import TrainerFeedbackForm
from .models import TrainerFeedback, TrainerProfile
from django.contrib import messages

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import TrainerFeedbackForm
from .models import TrainerFeedback, TrainerProfile, Course

@login_required
def rate_trainer(request, trainer_id=None, course_id=None):
    trainer = get_object_or_404(TrainerProfile, id=trainer_id) if trainer_id else None
    course = get_object_or_404(Course, id=course_id) if course_id else None

    # Check if already rated
    if trainer and course:
        if TrainerFeedback.objects.filter(student=request.user, trainer=trainer, course=course).exists():
            messages.info(request, "You've already rated this trainer for this course.")
            return redirect('student')

    if request.method == 'POST':
        form = TrainerFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.student = request.user

            if trainer:  # If passed from URL
                feedback.trainer = trainer
            if course:
                feedback.course = course

            feedback.save()
            messages.success(request, "Thanks for your feedback!")
            return redirect('student')

    else:
        form = TrainerFeedbackForm()

    return render(request, 'courses/rate_trainer.html', {
        'form': form,
        'trainer': trainer,
        'course': course
    })

 
from django.contrib.auth.decorators import login_required
from courses.models import Course
from django.shortcuts import render

@login_required
def trainer_courses(request):
    if not hasattr(request.user, 'trainerprofile'):
        return redirect('index')

    courses = Course.objects.filter(trainer=request.user.trainerprofile)
    return render(request, 'trainer/my_courses.html', {'courses': courses})


from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from notifications.models import Notification  
from .models import Video, VideoRating
from .forms import VideoRatingForm

@login_required
def rate_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)

    rating_obj, created = VideoRating.objects.get_or_create(
        student=request.user,
        video=video
    )

    if request.method == 'POST':
        form = VideoRatingForm(request.POST, instance=rating_obj)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.student = request.user
            feedback.video = video
            feedback.save()

            # ✅ Send trainer notification
            Notification.objects.create(
                user=video.course.trainer.user,
                message=f"{request.user.username} rated/commented on {video.title}.",
                link=request.build_absolute_uri(request.path)
            )

            messages.success(request, "Thanks for your feedback!")
            return redirect('course_videos', course_id=video.course.id)
    else:
        form = VideoRatingForm(instance=rating_obj)

    return render(request, 'courses/rate_video.html', {
        'form': form,
        'video': video
    })


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Video, VideoRating

@login_required
def trainer_video_feedback(request):
    if not hasattr(request.user, 'trainerprofile'):
        return redirect('index')  # not a trainer

    videos = Video.objects.filter(course__trainer=request.user.trainerprofile).prefetch_related('ratings')

    feedback_data = []
    for video in videos:
        feedback_data.append({
            'video': video,
            'ratings': video.ratings.all()
        })

    return render(request, 'trainer/video_feedback.html', {
        'feedback_data': feedback_data
    })

from django.db.models import Avg
from .models import Video

def top_rated_videos(request):
    top_videos = Video.objects.with_avg_rating()[:10]  # Top 10
    return render(request, 'courses/top_rated_videos.html', {'top_videos': top_videos})

from .models import CourseRating
from django.contrib import messages

@login_required
def rate_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        feedback = request.POST.get('feedback', '')

        obj, created = CourseRating.objects.update_or_create(
            student=request.user,
            course=course,
            defaults={'rating': rating, 'feedback': feedback}
        )
        messages.success(request, 'Thank you for rating this course!')
        return redirect('course_videos', course_id=course.id)

    return render(request, 'courses/rate_course.html', {'course': course})

from django.contrib.admin.views.decorators import staff_member_required
from .models import Course, CourseRating
from django.db.models import Avg, Count

@login_required
def manager_course_ratings(request):
    if not request.user.is_manager:
        return redirect('index')

    courses = Course.objects.annotate(
        avg_rating=Avg('course_ratings__rating'),
        total_ratings=Count('course_ratings')
    ).order_by('-avg_rating')

    return render(request, 'courses/manager_course_ratings.html', {'courses': courses})


from django.db.models import Q

@login_required
def manager_feedback_view(request):
    if not request.user.is_manager:
        return redirect('index')

    courses = Course.objects.all()
    ratings = CourseRating.objects.select_related('student', 'course', 'course__trainer')

    # Filters
    course_id = request.GET.get('course')
    min_rating = request.GET.get('min_rating')

    if course_id:
        ratings = ratings.filter(course_id=course_id)
    if min_rating:
        ratings = ratings.filter(rating__gte=min_rating)

    return render(request, 'courses/manager_feedback.html', {
        'ratings': ratings,
        'courses': courses,
        'selected_course': course_id,
        'selected_rating': min_rating
    })

import csv
from django.http import HttpResponse
from .models import CourseRating


@login_required
def export_feedback_csv(request):
    if not request.user.is_manager:
        return redirect('index')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="student_feedback.csv"'

    writer = csv.writer(response)
    writer.writerow(['Student', 'Course', 'Trainer', 'Rating', 'Feedback', 'Submitted At'])

    feedbacks = CourseRating.objects.select_related('student', 'course', 'course__trainer')

    course_id = request.GET.get('course')
    min_rating = request.GET.get('min_rating')

    if course_id:
        feedbacks = feedbacks.filter(course_id=course_id)
    if min_rating:
        feedbacks = feedbacks.filter(rating__gte=min_rating)

    for rating in feedbacks:
        writer.writerow([
            rating.student.username,
            rating.course.title,
            rating.course.trainer.user.username,
            rating.rating,
            rating.feedback or '',
            rating.created_at.strftime("%Y-%m-%d %H:%M")
        ])

    return response

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
import json

from .models import CourseRating  # make sure this is your model

@login_required
def feedback_charts(request):
    if not request.user.is_manager:
        return redirect('index')

    rating_data = CourseRating.objects.values('rating').annotate(count=Count('id')).order_by('-rating')

    labels = []
    data = []
    for entry in rating_data:
        labels.append(f"{entry['rating']} Stars")
        data.append(entry['count'])

    return render(request, 'courses/feedback_charts.html', {
        'labels': json.dumps(labels),   # 👈 JSON encoding
        'data': json.dumps(data)        # 👈 JSON encoding
    })


from django.db.models.functions import TruncMonth

@login_required
def feedback_timeline_chart(request):
    if not request.user.is_manager:
        return redirect('index')

    timeline_data = (
        CourseRating.objects
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(avg_rating=Avg('rating'), count=Count('id'))
        .order_by('month')
    )

    labels = [entry['month'].strftime('%b %Y') for entry in timeline_data]
    ratings = [round(entry['avg_rating'], 2) for entry in timeline_data]
    counts = [entry['count'] for entry in timeline_data]

    return render(request, 'courses/feedback_timeline.html', {
        'labels': labels,
        'ratings': ratings,
        'counts': counts
    })

from django.db.models import Avg, Count
from .models import TrainerProfile

@login_required
def trainer_performance_dashboard(request):
    if not request.user.is_manager:
        return redirect('index')

    trainer_stats = TrainerProfile.objects.filter(user__is_trainer=True).annotate(
    avg_rating=Avg('courses__course_ratings__rating'),
    total_courses=Count('courses', distinct=True),
    total_feedback=Count('courses__course_ratings', distinct=True),
    total_students=Count('courses__courseprogress__student', distinct=True)
)


    return render(request, 'courses/trainer_performance.html', {
        'trainer_stats': trainer_stats
    })

from .utils import get_low_rated_trainers

@login_required
def low_rated_trainers_view(request):
    if not request.user.is_manager:
        return redirect('index')

    low_trainers = get_low_rated_trainers()

    return render(request, 'courses/low_rated_trainers.html', {
        'low_trainers': low_trainers
    })

import csv
from django.http import HttpResponse

@login_required
def export_trainer_performance_csv(request):
    if not request.user.is_manager:
        return redirect('index')

    trainers = TrainerProfile.objects.annotate(
        avg_rating=Avg('course__courserating__rating'),
        total_courses=Count('course', distinct=True),
        total_feedback=Count('course__courserating', distinct=True),
        total_students=Count('course__courseprogress__student', distinct=True)
    )

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="trainer_performance.csv"'

    writer = csv.writer(response)
    writer.writerow(['Trainer', 'Courses', 'Students', 'Feedbacks', 'Avg. Rating'])

    for t in trainers:
        writer.writerow([
            t.user.username,
            t.total_courses,
            t.total_students,
            t.total_feedback,
            f"{t.avg_rating:.1f}" if t.avg_rating else "N/A"
        ])

    return response


from django.core.mail import EmailMessage
from django.conf import settings
from .utils import generate_weekly_summary_html

@login_required
def send_weekly_summary(request):
    if not request.user.is_manager:
        return redirect('index')

    html_content = generate_weekly_summary_html()
    subject = "📬 Weekly Trainer Performance Summary"
    to_email = request.user.email

    email = EmailMessage(subject, html_content, settings.EMAIL_FROM, [to_email])
    email.content_subtype = "html"

    if email.send():
        messages.success(request, "✅ Summary email sent successfully.")
    else:
        messages.error(request, "❌ Failed to send summary email.")

    return redirect('trainer_performance')





from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import redirect
from django.conf import settings
from django.core.mail import EmailMessage
from django.db.models import Avg
from .models import TrainerProfile

# Check if the user is a manager
def is_manager(user):
    return user.is_authenticated and user.role == 'manager'

@login_required
@user_passes_test(is_manager)
def notify_low_rated_trainers_view(request):
    trainers = TrainerProfile.objects.annotate(
        avg_rating=Avg('courses__course_ratings__rating')
    ).filter(avg_rating__lt=3.0)

    for trainer in trainers:
        email = trainer.user.email
        if email:
            subject = "⚠️ Improve Your Course Quality"
            message = f"""
Dear {trainer.user.first_name or trainer.user.username},

Your average rating has dropped below 3.0.
Current average: {round(trainer.avg_rating or 0, 1)}

Please review your course content and student feedback.

Tips:
- Add more practical examples
- Update older videos
- Engage with student questions

Thank you,
E-Learning Team
            """
            email_obj = EmailMessage(subject, message, settings.EMAIL_FROM, [email])
            try:
                email_obj.send()
                print(f"✅ Email sent to {email}")
            except Exception as e:
                print(f"❌ Failed to send email to {email}: {e}")


    return HttpResponse("<h4>✅ Notification sent to low-rated trainers.</h4>")


from .models import TrainerFeedback, VideoRating
from django.contrib.auth.decorators import login_required

@login_required
def all_feedbacks(request):
    if not request.user.is_manager:
        return redirect('index')

    trainer_feedbacks = TrainerFeedback.objects.select_related('trainer__user', 'student', 'course')
    video_feedbacks = VideoRating.objects.select_related('video', 'student')

    return render(request, 'courses/all_feedbacks.html', {
        'trainer_feedbacks': trainer_feedbacks,
        'video_feedbacks': video_feedbacks,
    })


from accounts.models import User
from .models import Course, CourseProgress
from django.db.models import Avg, Count

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from accounts.models import User
from courses.models import Course, CourseProgress

@login_required
def student_progress_report(request):
    # Only allow access to managers and trainers
    if not (request.user.is_manager or request.user.is_trainer):
        return redirect('index')

    students = User.objects.filter(is_student=True)
    
    # If trainer, show only their courses
    if request.user.is_trainer:
        courses = Course.objects.filter(trainer__user=request.user)
    else:
        courses = Course.objects.all()

    report_data = []

    for student in students:
        student_row = {
            'student': student.username,
            'progress': []
        }

        for course in courses:
            try:
                progress = CourseProgress.objects.get(student=student, course=course)
                percent = progress.progress_percent()
            except CourseProgress.DoesNotExist:
                percent = 0
            student_row['progress'].append({
                'course': course.title,
                'percent': int(percent)
            })
        report_data.append(student_row)

    context = {
        'courses': courses,
        'report_data': report_data
    }

    return render(request, 'courses/student_progress_report.html', context)


import openpyxl
from django.http import HttpResponse

@login_required
def export_progress_excel(request):
    if not (request.user.is_manager or request.user.is_trainer):
        return redirect('index')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Student Progress"

    students = User.objects.filter(is_student=True)

    if request.user.is_trainer:
        courses = Course.objects.filter(trainer__user=request.user)
    else:
        courses = Course.objects.all()

    headers = ['Student'] + [course.title for course in courses]
    ws.append(headers)

    for student in students:
        row = [student.username]
        for course in courses:
            try:
                progress = CourseProgress.objects.get(student=student, course=course)
                percent = int(progress.progress_percent())
            except CourseProgress.DoesNotExist:
                percent = 0
            row.append(f"{percent}%")
        ws.append(row)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=student_progress.xlsx'
    wb.save(response)
    return response


   


from django.contrib.auth import get_user_model
from .models import CourseProgress

User = get_user_model()

@login_required
def manage_student_progress(request):
    if not request.user.is_manager:
        return redirect('index')

    progress_records = CourseProgress.objects.select_related('student', 'course')

    return render(request, 'courses/manage_progress.html', {
        'progress_records': progress_records
    })


@login_required
def reset_student_progress(request, progress_id):
    if not request.user.is_manager:
        return redirect('index')

    progress = get_object_or_404(CourseProgress, pk=progress_id)
    progress.completed_videos.clear()
    messages.success(request, f"{progress.student.username}'s progress for {progress.course.title} has been reset.")
    return redirect('manage_student_progress')



from django.contrib.auth.decorators import login_required
from .models import CourseProgress, Course
from django.db.models import Prefetch

@login_required
def trainer_students(request):
    if not hasattr(request.user, 'trainerprofile'):
        return redirect('index')

    courses = Course.objects.filter(trainer__user=request.user)
    progress_data = CourseProgress.objects.filter(course__in=courses).select_related('student', 'course')

    return render(request, 'courses/trainer_students.html', {
        'progress_data': progress_data
    })


from django.http import HttpResponse
from django.template.loader import render_to_string
import pdfkit  # or use xhtml2pdf, reportlab, etc.
from django.contrib.auth.decorators import login_required
from .models import Course, CourseProgress

@login_required
def download_certificate(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    progress = get_object_or_404(CourseProgress, student=request.user, course=course)

    if progress.progress_percent() < 100:
        messages.error(request, "You must complete the course to download the certificate.")
        return redirect('course_videos', course_id=course.id)

    html = render_to_string("courses/certificate_template.html", {
        'student': request.user,
        'course': course
    })

    pdf = pdfkit.from_string(html, False)  # Requires wkhtmltopdf installed

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{course.title}_certificate.pdf"'
    return response



# views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Video, CourseProgress  # adjust import path as needed


@login_required
def watch_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)

    # Convert YouTube URLs
    if video.video_url:
        if "youtube.com/watch" in video.video_url:
            video.video_url = video.video_url.replace("watch?v=", "embed/")
        elif "youtu.be/" in video.video_url:
            youtube_id = video.video_url.split('/')[-1]
            video.video_url = f"https://www.youtube.com/embed/{youtube_id}"

    # Mark video as completed
    progress, _ = CourseProgress.objects.get_or_create(
        student=request.user,
        course=video.course
    )
    if not progress.completed_videos.filter(id=video.id).exists():
        progress.completed_videos.add(video)

    is_mp4 = bool(video.video_file)

    return render(request, 'courses/watch.html', {
        'video': video,
        'is_mp4': is_mp4
    })



import json

from django.shortcuts import render, redirect
from .forms import SignUpForm, LoginForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from django.contrib import messages
from .tokens import account_activation_token
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from .models import State, District
from .models import Country
from courses.models import Course


from django.http import JsonResponse


# Create your views here.

def index(request):
    return render(request, 'accounts/index.html')

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SignUpForm

User = get_user_model()

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Thank you for your email confirmation. Now you can login your account.")
        
        # ✅ Automatically log in the user
        login(request, user)
        
        # ✅ Redirect based on role
        if user.is_manager:
            return redirect('manager')
        elif user.is_student:
            return redirect('student')
        elif user.is_trainer:
            return redirect('trainer')
        else:
            return redirect('login')  # fallback

    else:
        messages.error(request, "Activation link is invalid!")
        return redirect('index')


from django.core.mail import get_connection
from django.conf import settings

def activateEmail(request, user, to_email):
    mail_subject = "Activate your user account."
    message = render_to_string("activate_account.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })

    # ✅ Use SSL context from settings (fixes the certificate error)
    connection = get_connection(
        username=settings.EMAIL_HOST_USER,
        password=settings.EMAIL_HOST_PASSWORD,
        fail_silently=False,
        use_tls=True,
        host=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        ssl_context=settings.EMAIL_SSL_CONTEXT
    )

    email = EmailMessage(
        mail_subject,
        message,
        from_email=settings.EMAIL_FROM,
        to=[to_email],
        connection=connection
    )

    if email.send():
        messages.success(request, f'Dear <b>{user}</b>, please go to your email <b>{to_email}</b> and click on the activation link. <b>Note:</b> Check your spam folder.')
    else:
        messages.error(request, f'Problem sending email to {to_email}, check if the address is correct.')

        
        
def register(request):
    countries = Country.objects.all() 
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # ✅ Prevent login until activation
            user.save()
            activateEmail(request, user, form.cleaned_data.get('email'))
            
            return redirect('index')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        form = SignUpForm()

    return render(request=request,
        template_name="register.html",
        context={"form": form,"countries": countries}
        )
from django import forms
from django.contrib.auth.models import User
from django.conf import settings

def clean(self):
    cleaned_data = super().clean()
    is_trainer = cleaned_data.get("is_trainer")
    is_manager = cleaned_data.get("is_manager")
    passkey = cleaned_data.get("passkey")

    if is_trainer and passkey != settings.TRAINER_PASSKEY:
        raise forms.ValidationError("Invalid passkey for Trainer access.")

    if is_manager and passkey != settings.MANAGER_PASSKEY:
        raise forms.ValidationError("Invalid passkey for Manager access.")



def login_view(request):
    form = LoginForm(request.POST or None)
    msg = None

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_manager:
                    login(request, user)
                    return redirect('manager')
                elif user.is_student:
                    login(request, user)
                    return redirect('student')
                elif user.is_trainer:
                    login(request, user)
                    return redirect('trainer')
                else:
                    # ✅ Fallback in case no role is selected
                    login(request, user)
                    return redirect('index')  # or another default page
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating form'

    return render(request, 'login.html', {'form': form, 'msg': msg})

from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return redirect('index')

# def home(request):
#     return render(request, 'home.html')

from .models import User  # use your custom user model
from courses.models import TrainerProfile

from django.db.models import Avg, Count, F
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import User
from payments.models import Payment
from courses.models import Course, CourseProgress
from django.db.models import Avg, F, Count, FloatField, ExpressionWrapper


@login_required
def manager(request):
    if not request.user.is_manager:
        return redirect('index')

    # Dashboard Metrics
    total_students = User.objects.filter(is_student=True).count()
    total_courses = Course.objects.count()
    total_purchases = Payment.objects.filter(status='SUCCESS').count()

    # Step 1: Annotate each CourseProgress with video count from the related course
    progress_qs = CourseProgress.objects.annotate(
    total_videos=Count('course__videos', distinct=True)).annotate(
    percentage=ExpressionWrapper(
        F('completed_videos') * 100.0 / F('total_videos'),
        output_field=FloatField()
    )
)

# Step 2: Aggregate the average percentage
    avg_progress = progress_qs.aggregate(average=Avg('percentage'))['average'] or 0

    # Trainers & Courses
    trainers = TrainerProfile.objects.filter(user__is_trainer=True)

    courses = Course.objects.all()
    students = User.objects.filter(is_student=True)


    context = {
        'total_students': total_students,
        'total_courses': total_courses,
        'total_purchases': total_purchases,
        'avg_progress': round(avg_progress, 2),
        'trainers': trainers,
        'courses': courses,
        'students': students
    }
    return render(request, 'manager/manager.html', context)



@login_required
def add_trainer(request):
    if not request.user.is_manager:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Create trainer user
        user = User.objects.create_user(username=username, email=email, password=password, is_trainer=True)
        TrainerProfile.objects.create(user=user)
        messages.success(request, 'Trainer added successfully!')
        return redirect('manager')

    return render(request, 'manager/add_trainer.html')


@login_required
def add_course(request):
    if not request.user.is_manager:
        return redirect('index')

    trainers = TrainerProfile.objects.filter(user__is_trainer=True)


    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        price = request.POST.get('price')
        trainer_id = request.POST.get('trainer')

        trainer = TrainerProfile.objects.get(id=trainer_id)
        Course.objects.create(title=title, description=description, price=price, trainer=trainer)

        messages.success(request, 'Course added successfully!')
        return redirect('manager')

    return render(request, 'manager/add_course.html', {'trainers': trainers})



from django.shortcuts import render
from courses.models import CourseProgress
import json

def student(request):
    course_progresses = CourseProgress.objects.filter(student=request.user).select_related('course')

    titles = []
    progress_data = []
    course_data = []

    for cp in course_progresses:
        progress = round(cp.progress_percent(), 1)
        course = cp.course
        titles.append(course.title)
        progress_data.append(progress)

        # Handle image URL safely
        image_url = course.image.url if hasattr(course, 'image') and course.image else None

        course_data.append({
            "title": course.title,
            "progress": progress,
            "image": image_url
        })

    return render(request, 'student.html', {
        "course_titles": json.dumps(titles),           # For Chart.js
        "course_progress": json.dumps(progress_data),  # For Chart.js
        "course_data": course_data                     # For progress cards
    })



def trainer(request):
    return render(request,'trainer.html')


def load_states(request):
    country_id = request.GET.get('country_id')
    states = State.objects.filter(country_id=country_id).order_by('name')
    return JsonResponse(list(states.values('id', 'name')), safe=False)

def load_districts(request):
    state_id = request.GET.get('state_id')
    districts = District.objects.filter(state_id=state_id).order_by('name')
    return JsonResponse(list(districts.values('id', 'name')), safe=False)


from django.contrib.admin.views.decorators import staff_member_required
from courses.models import TrainerFeedback

@login_required
def all_feedback(request):
    if not request.user.is_manager:
        return redirect('index')

    feedbacks = TrainerFeedback.objects.select_related('trainer', 'student')
    return render(request, 'manager/all_feedback.html', {'feedbacks': feedbacks})

from payments.models import Purchase

@login_required
def all_purchases(request):
    if not request.user.is_manager:
        return redirect('index')

    purchases = Purchase.objects.select_related('student', 'course')
    return render(request, 'manager/all_purchases.html', {'purchases': purchases})

from courses.models import CourseProgress

@login_required
def student_progress(request):
    if not request.user.is_manager:
        return redirect('index')

    progress_data = CourseProgress.objects.select_related('student', 'course')
    return render(request, 'manager/student_progress.html', {'progress_data': progress_data})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from courses.models import Course
from courses.models import TrainerProfile  # Make sure this is the correct model

@login_required
def assign_trainer(request):
    if not request.user.is_manager:
        messages.error(request, "Only managers can assign trainers.")
        return redirect('index')

    courses = Course.objects.all()
    trainers = TrainerProfile.objects.filter(user__is_trainer=True)



    if request.method == 'POST':
        course_id = request.POST.get('course')
        trainer_id = request.POST.get('trainer')

        course = get_object_or_404(Course, id=course_id)
        trainer = get_object_or_404(TrainerProfile, id=trainer_id)

        course.trainer = trainer
        course.save()

        messages.success(request, f"Trainer '{trainer.user.username}' assigned to course '{course.title}'")
        return redirect('assign_trainer')

    return render(request, 'manager/assign_trainer.html', {
        'courses': courses,
        'trainers': trainers
    })


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from courses.models import Course
from courses.forms import CourseForm  # We'll create this next

@login_required
def manage_courses(request):
    if not request.user.is_manager:
        return redirect('index')
    courses = Course.objects.all()
    return render(request, 'manager/manage_courses.html', {'courses': courses})

# @login_required
# def add_course(request):
#     if not request.user.is_manager:
#         return redirect('index')
#     if request.method == "POST":
#         form = CourseForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('manage_courses')
#     else:
#         form = CourseForm()
#     return render(request, 'manager/add_course.html', {'form': form})

@login_required
def edit_course(request, course_id):
    if not request.user.is_manager:
        return redirect('index')
    course = get_object_or_404(Course, pk=course_id)
    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('manage_courses')
    else:
        form = CourseForm(instance=course)
    return render(request, 'manager/edit_course.html', {'form': form, 'course': course})

@login_required
def delete_course(request, course_id):
    if not request.user.is_manager:
        return redirect('index')
    course = get_object_or_404(Course, pk=course_id)
    course.delete()
    return redirect('manage_courses')

from .forms import StudentProfileForm, StudentUserForm
from accounts.models import StudentProfile


@login_required
def edit_student_profile(request):
    if not request.user.is_student:
        return redirect('index')

    # ✅ Create student profile if missing
    profile, created = StudentProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = StudentUserForm(request.POST, instance=request.user)
        profile_form = StudentProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('student')
    else:
        user_form = StudentUserForm(instance=request.user)
        profile_form = StudentProfileForm(instance=profile)

    return render(request, 'student/edit_student_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


from django.http import JsonResponse
from courses.models import CourseProgress

@login_required
def ajax_course_progress_data(request):
    progress_data = CourseProgress.objects.filter(student=request.user)
    labels = []
    progress = []

    for cp in progress_data:
        labels.append(cp.course.title)
        progress.append(cp.progress_percent())  # make sure this method returns int

    return JsonResponse({
        'labels': labels,
        'progress': progress
    })


from django.http import JsonResponse
from courses.models import Video, VideoRating, CourseProgress

@login_required
def rate_video_ajax(request):
    if request.method == 'POST':
        video = get_object_or_404(Video, id=request.POST.get('video_id'))
        rating = request.POST.get('rating')
        feedback = request.POST.get('feedback')
        VideoRating.objects.update_or_create(
            video=video,
            student=request.user,
            defaults={'rating': rating, 'feedback': feedback}
        )
        return JsonResponse({'status': 'success'})

@login_required
def mark_completed_ajax(request):
    if request.method == 'POST':
        video = get_object_or_404(Video, id=request.POST.get('video_id'))
        progress, _ = CourseProgress.objects.get_or_create(
            student=request.user,
            course=video.course
        )
        progress.completed_videos.add(video)
        progress.save()
        return JsonResponse({'status': 'success'})

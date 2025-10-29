from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Quiz, Question, Choice, QuizAttempt
from .forms import QuizForm

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Quiz, Choice, QuizAttempt
from .forms import QuizForm
from django.contrib import messages

from courses.models import CourseProgress

@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.prefetch_related('choices')

    try:
        attempt = QuizAttempt.objects.get(student=request.user, quiz=quiz)
        if attempt.attempts >= quiz.max_attempts:
            messages.warning(request, "You have reached the maximum attempts.")
            return redirect('student_quiz_dashboard')
    except QuizAttempt.DoesNotExist:
        attempt = None

    if request.method == 'POST':
        score = 0
        total = questions.count()

        for question in questions:
            selected = request.POST.get(f'q_{question.id}')
            correct_choice = question.choices.filter(is_correct=True).first()
            if correct_choice and selected == str(correct_choice.id):
                score += 1

        if attempt:
            attempt.score = score
            attempt.total = total
            attempt.attempts += 1
            attempt.save()
        else:
            QuizAttempt.objects.create(student=request.user, quiz=quiz, score=score, total=total)

        messages.success(request, f'You scored {score}/{total}')
        return redirect('student_quiz_dashboard')

    return render(request, 'quiz/take_quiz.html', {
        'quiz': quiz,
        'questions': questions
    })




@login_required
def quiz_result(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    attempt = get_object_or_404(QuizAttempt, quiz=quiz, student=request.user)

    percent = int((attempt.score / attempt.total) * 100) if attempt.total else 0

    return render(request, 'quiz/quiz_result.html', {
        'quiz': quiz,
        'score': attempt.score,
        'total': attempt.total,
        'percent': percent,
        'attempt': attempt
    })

# Student
@login_required
def student_quiz_dashboard(request):
    attempts = QuizAttempt.objects.filter(student=request.user).select_related('quiz')
    quizzes = Quiz.objects.all()  # Or filter for only available ones
    return render(request, 'quiz/student_quiz_dashboard.html', {
        'attempts': attempts,
        'quizzes': quizzes
    })

# Trainer
@login_required
def trainer_quiz_dashboard(request):
    if not hasattr(request.user, 'trainerprofile'):
        return redirect('index')

    quizzes = Quiz.objects.filter(course__trainer=request.user.trainerprofile)
    attempts = QuizAttempt.objects.filter(quiz__in=quizzes).select_related('student', 'quiz')
    return render(request, 'quiz/trainer_quiz_dashboard.html', {'attempts': attempts})

# Manager
@login_required
def manager_quiz_dashboard(request):
    if not request.user.is_manager:
        return redirect('index')

    attempts = QuizAttempt.objects.select_related('student', 'quiz', 'quiz__course')
    return render(request, 'quiz/manager_quiz_dashboard.html', {'attempts': attempts})


# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages  # For success/warning messages
from .models import Quiz, Question, Choice, Course, Video  # Import your models
from django.urls import reverse



@login_required
def create_quiz(request):
    if not (hasattr(request.user, 'trainerprofile') or request.user.is_manager):
        return redirect('index')

    if request.user.is_manager:
        courses = Course.objects.all()
        videos = Video.objects.all()
    else:
        trainer = request.user.trainerprofile
        courses = Course.objects.filter(trainer=trainer)
        videos = Video.objects.filter(course__trainer=trainer)

    if request.method == 'POST':
        title = request.POST.get('title')

        course_id = request.POST.get('course')
        video_id = request.POST.get('video')
        duration = request.POST['duration']
        max_attempts = request.POST['max_attempts']
        

        course = get_object_or_404(Course, id=course_id)
        video = Video.objects.get(id=video_id) if video_id else None
        
        

        quiz = Quiz.objects.create(
            title=title,
            course=course,
            video=video,
            duration=duration,
            max_attempts=max_attempts


        )
        question_count = int(request.POST.get('question_count'))
        messages.success(request, 'Quiz created! Now add questions.')
        return redirect(f"{reverse('add_question', kwargs={'quiz_id': quiz.id})}?count={question_count}")



    return render(request, 'quiz/create_quiz.html', {
        'courses': courses,
        'videos': videos
    })


@login_required
def add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Safely get total from ?count= in URL
    total_questions = request.GET.get('count')
    try:
        total_questions = int(total_questions)
    except (TypeError, ValueError):
        total_questions = None  # fallback

    # Restrict access
    if not (request.user.is_manager or (hasattr(request.user, 'trainerprofile') and quiz.course.trainer == request.user.trainerprofile)):
        return redirect('index')

    if request.method == 'POST':
        question_text = request.POST['question']
        choices = [
            {'text': request.POST['choice1'], 'correct': request.POST.get('correct') == '1'},
            {'text': request.POST['choice2'], 'correct': request.POST.get('correct') == '2'},
            {'text': request.POST['choice3'], 'correct': request.POST.get('correct') == '3'},
            {'text': request.POST['choice4'], 'correct': request.POST.get('correct') == '4'},
        ]

        question = Question.objects.create(quiz=quiz, text=question_text)
        for c in choices:
            Choice.objects.create(question=question, text=c['text'], is_correct=c['correct'])

        messages.success(request, 'Question added.')

        # Redirect after last question
        if total_questions and quiz.questions.count() >= total_questions:
            return redirect('quiz_summary', quiz.id)

        return redirect(f"{request.path}?count={total_questions}" if total_questions else request.path)

    return render(request, 'quiz/add_question.html', {
        'quiz': quiz,
        'total': total_questions,                    # This is what makes it show up
        'added': quiz.questions.count()
    })




@login_required
def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # ✅ Allow access if user is manager or the quiz's trainer
    if request.user.is_manager or (hasattr(request.user, 'trainerprofile') and quiz.course.trainer == request.user.trainerprofile):
        form = QuizForm(request.POST or None, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quiz updated successfully.')
            # Redirect manager or trainer to their respective dashboards
            if request.user.is_manager:
                return redirect('manager_quiz_list')
            else:
                return redirect('trainer_quiz_dashboard')
        return render(request, 'quiz/edit_quiz.html', {'form': form})
    
    # 🚫 Unauthorized access
    return redirect('index')



@login_required
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.user.is_manager or (hasattr(request.user, 'trainerprofile') and quiz.course.trainer == request.user.trainerprofile):
        quiz.delete()
        messages.success(request, 'Quiz deleted successfully.')
        if request.user.is_manager:
            return redirect('manager_quiz_list')
        else:
            return redirect('trainer_quiz_dashboard')

    return redirect('index')

from django.db.models import Count

@login_required
def manager_quiz_list(request):
    if not request.user.is_manager:
        return redirect('index')

    quizzes = Quiz.objects.select_related('course', 'video', ).annotate(
        question_count=Count('questions')  # ✅ this is required
    )

   
    return render(request, 'quiz/manager_quiz_list.html', {'quizzes': quizzes})


# views.py
from .models import QuizLog

def quiz_activity_log(request):
    logs = QuizLog.objects.select_related('quiz', 'user').order_by('-timestamp')
    return render(request, 'quiz/logs.html', {'logs': logs})

@login_required
def quiz_summary(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.prefetch_related('choices')

    return render(request, 'quiz/quiz_summary.html', {
        'quiz': quiz,
        'questions': questions
    })

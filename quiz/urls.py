from django.urls import path
from . import views

urlpatterns = [
    path('<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('<int:quiz_id>/result/', views.quiz_result, name='quiz_result'),
    # urls.py
    path('trainer/create-quiz/', views.create_quiz, name='create_quiz'),
    path('trainer/add-question/<int:quiz_id>/', views.add_question, name='add_question'),
    path('quiz/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    
    path('trainer/quiz-summary/<int:quiz_id>/', views.quiz_summary, name='quiz_summary'),
    
    path('<int:quiz_id>/edit/', views.edit_quiz, name='edit_quiz'),  # ✅ This fixes the error
    path('<int:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'),

    path('student/quiz-dashboard/', views.student_quiz_dashboard, name='student_quiz_dashboard'),
    path('trainer/quiz-dashboard/', views.trainer_quiz_dashboard, name='trainer_quiz_dashboard'),
    path('manager/quiz-dashboard/', views.manager_quiz_dashboard, name='manager_quiz_dashboard'),
    
    # urls.py
    path('manager/quizzes/', views.manager_quiz_list, name='manager_quiz_list')



]

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # General
    path('', views.index, name='index'),
   
    path('login/', views.login_view, name='login_view'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    # Manager module
    path('manager/', views.manager, name='manager'),
    path('manager/add-trainer/', views.add_trainer, name='add_trainer'),
    path('manager/add-course/', views.add_course, name='add_course'),
    path('assign-trainer/', views.assign_trainer, name='assign_trainer'),
    path('all-feedback/', views.all_feedback, name='all_feedback'),
    path('all-purchases/', views.all_purchases, name='all_purchases'),

    # Student & Trainer
    path('student/', views.student, name='student'),
    path('ajax/progress/', views.ajax_course_progress_data, name='ajax_course_progress_data'),
    path('trainer/', views.trainer, name='trainer'),
    path('progress/', views.student_progress, name='student_progress'),

    # AJAX Dropdowns
    path('ajax/load-states/', views.load_states, name='ajax_load_states'),
    path('ajax/load-districts/', views.load_districts, name='ajax_load_districts'),

    # Course management
    path('courses/', views.manage_courses, name='manage_courses'),
    path('courses/add/', views.add_course, name='add_course'),
    path('courses/edit/<int:course_id>/', views.edit_course, name='edit_course'),
    path('courses/delete/<int:course_id>/', views.delete_course, name='delete_course'),
    
    path('student/edit-profile/', views.edit_student_profile, name='edit_student_profile'),

    # Password Reset
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html'
    ), name='password_reset'),

    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html'
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),

    # Password Change for Student
    path('student/password-change/', auth_views.PasswordChangeView.as_view(
        template_name='student/password_change.html',
        success_url='/student/'
    ), name='student_password_change'),
    
    path('ajax/rate/', views.rate_video_ajax, name='rate_video_ajax'),
    path('ajax/complete/', views.mark_completed_ajax, name='mark_completed_ajax'),

]

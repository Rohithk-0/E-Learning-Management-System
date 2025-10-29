from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('<int:course_id>/videos/', views.course_videos, name='course_videos'),
    path('trainer/add-video/', views.add_video, name='add_video'),
    path('my-videos/', views.trainer_all_videos, name='trainer_video_list'),
    path('edit-video/<int:video_id>/', views.edit_video, name='edit_video'),
    path('delete-video/<int:video_id>/', views.delete_video, name='delete_video'),
    
    path('trainer/student-progress/', views.trainer_student_progress, name='trainer_student_progress'),
    path('trainer/video-feedback/', views.trainer_feedback_view, name='trainer_feedback'),
    
    path('trainer/edit-profile/', views.edit_trainer_profile, name='edit_trainer_profile'),
    
    path('trainers/', views.trainer_list, name='trainer_list'),
    path('trainers/<int:trainer_id>/', views.trainer_detail, name='trainer_detail'),
    
    path('rate-trainer/<int:trainer_id>/<int:course_id>/', views.rate_trainer, name='rate_trainer'),
    
    path('trainer/students/', views.trainer_students, name='trainer_students'),

    

    
    path('my-courses/', views.trainer_courses, name='trainer_courses'),
    
    path('trainer/course/<int:course_id>/videos/', views.trainer_course_videos, name='trainer_video_list_by_course'),
    
    path('video/<int:video_id>/rate/', views.rate_video, name='rate_video'),
    
    path('trainer/video-feedback/', views.trainer_video_feedback, name='trainer_video_feedback'),
    
    path('top-rated/', views.top_rated_videos, name='top_rated_videos'),
    
    path('rate-course/<int:course_id>/', views.rate_course, name='rate_course'),
    
    path('manager/course-ratings/', views.manager_course_ratings, name='manager_course_ratings'),
    
    path('manager/feedback/', views.manager_feedback_view, name='manager_feedback'),
    
    path('manager/export-feedback/', views.export_feedback_csv, name='export_feedback'),
    
    path('manager/feedback-charts/', views.feedback_charts, name='feedback_charts'),
    
    path('manager/feedback-trend/', views.feedback_timeline_chart, name='feedback_timeline'),
    
    path('manager/trainer-performance/', views.trainer_performance_dashboard, name='trainer_performance'),
    
    path('manager/low-rated-trainers/', views.low_rated_trainers_view, name='low_rated_trainers'),
    
    path('manager/export-trainers/', views.export_trainer_performance_csv, name='export_trainer_csv'),
    
    path('manager/send-summary/', views.send_weekly_summary, name='send_weekly_summary'),
    
    path('manager/notify-low-ratings/', views.notify_low_rated_trainers_view, name='notify_low_ratings'),
    
    path('manager/feedbacks/', views.all_feedbacks, name='all_feedbacks'),
    
    path('manager/progress-report/', views.student_progress_report, name='student_progress_report'),
    
    path('manager/progress-report/export/', views.export_progress_excel, name='export_progress_excel'),
    
    path('manager/progress/', views.manage_student_progress, name='manage_student_progress'),
    path('manager/reset-progress/<int:progress_id>/', views.reset_student_progress, name='reset_student_progress'),
    
    path('certificate/<int:course_id>/', views.download_certificate, name='download_certificate'),
    
    path('watch/<int:video_id>/', views.watch_video, name='watch_video'),






]

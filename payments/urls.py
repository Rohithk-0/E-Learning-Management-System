from django.urls import path
from . import views

urlpatterns = [
    path('courses/', views.browse_courses, name='browse_courses'),
    path('buy/<int:course_id>/', views.buy_course, name='buy_course'),

    path('my-purchases/', views.my_purchases, name='my_purchases'),
    path('manager/all-purchases/', views.all_purchases, name='all_purchases'),

]


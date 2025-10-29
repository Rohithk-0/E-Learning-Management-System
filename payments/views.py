from django.shortcuts import render, redirect, get_object_or_404
from .models import Payment
from courses.models import Course
from django.contrib.auth.decorators import login_required

from .models import Payment

@login_required
def buy_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    # Simulate payment success
    payment, created = Payment.objects.get_or_create(
        student=request.user,
        course=course,
        defaults={'amount': course.price, 'status': 'SUCCESS'}
    )

    if not created and payment.status != 'SUCCESS':
        payment.status = 'SUCCESS'
        payment.save()

    # Save purchase record
    Purchase.objects.get_or_create(student=request.user, course=course)

    return redirect('course_videos', course_id=course.id)



@login_required
def my_purchases(request):
    payments = Payment.objects.filter(student=request.user, status='SUCCESS')
    return render(request, 'payments/my_purchases.html', {'payments': payments})

from .models import Purchase

@login_required
def browse_courses(request):
    all_courses = Course.objects.all()
    purchases = Purchase.objects.filter(student=request.user).values_list('course_id', flat=True)

    return render(request, 'courses/browse_courses.html', {
        'courses': all_courses,
        'purchased': purchases
    })

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.utils.dateparse import parse_date
from payments.models import Payment
from django.contrib.auth.decorators import login_required

@login_required
def all_purchases(request):
    if not request.user.is_manager:
        return redirect('index')

    query = Q(status='SUCCESS')
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')

    if start_date:
        query &= Q(timestamp__date__gte=parse_date(start_date))
    if end_date:
        query &= Q(timestamp__date__lte=parse_date(end_date))

    purchases = Payment.objects.filter(query).select_related('student', 'course').order_by('-timestamp')

    context = {
        'purchases': purchases,
        'start_date': start_date,
        'end_date': end_date
    }
    return render(request, 'payments/all_purchases.html', context)


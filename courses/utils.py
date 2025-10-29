from django.db.models import Avg
from .models import TrainerProfile

def get_low_rated_trainers(threshold=3.0):
    return TrainerProfile.objects.annotate(
        avg_rating=Avg('courses__course_ratings__rating')
    ).filter(avg_rating__lt=threshold)


from django.db.models import Avg, Count
from .models import TrainerProfile

def generate_weekly_summary_html():
    trainers = TrainerProfile.objects.annotate(
        avg_rating=Avg('courses__course_ratings__rating'),
        total_students=Count('courses__courseprogress__student', distinct=True)
    )

    html = """
    <h2>📊 Trainer Performance Summary</h2>
    <table border="1" cellpadding="10" cellspacing="0" style="border-collapse: collapse;">
        <tr>
            <th>Trainer</th>
            <th>Avg Rating</th>
            <th>Total Students</th>
        </tr>
    """

    for t in trainers:
        html += f"""
            <tr>
                <td>{t.user.username}</td>
                <td>{round(t.avg_rating, 1) if t.avg_rating else 'N/A'}</td>
                <td>{t.total_students}</td>
            </tr>
        """

    html += "</table>"
    return html


from django.db.models import Avg
from django.core.mail import EmailMessage
from django.conf import settings
from .models import TrainerProfile

def notify_low_rated_trainers(threshold=3.0):
    trainers = TrainerProfile.objects.annotate(
        avg_rating=Avg('courses__course_ratings__rating')
    ).filter(avg_rating__lt=threshold)

    for trainer in trainers:
        email = trainer.user.email
        if email:
            subject = "⚠️ Improve Your Course Quality"
            message = f"""
Dear {trainer.user.first_name or trainer.user.username},

Your average rating has dropped below {threshold}.
Current average: {round(trainer.avg_rating or 0, 1)}

Please review your course content and student feedback.

Tips:
- Add more practical examples
- Update older videos
- Engage with student questions

Thank you,
E-Learning Team
            """
            email_obj = EmailMessage(
                subject,
                message,
                settings.EMAIL_FROM,
                [email]
            )

            try:
                email_obj.send()
                print(f"✅ Email sent to {email}")
            except Exception as e:
                print(f"❌ Failed to email {email}: {e}")




# import smtplib
# import ssl
# from email.message import EmailMessage

# def send_test_email():
#     try:
#         msg = EmailMessage()
#         msg.set_content("Hello! This is a test email from Django 📬")
#         msg['Subject'] = "Test Email"
#         msg['From'] = "sugurohith2002@gmail.com"
#         msg['To'] = "sugurohith2002@gmail.com"

#         context = ssl._create_unverified_context()

#         with smtplib.SMTP("smtp.gmail.com", 587) as server:
#             server.ehlo()
#             server.starttls(context=context)  # Skip cert verification
#             server.login("sugurohith2002@gmail.com", "bvxsvaaqsggsiwvg")
#             server.send_message(msg)

#         print("✅ Test email sent successfully.")

#     except Exception as e:
#         print(f"❌ Email sending failed: {e}")





# python manage.py shell
# >>> from courses.utils import send_test_email
# >>> send_test_email()

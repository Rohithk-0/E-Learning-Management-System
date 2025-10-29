from django.contrib import admin
from .models import Quiz, Question, Choice, QuizAttempt

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2

class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or getattr(request.user, 'is_manager', False):
            return qs
        elif getattr(request.user, 'is_trainer', False):
            return qs.filter(video__course__trainer__user=request.user)
        return qs.none()  # hide for students/others

from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path
import csv, io

from .models import Quiz, Question, Choice
from .admin_forms import CSVUploadForm

class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'video', 'duration', 'max_attempts']
    change_list_template = "admin/quiz_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-quiz-csv/', self.admin_site.admin_view(self.import_csv))
        ]
        return custom_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            form = CSVUploadForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = io.TextIOWrapper(request.FILES['csv_file'].file, encoding='utf-8')
                reader = csv.DictReader(csv_file)

                for row in reader:
                    quiz_id = row['quiz_id']
                    question_text = row['text']
                    correct_key = row['correct_choice']  # like "option_b"

                    quiz = Quiz.objects.get(id=quiz_id)
                    question = Question.objects.create(quiz=quiz, text=question_text)

                    for key in ['option_a', 'option_b', 'option_c', 'option_d']:
                        Choice.objects.create(
                            question=question,
                            text=row[key],
                            is_correct=(key == correct_key)
                        )

                self.message_user(request, "CSV imported successfully.")
                return redirect("..")
        else:
            form = CSVUploadForm()

        return render(request, "admin/csv_upload.html", {'form': form})


admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(QuizAttempt)

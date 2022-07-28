from django.contrib import admin

# Register your models here.

from .models import Question, Choice, T6

#admin.site.register(Question) # default ordering of fields

class QuestionAdmin(admin.ModelAdmin): 
    fieldsets = [
        (None,               {'fields': ['question_text']}),
        ('Date information', {'fields': ['pub_date']}),
    ]
#     fields = ['pub_date', 'question_text'] # custom ordering of fields
admin.site.register(Question, QuestionAdmin)

    

admin.site.register(Choice)
admin.site.register(T6)


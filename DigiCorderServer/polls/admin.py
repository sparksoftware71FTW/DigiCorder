from django.contrib import admin

# Register your models here.

from .models import Question, Choice, T6

#admin.site.register(Choice) # default ordering/seperate form 
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

#admin.site.register(Question) # default ordering of fields

class QuestionAdmin(admin.ModelAdmin): 
    fieldsets = [
        (None,               {'fields': ['question_text']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline]
    list_display = ('question_text', 'pub_date', 'was_published_recently')
    list_filter = ['pub_date']

#     fields = ['pub_date', 'question_text'] # custom ordering of fields
admin.site.register(Question, QuestionAdmin)
    

admin.site.register(T6)


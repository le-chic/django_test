from django.contrib import admin

from .models import Choice, Question

class ChoiceInline(admin.TabularInline):    # or StackedInline
    model = Choice
    extra = 3                               # choices by default + extra choices every time we come back for editing

class QuestionAdmin(admin.ModelAdmin):

    # Set the order of fields on admin page
    fieldsets = [
        (None,               {'fields': ['question_text']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]

    inlines = [ChoiceInline]

    list_display = ('question_text', 'pub_date', 'was_published_recently', "has_enough_choices")
    list_filter = ['pub_date']

    search_fields = ['question_text']


admin.site.register(Question, QuestionAdmin)

from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Choice, Question

app_name = "testapp"

# ListView : display a list of objects
class IndexView(generic.ListView):
    template_name = f'{app_name}/index.html'
    context_object_name = 'latest_question_list'            # to override the automatically generated context variable

    def get_queryset(self):
        """
        Return the last five published questions.
        Excludes questions set to be published in the future, nor those with 1 or 0 choices.
        """

        # Filter on date
        qset = Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')

        # Filter on number of choices : uses a model method, thus has to be done through list comprehension
        qset = qset.filter(id__in=[question.id for question in qset if question.has_enough_choices()])

        # Return 5 most recent questions
        return qset[:5]


# DetailView : display a detail page for a particular type of object
# Expects the primary key value captured from the URL to be called "pk"
class DetailView(generic.DetailView):
    model = Question
    template_name = f'{app_name}/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet + those with 1 or 0 choices
        """
        qset = Question.objects.filter(pub_date__lte=timezone.now())
        qset = qset.filter(id__in=[question.id for question in qset if question.has_enough_choices()])
        return qset


class ResultsView(generic.DetailView):
    model = Question
    template_name = f'{app_name}/results.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet + those with 1 or 0 choices
        """
        qset = Question.objects.filter(pub_date__lte=timezone.now())
        qset = qset.filter(id__in=[question.id for question in qset if question.has_enough_choices()])
        return qset


def vote(request: HttpRequest, pk: int):
    question = get_object_or_404(Question, pk=pk)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])        # access submitted data
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form
        return render(
            request=request,
            template_name=f'{app_name}/detail.html',
            context={
                'question': question,
                'error_message': "You didn't make a choice.",
            }
        )
    else:
        selected_choice.votes += 1
        selected_choice.save()

        # GOOD WEB DEV PRACTICE
        # Always return an HttpResponseRedirect after successfully dealing with POST data.
        # This prevents data from being posted twice if a user hits the Back button.
        return HttpResponseRedirect(reverse(viewname=f'{app_name}:results', args=(question.id,)))

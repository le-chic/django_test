import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question

app_name = "polls"


def create_question(question_text: str, days: int, without_choices: bool = False):
    """
    Create a question with the given `question_text` and published the given number of `days` offset to now
    (negative for questions published in the past, positive for questions that have yet to be published)
    """
    time = timezone.now() + datetime.timedelta(days=days)
    q = Question.objects.create(question_text=question_text, pub_date=time)

    if not without_choices:
        q.choice_set.create(choice_text='foo', votes=0)
        q.choice_set.create(choice_text='bar', votes=0)

    return q


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions with pub_date in the future
        """
        future_date = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=future_date)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date is older than 1 day
        """
        just_over_one_day_ago = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=just_over_one_day_ago)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date is within the last day
        """
        just_under_one_day_ago = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=just_under_one_day_ago)
        self.assertIs(recent_question.was_published_recently(), True)


class QuestionIndexViewTests(TestCase):

    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed
        """
        response = self.client.get(reverse(f'{app_name}:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_question_without_choices(self):
        """
        If only questions without enough choices, an appropriate message is displayed
        """
        # 0 choices
        create_question(question_text="Question with 0 choices.", days=-30, without_choices=True)
        # 1 choice
        q = create_question(question_text="Question with 1 choice.", days=-30, without_choices=True)
        q.choice_set.create(choice_text='foo', votes=0)

        response = self.client.get(reverse(f'{app_name}:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the index page
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse(f'{app_name}:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on the index page
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse(f'{app_name}:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions are displayed
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse(f'{app_name}:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse(f'{app_name}:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question2, question1],
        )


class QuestionDetailViewTests(TestCase):

    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future returns a 404 not found
        """
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse(f'{app_name}:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past displays the question's text
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse(f'{app_name}:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_question_without_choices(self):
        """
        The detail view of a question without enough choices (<2, 0 here) returns a 404 not found
        """
        question_without_choices = create_question(
            question_text='Question without choices.',
            days=0,
            without_choices=True
        )
        url = reverse(f'{app_name}:detail', args=(question_without_choices.id,))
        question_without_choices.save()
        response = self.client.get(url)
        self.assertIs(question_without_choices.has_enough_choices(), False)
        self.assertEqual(response.status_code, 404)

    def test_question_with_choices(self):
        """
        The detail view of a question with enough choices (>=2, 2 here) displays the question's text
        """
        question_with_choices = create_question(question_text='Question with enough choices.', days=0)
        question_with_choices.save()
        url = reverse(f'{app_name}:detail', args=(question_with_choices.id,))
        response = self.client.get(url)
        self.assertIs(question_with_choices.has_enough_choices(), True)
        self.assertContains(response, question_with_choices.question_text)


class QuestionResultsViewTests(TestCase):

    def test_future_question(self):
        """
        The results view of a question with a pub_date in the future returns a 404 not found
        """
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse(f'{app_name}:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The results view of a question with a pub_date in the past displays the question's results
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse(f'{app_name}:results', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_question_without_choices(self):
        """
        The results view of a question without enough choices (<2, 0 here) returns a 404 not found
        """
        question_without_choices = create_question(
            question_text='Question without choices.',
            days=0,
            without_choices=True
        )
        url = reverse(f'{app_name}:results', args=(question_without_choices.id,))
        question_without_choices.save()
        response = self.client.get(url)
        self.assertIs(question_without_choices.has_enough_choices(), False)
        self.assertEqual(response.status_code, 404)

    def test_question_with_choices(self):
        """
        The results view of a question with enough choices (>=2, 2 here) displays the question's text
        """
        question_with_choices = create_question(question_text='Question with enough choices.', days=0)
        question_with_choices.save()
        url = reverse(f'{app_name}:results', args=(question_with_choices.id,))
        response = self.client.get(url)
        self.assertIs(question_with_choices.has_enough_choices(), True)
        self.assertContains(response, question_with_choices.question_text)

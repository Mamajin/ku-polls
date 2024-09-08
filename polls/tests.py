import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question, Choice, Vote


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_is_published_with_future_pub_date(self):
        """
        is_published() should return False for questions whose pub_date
        is in the future.
        """
        future_time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=future_time)
        self.assertIs(future_question.is_published(), False)

    def test_is_published_with_default_pub_date(self):
        """
        is_published() should return True for questions whose pub_date
        is now (default).
        """
        question = Question()
        self.assertIs(question.is_published(), True)

    def test_is_published_with_past_pub_date(self):
        """
        is_published() should return True for questions whose pub_date
        is in the past.
        """
        past_time = timezone.now() - datetime.timedelta(days=1)
        past_question = Question(pub_date=past_time)
        self.assertIs(past_question.is_published(), True)

    def test_can_vote_within_date_range(self):
        """
        can_vote() should return True for questions whose current date is
        between pub_date and end_date.
        """
        now = timezone.now()
        question = Question(pub_date=now - datetime.timedelta(days=1),
                            end_date=now + datetime.timedelta(days=1))
        self.assertIs(question.can_vote(), True)

    def test_can_vote_with_end_date_in_past(self):
        """
        can_vote() should return False if the end_date is in the past.
        """
        now = timezone.now()
        question = Question(pub_date=now - datetime.timedelta(days=2),
                            end_date=now - datetime.timedelta(days=1))
        self.assertIs(question.can_vote(), False)

    def test_can_vote_without_end_date(self):
        """
        can_vote() should return True if there is no end_date and the current
        date is after pub_date.
        """
        now = timezone.now()
        question = Question(pub_date=now - datetime.timedelta(days=1),
                            end_date=None)
        self.assertIs(question.can_vote(), True)


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question2, question1],
        )


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text="Past Question.", days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class ChoiceModelTests(TestCase):
    def test_choice_str(self):
        """
        The __str__() method of the Choice model should return the choice_text.
        """
        question = create_question(question_text="Test question.", days=-1)
        choice = Choice.objects.create(question=question,
                                       choice_text="Test choice.")
        self.assertEqual(str(choice), "Test choice")

    def test_choice_votes_count(self):
        """
        The votes property should correctly count the number of votes for a choice.
        """
        question = create_question(question_text="Test question.", days=-1)
        choice = Choice.objects.create(question=question,
                                       choice_text="Test choice.")
        user1 = User.objects.create_user(username='user1', password='password')
        user2 = User.objects.create_user(username='user2', password='password')

        Vote.objects.create(choice=choice, user=user1)
        Vote.objects.create(choice=choice, user=user2)

        self.assertEqual(choice.votes, 2)


class VoteModelTests(TestCase):
    def test_vote_creation(self):
        """
        Test that a vote can be created and is associated with the correct choice and user.
        """
        question = create_question(question_text="Test question.", days=-1)
        choice = Choice.objects.create(question=question,
                                       choice_text="Test choice.")
        user = User.objects.create_user(username='user', password='password')

        vote = Vote.objects.create(choice=choice, user=user)

        self.assertEqual(vote.choice, choice)
        self.assertEqual(vote.user, user)

    def test_multiple_votes_by_same_user(self):
        """
        A user should not be able to vote multiple times for the same choice in a poll.
        """
        question = create_question(question_text="Test question.", days=-1)
        choice = Choice.objects.create(question=question,
                                       choice_text="Test choice.")
        user = User.objects.create_user(username='user', password='password')

        Vote.objects.create(choice=choice, user=user)
        with self.assertRaises(Exception):
            Vote.objects.create(choice=choice, user=user)

    def test_votes_for_multiple_choices(self):
        """
        A user should be able to vote for different choices in different polls.
        """
        question1 = create_question(question_text="Test question 1.", days=-1)
        choice1 = Choice.objects.create(question=question1,
                                        choice_text="Test choice 1.")

        question2 = create_question(question_text="Test question 2.", days=-1)
        choice2 = Choice.objects.create(question=question2,
                                        choice_text="Test choice 2.")

        user = User.objects.create_user(username='user', password='password')

        vote1 = Vote.objects.create(choice=choice1, user=user)
        vote2 = Vote.objects.create(choice=choice2, user=user)

        self.assertEqual(vote1.choice, choice1)
        self.assertEqual(vote2.choice, choice2)

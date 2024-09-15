import datetime
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from polls.models import Question, Choice, Vote

def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


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

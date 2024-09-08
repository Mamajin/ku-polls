import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


# Create your models here.


class Question(models.Model):
    """
    The Question model represents a poll question in the system. It contains
    fields for ‘question_text’, ‘pub_date’ (date published), and ‘end_date’.
    The was_published_recently method checks if the question has been recently
    published, while is_published returns True if the current date/time is on
    or after the publication date. The can_vote method determines if voting is
    allowed based on the current date/time in relation to the publication and
    end dates.
    """
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    end_date = models.DateTimeField('end date', null=True, blank=True)

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def is_published(self):
        """
        Return True if current date/time is on or after question's
        publication date.
        """
        return timezone.localtime() >= self.pub_date

    def can_vote(self):
        """
        Returns True if voting is allowed for this question.
        Voting is allowed if the current date/time is between pub_date
        and end_date. If end_date is None, voting is allowed anytime after
        pub_date.
        """
        now = timezone.localtime()
        if self.end_date:
            return self.pub_date <= now <= self.end_date
        return now >= self.pub_date


class Choice(models.Model):
    """
    The Choice model represents a choice within a poll. It contains fields for
    ‘question’ (a foreign key relationship with the Question model),
    ‘choice_text’, and ‘votes’.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    # votes = models.IntegerField(default=0)

    @property
    def votes(self):
        """return the votes for this choice"""
        return self.vote_set.count()

    def __str__(self):
        return self.choice_text


class Vote(models.Model):
    """
    A vote by a user for a choice in a poll.
    """

    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


def get_client_ip(request):
    """Get the visitor’s IP address using request headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

from django.contrib import messages
from django.db.models import F
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.utils import timezone
from .models import Choice, Question

# Create your views here.


class IndexView(generic.ListView):
    """
    The IndexView class is a generic ListView that displays a list of the
    latest five published questions. It uses the “polls/index.html” template
    to render the index page.
    """
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by(
            "-pub_date")[
               :5
               ]


class DetailView(generic.DetailView):
    """
    The DetailView class is a generic DetailView that allows users to view
    details of individual questions. It checks if the question is published
    and if voting is allowed before rendering the “polls/detail.html” template
    with the relevant data.
    """
    model = Question
    template_name = "polls/detail.html"

    def get(self, request, *args, **kwargs):
        question = self.get_object()
        if not question.is_published():
            messages.error(request, "This poll is not yet published.")
            return redirect('polls:index')
        if not question.can_vote():
            messages.error(request, "Voting is not allowed for this poll.")
            return redirect('polls:index')
        return super().get(request, *args, **kwargs)


class ResultsView(generic.DetailView):
    """
    The ResultsView class is another generic DetailView, displaying the
    results of a specific Question instance. The template used here is
    “polls/results.html”.
    """
    model = Question
    template_name = "polls/results.html"


def vote(request, question_id):
    """
    The vote function handles voting on a particular question. It first fetches
     the question based on the provided ID. If no valid choice is submitted in
     the POST request, it returns an error message to the user and redisplay
     the detail page. Otherwise, it increments the vote count for that chosen
     option, saves it, and redirects the user to the results page of the
     questioned they just voted on.
    """
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
    return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))

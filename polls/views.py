from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.utils import timezone
from .models import Choice, Question, Vote
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
import logging


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
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")


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
        # First, retrieve the object by calling the parent class's get method
        self.object = self.get_object()
        question = self.object  # Now, 'question' is the retrieved object

        # Check if the poll is published
        if not question.is_published():
            messages.error(request, "This poll is not yet published.")
            return redirect('polls:index')

        # Check if voting is allowed for the poll
        if not question.can_vote():
            messages.error(request, "Voting is not allowed for this poll.")
            return redirect('polls:index')

        # Attempt to retrieve the user's previous vote if authenticated
        user_vote = None
        if request.user.is_authenticated:
            try:
                user_vote = Vote.objects.get(user=request.user, choice__question=question).choice.id
            except Vote.DoesNotExist:
                user_vote = None

        # Call super().get_context_data() to properly initialize context
        context = self.get_context_data(object=question, user_vote=user_vote)
        return self.render_to_response(context)


logger = logging.getLogger('polls')


class ResultsView(generic.DetailView):
    """
    The ResultsView class is another generic DetailView, displaying the
    results of a specific Question instance. The template used here is
    “polls/results.html”.
    """
    model = Question
    template_name = "polls/results.html"


@login_required
def vote(request, question_id):
    """
    The vote function handles voting on a particular question. It first fetches
    the question based on the provided ID. If no valid choice is submitted in
    the POST request, it returns an error message to the user and redisplays
    the detail page. Otherwise, it increments the vote count for that chosen
    option, saves it, and redirects the user to the results page of the
    question they just voted on.
    """
    question = get_object_or_404(Question, pk=question_id)

    if not question.can_vote():
        logger.warning(f"User {request.user.username} attempted to vote in a closed poll {question_id}")
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You cannot vote in this poll."
        })

    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        logger.warning(f"User {request.user.username} failed to select a choice for question {question_id}")
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )

    this_user = request.user
    try:
        # Check if the user already has a vote
        vote = Vote.objects.get(user=this_user, choice__question=question)
        # If they do, update their vote
        vote.choice = selected_choice
        vote.save()
        logger.info(f"User {this_user.username} changed their vote to choice {selected_choice.choice_text} for question {question_id}")
        messages.success(request, f"Your vote was updated to '{selected_choice.choice_text}'")
    except Vote.DoesNotExist:
        # If they don't have a vote yet, create a new one
        vote = Vote.objects.create(user=this_user, choice=selected_choice)
        logger.info(f"User {this_user.username} voted for choice {selected_choice.choice_text} for question {question_id}")
        messages.success(request, f"You voted for '{selected_choice.choice_text}'")

    # Redirect to the results page
    return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))


def login(request):
    """
    Handle user login.
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            ip_addr = request.META.get('REMOTE_ADDR')
            logger.info(f"User {username} logged in from {ip_addr}")
            return redirect('polls:index')
        else:
            ip_addr = request.META.get('REMOTE_ADDR')
            logger.warning(f"Failed login attempt for {username} from {ip_addr}")
    return render(request, 'login.html')


def logout(request):
    """
    Handle user logout.
    """
    ip_addr = request.META.get('REMOTE_ADDR')
    logger.info(f"User {request.user.username} logged out from {ip_addr}")
    auth_logout(request)
    return redirect('polls:index')

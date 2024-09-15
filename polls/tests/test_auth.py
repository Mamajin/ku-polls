from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from mysite import settings
from polls.models import Question, Choice


class UserAuthenticationTests(TestCase):

    def setUp(self):
        # Calling superclass setUp to initialize the test client and database
        super().setUp()
        self.username = "sampleuser"
        self.password = "SecurePass!"
        self.test_user = User.objects.create_user(
            username=self.username,
            password=self.password,
            email="sampleuser@example.com"
        )
        self.test_user.first_name = "Sample"
        self.test_user.save()
        # Creating a sample poll question for voting test cases
        question_instance = Question.objects.create(question_text="Sample Poll Question")
        question_instance.save()
        # Adding some choices for the poll
        for i in range(1, 4):
            option = Choice(choice_text=f"Option {i}", question=question_instance)
            option.save()
        self.poll_question = question_instance

    def test_user_logout(self):
        """A logged-in user should be able to log out through the logout URL.

        As an authenticated user,
        when I access /accounts/logout/,
        I should be logged out
        and then redirected to the login page.
        """
        logout_url = reverse("logout")
        # Authenticate the user using the client login method
        self.assertTrue(
            self.client.login(username=self.username, password=self.password)
        )
        # Trigger the logout by sending a POST request to the logout URL
        response = self.client.post(logout_url, {})
        self.assertEqual(302, response.status_code)

        # Verifying redirection to the expected page after logging out
        self.assertRedirects(response, reverse(settings.LOGOUT_REDIRECT_URL))

    def test_login_view_access(self):
        """A user should be able to access the login page and log in successfully."""
        login_url = reverse("login")
        # Access the login page
        response = self.client.get(login_url)
        self.assertEqual(200, response.status_code)
        # Log in by sending a POST request with valid credentials
        form_data = {"username": "sampleuser",
                     "password": "SecurePass!"
                     }
        response = self.client.post(login_url, form_data)
        # Check if login is successful and the user is redirected
        self.assertEqual(302, response.status_code)
        # Verify that the user is redirected to the index page after login
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))

    def test_voting_requires_authentication(self):
        """Unauthenticated users should be redirected to the login page when attempting to vote.

        As an unauthenticated user,
        if I try to submit a vote for a question,
        I should be redirected to the login page
        or receive a 403 Forbidden response.
        """
        vote_url = reverse('polls:vote', args=[self.poll_question.id])

        # Select the first choice for voting
        selected_choice = self.poll_question.choice_set.first()
        form_data = {"choice": f"{selected_choice.id}"}
        response = self.client.post(vote_url, form_data)
        # Ensure redirection to the login page if not authenticated
        self.assertEqual(response.status_code, 302)
        # Verifying redirection to the login page with the next parameter
        login_redirect_url = f"{reverse('login')}?next={vote_url}"
        self.assertRedirects(response, login_redirect_url)

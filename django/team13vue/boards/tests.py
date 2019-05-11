from django.test import TestCase
from django.urls import reverse
from django.urls import resolve
from django.contrib.auth.models import User
from boards.models import Board, Topic, Post
from boards.views import home, board_topics, new_topic

from .forms import NewTopicForm
class Hometest(TestCase):
    def setUp(self):
        self.board = Board.objects.create(
            name="Django", description="Firts Board Created")
        self.url = reverse('home')
        self.response = self.client.get(self.url)

    def test_home_view_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_home_url_resolves_home_view(self):
        view = resolve('/')
        self.assertEquals(view.func, home)

    def test_home_view_contains_link_to_topics_url(self):
        board_topics_url = reverse('board_topics', kwargs={
                                   'boardid': self.board.pk})
        self.assertContains(
            self.response, 'href="{0}"'.format(board_topics_url))


class TestBoardTopics(TestCase):

    def setUp(self):
        self.board = Board.objects.create(
            name="Django", description="Firts Board Created")
        self.url = reverse('board_topics', kwargs={'boardid': 1})
        self.response = self.client.get(self.url)

    def test_boardtopics_view_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_board_topics_view_contains_navigation_links(self):
        board_topics_url = reverse('board_topics', kwargs={'boardid': 1})
        homepage_url = reverse('home')
        new_topic_url = reverse('new_topic', kwargs={'boardid': 1})

        response = self.client.get(board_topics_url)

        self.assertContains(response, 'href="{0}"'.format(homepage_url))
        self.assertContains(response, 'href="{0}"'.format(new_topic_url))

    def test_boardtopics_not_found_view_status_code(self):
        url = reverse('board_topics', kwargs={'boardid': 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_boardstopics_url_resolves_boardstopics_view(self):
        view = resolve('/boards/1/')
        self.assertEqual(view.func, board_topics)


class TestNewTopic(TestCase):
    def setUp(self):

        self.board = Board.objects.create(
            name="Django", description="Firts Board Created")
        self.url = reverse('new_topic', kwargs={'boardid': 1})
        self.response = self.client.get(self.url)

    def test_newtopic_view_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_newtopic_view_contains_url_to_home_view(self):
        homepage_url = reverse('home')
        self.assertContains(self.response, 'href="{0}"'.format(homepage_url))

    def test_newtopic_view_contains_url_to_boardtopics_view(self):
        board_topics_url = reverse('board_topics', kwargs={
                                   'boardid': self.board.pk})
        self.assertContains(
            self.response, 'href="{0}"'.format(board_topics_url))

    def test_newtopic_not_found_view_status_code(self):
        url = reverse('new_topic', kwargs={'boardid': 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_newtopic_url_resolves_newtopic_view(self):
        view = resolve('/boards/1/new')
        self.assertEqual(view.func, new_topic)


class NewTopicTests(TestCase):
    def setUp(self):
        Board.objects.create(name='Django', description='Django board.')
        # <- included this line here
        User.objects.create_user(
            username='john', email='john@doe.com', password='123')

    # ...

    def test_csrf(self):
        url = reverse('new_topic', kwargs={'boardid': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_new_topic_valid_post_data(self):
        url = reverse('new_topic', kwargs={'boardid': 1})
        data = {
            'title': 'Test title',
            'message': 'Lorem ipsum dolor sit amet'
        }
        response = self.client.post(url, data)
        self.assertTrue(Topic.objects.exists())
        self.assertTrue(Post.objects.exists())

    def test_contains_form(self):  # <- new test
        url = reverse('new_topic', kwargs={'boardid': 1})
        response = self.client.get(url)
        form = response.context.get('form')
        self.assertIsInstance(form, NewTopicForm)

    def test_new_topic_invalid_post_data(self):  # <- updated this one
        '''
        Invalid post data should not redirect
        The expected behavior is to show the form again with validation errors
        '''
        url = reverse('new_topic', kwargs={'boardid': 1})
        response = self.client.post(url, {})
        form = response.context.get('form')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)

    def test_new_topic_invalid_post_data_empty_fields(self):
        '''
        Invalid post data should not redirect
        The expected behavior is to show the form again with validation errors
        '''
        url = reverse('new_topic', kwargs={'boardid': 1})
        data = {
            'title': '',
            'message': ''
        }
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(Topic.objects.exists())
        self.assertFalse(Post.objects.exists())
# Create your tests here.
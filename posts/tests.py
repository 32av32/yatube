from yatube import settings
from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Group, Post


class TestPost(TestCase):
    def setUp(self):
        self.client = Client()

        group = Group.objects.create(title='test_text', slug='test_group', description='test_group')
        group.save()
        self.group_slug = group.slug
        self.group_id = group.pk

        self.user = User.objects.create(username='testuser', email='test@email.com')
        self.user.set_password('12345')
        self.user.save()

        self.auth_client = Client()
        self.auth_client.login(username='testuser', password='12345')

    def test_index_available(self):
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200, msg='Index unavailable')

    def test_group_post_available(self):
        response = self.client.get(f'/group/{self.group_slug}/')
        self.assertEquals(response.status_code, 200, msg='Group unavailable')

    def test_group_incorrect(self):
        response = self.client.get('/group/non-exist-group/')
        self.assertEquals(response.status_code, 404, 'Status code must be 404 for Non-Exist-Group page')

    def test_nongroup(self):
        response = self.client.get('/group/')
        self.assertEquals(response.status_code, 404, 'Status code must be 404 for Non-Group page')

    def test_redirect_guest_from_new(self):
        response = self.client.get('/new/')
        self.assertRedirects(response=response, expected_url='/auth/login/?next=/new/', status_code=302,
                             target_status_code=200, fetch_redirect_response=True,
                             msg_prefix='Guest must be redirected to login page')
        
    def test_available_new_for_auth_user(self):
        response = self.auth_client.get('/new/')
        self.assertEquals(response.status_code, 200, msg='page new unavailable for authorized user')

    def test_valid_form_new(self):
        self.auth_client.post('/new/', {'text': 'test_text', 'group': self.group_id})
        post = Post.objects.filter(text='test_text', group=self.group_id)
        self.assertTrue(post.exists(), msg='Post not created')

    def test_invalid_form_new(self):
        response = self.auth_client.post('/new/', data={'text': ''})
        self.assertFormError(response, form='form', field='text', errors=['Обязательное поле.'])

    def test_create_profile(self):
        self.client.post('auth/signup/',
                         {'username': 'testuser', 'password': '12345', 'email': 'test@email.com'})
        response = self.client.get('/testuser/')
        self.assertEqual(response.status_code, 200, msg='Did not created profile page after registration')

    def test_existence_created_post(self):
        self.auth_client.post(f'/new/', {'text': 'test_text', 'group': self.group_id, 'author': self.user})
        response = self.client.get('/')
        self.assertContains(response, 'test_text', msg_prefix='Created post do not existence in main page')
        response = self.client.get(f'/{self.user.username}/')
        self.assertContains(response, 'test_text', msg_prefix='Created post do not existence in profile page')
        response = self.client.get(f'/{self.user.username}/{1}/')
        self.assertContains(response, 'test_text', msg_prefix='Created post do not existence in post page')

    def test_post_edit_auth(self):
        self.auth_client.post('/new/', {'text': 'test_text', 'group': self.group_id, 'author': self.user})
        self.auth_client.post(f'/{self.user.username}/{1}/edit/', {'text': 'new_text'})
        response = self.client.get('/')
        self.assertContains(response, 'new_text', msg_prefix='Edited text do not existence in main page')
        response = self.client.get(f'/{self.user.username}/')
        self.assertContains(response, 'new_text', msg_prefix='Edited text do not existence in profile page')
        response = self.client.get(f'/{self.user.username}/{1}/')
        self.assertContains(response, 'new_text', msg_prefix='Edited text do not existence in post page')

    def test_post_edit_guest(self):
        response = self.client.get(f'/{self.user.username}/{1}/edit/')
        self.assertRedirects(response=response, expected_url=f'/auth/login/?next=/{self.user.username}/{1}/edit/',
                             status_code=302, target_status_code=200, fetch_redirect_response=True,
                             msg_prefix='Guest must be redirected to login page')
        self.client.post(f'/{self.user.username}/{1}/edit/', {'text': 'new_text'})
        self.assertRedirects(response=response, expected_url=f'/auth/login/?next=/{self.user.username}/{1}/edit/',
                             status_code=302, target_status_code=200, fetch_redirect_response=True,
                             msg_prefix='Guest must be redirected to login page')

    def test_page_not_found(self):
        response = self.client.get('/none_exist_page/')
        self.assertEquals(response.status_code, 404, msg='response do not return 404 status code')
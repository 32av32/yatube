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

        user = User.objects.create(username='testuser', email='test@email.com')
        user.set_password('12345')
        user.save()

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
        data = {
            'text': 'test_text',
            'group': self.group_id
        }
        self.auth_client.post('/new/', data=data)
        post = Post.objects.filter(text=data['text'], group=data['group'])
        self.assertTrue(post.exists(), msg='Post not created')

    def test_invalid_form_new(self):
        response = self.auth_client.post('/new/', data={'text': ''})
        self.assertFormError(response, form='form', field='text', errors=['Обязательное поле.'])

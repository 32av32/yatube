import io

from PIL import Image
from django.core.files.base import ContentFile
from django.urls import reverse
from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from .models import Group, Post
from tempfile import TemporaryDirectory
from django.core.cache import cache


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

    def test_get_index(self):
        response = self.client.get(reverse('index'))
        self.assertEquals(response.status_code, 200)

    def test_get_group(self):
        response = self.client.get(reverse('group', kwargs={'slug': self.group_slug}))
        self.assertEquals(response.status_code, 200)

    def test_group_nonexist(self):
        response = self.client.get('/group/non-exist-group/')
        self.assertEquals(response.status_code, 404)

    def test_nongroup(self):
        response = self.client.get('/group/')
        self.assertEquals(response.status_code, 404)

    def test_redirect_guest_from_new(self):
        response = self.client.get(reverse('new_post'))
        self.assertRedirects(response=response, expected_url='/auth/login/?next=/new/', status_code=302,
                             target_status_code=200, fetch_redirect_response=True)

    def test_get_new_for_auth_user(self):
        response = self.auth_client.get(reverse('new_post'))
        self.assertEquals(response.status_code, 200)

    def test_valid_form_new(self):
        data = {'text': 'test_text', 'group': self.group_id}
        self.auth_client.post(reverse('new_post'), data=data)
        post = Post.objects.filter(text='test_text', group=self.group_id)
        self.assertTrue(post.exists(), msg='Post not created')

    def test_invalid_form_new(self):
        response = self.auth_client.post(reverse('new_post'), data={'text': ''})
        self.assertFormError(response, form='form', field='text', errors=['Обязательное поле.'])

    def test_create_profile(self):
        data = {'username': 'testuser', 'password': '12345', 'email': 'test@email.com'}
        self.client.post(reverse('signup'), data=data)
        response = self.client.get(reverse('profile', kwargs={'username': self.user.username}))
        self.assertEqual(response.status_code, 200)

    def test_existence_created_post(self):
        data = {'text': 'test_text', 'group': self.group_id, 'author': self.user}
        self.auth_client.post(reverse('new_post'), data=data)

        urls = [
            reverse('index'),
            reverse('group', kwargs={'slug': self.group_slug}),
            reverse('profile', kwargs={'username': self.user.username}),
            reverse('post', kwargs={'username': self.user.username, 'post_id': 1})
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertContains(response, 'test_text', msg_prefix=f'Created post do not exist in url: {url}')

    def test_post_edit_auth(self):
        data = {'text': 'test_text', 'group': self.group_id, 'author': self.user}
        new_data = {'text': 'new_text', 'group': self.group_id}
        self.auth_client.post(reverse('new_post'), data=data)
        self.auth_client.post(reverse('post_edit',
                                      kwargs={'username': self.user.username, 'post_id': 1}), data=new_data)

        urls = [
            reverse('index'),
            reverse('group', kwargs={'slug': self.group_slug}),
            reverse('profile', kwargs={'username': self.user.username}),
            reverse('post', kwargs={'username': self.user.username, 'post_id': 1})
        ]

        for url in urls:
            cache.clear()
            response = self.client.get(url)
            self.assertContains(response, 'new_text', msg_prefix=f'Edited text do not exist in url: {url}')

    def test_post_edit_guest(self):
        response = self.client.get(reverse('post_edit',
                                           kwargs={'username': self.user.username, 'post_id': 1}))
        self.assertRedirects(response=response, expected_url=f'/auth/login/',
                             status_code=302, target_status_code=200, fetch_redirect_response=True)

        self.client.post(reverse('post_edit',
                                 kwargs={'username': self.user.username, 'post_id': 1}), data={'text': 'new_text'})
        self.assertRedirects(response=response, expected_url=reverse('login'),
                             status_code=302, target_status_code=200, fetch_redirect_response=True)

    def test_page_not_found(self):
        response = self.client.get('/none_exist_page/')
        self.assertEquals(response.status_code, 404)

    def test_display_image(self):
        cache.clear()
        with TemporaryDirectory() as temp_directory:
            with override_settings(MEDIA_ROOT=temp_directory):
                bytes_image = io.BytesIO()
                im = Image.new('RGB', size=(1000, 1000), color=(255, 0, 0, 0))
                im.save(bytes_image, format='jpeg')
                bytes_image.seek(0)
                image = ContentFile(bytes_image.read(), 'test.jpeg')

                data = {'text': 'text', 'group': self.group_id, 'image': image}
                self.auth_client.post(reverse('new_post'), data=data)

                urls = [
                    reverse('index'),
                    reverse('group', kwargs={'slug': self.group_slug}),
                    reverse('profile', kwargs={'username': self.user.username}),
                    reverse('post', kwargs={'username': self.user.username, 'post_id': 1})
                ]

                for url in urls:
                    response = self.client.get(url)
                    self.assertContains(response, '<img', msg_prefix=f'Image do not uploaded to url: {url}')

    def test_cache(self):
        self.auth_client.get('/')
        data = {'text': 'test_text', 'group': self.group_id, 'author': self.user}
        self.auth_client.post(reverse('new_post'), data=data)
        response = self.auth_client.get('/')
        self.assertNotContains(response, 'test_text', msg_prefix='Page do not must contain new post')

    def test_follow_auth(self):
        following = User.objects.create(username='author', password='12345', email='example@ex.com')
        following.save()
        urls = [
            reverse('profile_follow', kwargs={'username': following.username}),
            reverse('profile_unfollow', kwargs={'username': following.username}),
        ]
        for url in urls:
            response = self.auth_client.get(url)
            self.assertRedirects(response=response,
                                 expected_url=reverse('profile', kwargs={'username': following.username}), status_code=302,
                                 target_status_code=200, fetch_redirect_response=True)

    def test_post_comment(self):
        data = {'text': 'test_text', 'group': self.group_id, 'author': self.user}
        self.auth_client.post(reverse('new_post'), data=data)
        self.auth_client.post(
            reverse('add_comment',
                    kwargs={'username': self.user.username,
                            'post_id': Post.objects.all().first().pk}),
            data={'text': 'test_comment'})
        response = self.auth_client.get(reverse('post', kwargs={'username': self.user.username,
                                                                'post_id': Post.objects.all().first().pk}))
        self.assertContains(response, 'test_comment')

    def test_following_new_post(self):
        following = User.objects.create(username='author', password='12345', email='example@ex.com')
        following.save()
        visiter = User.objects.create(username='visiter', password='12345', email='example@ex.com')
        visiter.save()

        self.auth_client.get(reverse('profile_follow', kwargs={'username': following.username}))

        new_post = Post.objects.create(text='following_text', author=following)
        new_post.save()

        response = self.auth_client.get(reverse('follow_index'))
        self.assertContains(response, 'following_text')

        visiter_client = Client()
        visiter_client.force_login(visiter)
        response = visiter_client.get(reverse('follow_index'))
        self.assertNotContains(response, 'following_text')

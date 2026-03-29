"""
Comprehensive tests for the blog app.
Tests CRUD operations and views.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from .models import BlogPage
from .forms import BlogPageForm


class BlogPageModelTests(TestCase):
    """Tests for BlogPage model."""

    def test_create_blog_page(self):
        blog = BlogPage.objects.create(
            title="AI Art Revolution",
            content="<p>AI is changing everything...</p>",
        )
        self.assertEqual(str(blog), "AI Art Revolution")
        self.assertIsNotNone(blog.created_at)


class BlogFormTests(TestCase):
    """Tests for BlogPageForm."""

    def test_form_valid(self):
        form = BlogPageForm(data={
            'title': 'New Blog Post',
            'content': '<p>Great content here</p>',
        })
        self.assertTrue(form.is_valid())

    def test_form_missing_title(self):
        form = BlogPageForm(data={'content': '<p>Content only</p>'})
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)


class BlogViewTests(TestCase):
    """Tests for blog views."""

    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser('admin', 'admin@test.com', 'adminpass')
        self.user = User.objects.create_user('reader', 'reader@test.com', 'readerpass')
        self.blog = BlogPage.objects.create(
            title="Test Blog Post",
            content="<p>Interesting content</p>",
        )
        self.blog_list_url = reverse('blog')
        self.create_url = reverse('create_blog_page')

    def test_blog_list_view(self):
        response = self.client.get(self.blog_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Blog Post')

    def test_blog_list_pagination(self):
        # Create 5 blog posts
        for i in range(5):
            BlogPage.objects.create(title=f'Blog {i}', content='<p>Content</p>')
        response = self.client.get(self.blog_list_url)
        # Should paginate at 3 per page
        self.assertLessEqual(len(response.context['page_obj']), 3)

    def test_blog_detail_view(self):
        url = reverse('blog_page_detail', args=[self.blog.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Blog Post')

    def test_blog_detail_404(self):
        url = reverse('blog_page_detail', args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_create_blog_requires_login(self):
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 302)

    def test_create_blog_requires_superuser(self):
        self.client.login(username='reader', password='readerpass')
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 302)

    def test_create_blog_get_as_superuser(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)

    def test_create_blog_post_valid(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(self.create_url, data={
            'title': 'New Blog Post',
            'content': '<p>New content</p>',
        })
        self.assertEqual(BlogPage.objects.filter(title='New Blog Post').count(), 1)
        self.assertRedirects(response, reverse('blog'))

    def test_create_blog_post_invalid(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(self.create_url, data={})
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_valid())

    def test_edit_blog_get(self):
        self.client.login(username='admin', password='adminpass')
        url = reverse('edit_blog_page', args=[self.blog.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Blog Post')

    def test_edit_blog_post(self):
        self.client.login(username='admin', password='adminpass')
        url = reverse('edit_blog_page', args=[self.blog.pk])
        response = self.client.post(url, data={
            'title': 'Updated Title',
            'content': '<p>Updated</p>',
        })
        self.blog.refresh_from_db()
        self.assertEqual(self.blog.title, 'Updated Title')
        self.assertRedirects(response, reverse('blog_page_detail', args=[self.blog.pk]))

    def test_delete_blog_correct_username(self):
        self.client.login(username='admin', password='adminpass')
        url = reverse('delete_blog_page', args=[self.blog.pk])
        response = self.client.post(url, data={'username': 'admin'})
        self.assertEqual(BlogPage.objects.filter(pk=self.blog.pk).count(), 0)
        self.assertRedirects(response, reverse('blog'))

    def test_delete_blog_wrong_username(self):
        self.client.login(username='admin', password='adminpass')
        url = reverse('delete_blog_page', args=[self.blog.pk])
        response = self.client.post(url, data={'username': 'wrong'})
        self.assertEqual(BlogPage.objects.filter(pk=self.blog.pk).count(), 1)

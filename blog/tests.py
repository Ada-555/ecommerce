"""
Comprehensive tests for the blog app.
Tests CRUD operations and views.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from .models import BlogPage, BlogSubscriber
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
            is_published=True,
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
            BlogPage.objects.create(title=f'Blog {i}', content='<p>Content</p>', is_published=True)
        response = self.client.get(self.blog_list_url)
        # Should paginate at 6 per page
        self.assertLessEqual(len(response.context['page_obj']), 6)

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


class BlogPublicViewTests(TestCase):
    """Tests for public blog views (blog_index, blog_post, subscribe)."""

    def setUp(self):
        self.client = Client()
        # Published post
        self.published = BlogPage.objects.create(
            title="Published Post",
            content="<p>Great published content here.</p>",
            is_published=True,
            store='orderimo',
        )
        # Unpublished post
        self.unpublished = BlogPage.objects.create(
            title="Draft Post",
            content="<p>Not ready yet.</p>",
            is_published=False,
            store='orderimo',
        )

    def test_blog_index_shows_only_published(self):
        """blog_index should only list published posts."""
        response = self.client.get(reverse('blog_index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Published Post')
        self.assertNotContains(response, 'Draft Post')

    def test_blog_index_pagination(self):
        """blog_index paginates at 6 posts per page."""
        for i in range(7):
            BlogPage.objects.create(
                title=f"Post {i}",
                content=f"<p>Content {i}</p>",
                is_published=True,
                store='orderimo',
            )
        response = self.client.get(reverse('blog_index'))
        # Only 6 posts per page
        self.assertLessEqual(len(response.context['page_obj']), 6)

    def test_blog_post_shows_published_post(self):
        """blog_post view shows a published post by slug."""
        url = reverse('blog_post', kwargs={'slug': self.published.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Published Post')
        self.assertContains(response, self.published.content)

    def test_blog_post_404_for_unpublished(self):
        """blog_post view returns 404 for unpublished posts."""
        url = reverse('blog_post', kwargs={'slug': self.unpublished.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_subscribe_valid_email(self):
        """subscribe view returns success JSON for valid email."""
        response = self.client.post(
            reverse('blog_subscribe'),
            {'email': 'newsubscriber@example.com'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])

    def test_subscribe_duplicate_email(self):
        """subscribe view handles duplicate email gracefully."""
        BlogSubscriber.objects.create(email='duplicate@example.com', store='orderimo')
        response = self.client.post(
            reverse('blog_subscribe'),
            {'email': 'duplicate@example.com'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])

    def test_subscribe_get_method_not_allowed(self):
        """subscribe view returns 405 for non-POST requests."""
        response = self.client.get(reverse('blog_subscribe'))
        self.assertEqual(response.status_code, 405)

    def test_blog_post_reading_time(self):
        """BlogPage.reading_time() returns a string with minutes."""
        rt = self.published.reading_time()
        self.assertIn('min read', rt)

    def test_blog_post_excerpt(self):
        """BlogPage.excerpt returns plain text truncated to ~30 words."""
        excerpt = self.published.excerpt
        self.assertIsInstance(excerpt, str)
        self.assertLessEqual(len(excerpt), 200)

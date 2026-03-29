import re
from django.db import models
from ckeditor.fields import RichTextField


class BlogPage(models.Model):
    """ Model for blog page """
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    content = RichTextField(blank=True, null=True)
    image = models.ImageField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    store = models.CharField(max_length=50, blank=True, default='orderimo')
    is_published = models.BooleanField(default=False)
    newsletter_sent_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = re.sub(r'[^a-z0-9-]', '', self.title.lower().replace(' ', '-').replace("'", ''))[:50]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('blog_post', kwargs={'slug': self.slug})

    @property
    def excerpt(self):
        """Return a plain-text excerpt of the content."""
        from django.utils.html import strip_tags
        text = strip_tags(self.content or '')
        words = text.split()
        if len(words) <= 30:
            return text
        return ' '.join(words[:30]) + '...'

    def reading_time(self):
        """Return estimated reading time in minutes."""
        from django.utils.html import strip_tags
        text = strip_tags(self.content or '')
        word_count = len(text.split())
        minutes = max(1, round(word_count / 200))
        return f"{minutes} min read"


class BlogSubscriber(models.Model):
    """Stores blog newsletter subscribers, scoped per store."""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    store = models.CharField(max_length=50, blank=True, default='orderimo')
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-subscribed_at']

    def __str__(self):
        return f"{self.email} ({self.store})"

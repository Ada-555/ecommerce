from django.db import models
from ckeditor.fields import RichTextField


class BlogPage(models.Model):
    """ Model for blog page """
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    content = RichTextField(blank=True, null=True)
    image = models.ImageField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self):
        if not self.slug:
            import re
            self.slug = re.sub(r'[^a-z0-9-]', '', self.title.lower().replace(' ', '-').replace("'", ''))[:50]
        super().save()

    def __str__(self):
        return self.title

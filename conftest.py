"""
pytest configuration for Orderimo e-commerce project.
"""

import os
import django
from django.conf import settings


def pytest_configure():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
    os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-pytest-only-do-not-use-in-production')
    os.environ.setdefault('DEVELOPMENT', '1')
    os.environ.setdefault('STRIPE_PUBLIC_KEY', 'pk_test_dummy')
    os.environ.setdefault('STRIPE_SECRET_KEY', 'sk_test_dummy')
    # Override email backend for tests — use locmem so outbox works
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    settings.DEFAULT_FROM_EMAIL = 'hello@orderimo.com'
    # Ensure in-memory outbox exists
    from django.core import mail
    if not hasattr(mail, 'outbox'):
        mail.outbox = []

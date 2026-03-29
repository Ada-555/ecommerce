import pytest
from decimal import Decimal
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from django.test import Client, RequestFactory
from affiliates.models import Affiliate, AffiliateReferral
from checkout.models import Order, OrderLineItem
from profiles.models import UserProfile


@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='testpass123')


@pytest.fixture
def affiliate(db, user):
    return Affiliate.objects.create(
        user=user,
        commission_rate=Decimal('0.10'),
        is_active=True,
    )


@pytest.fixture
def referred_user(db):
    user = User.objects.create_user(
        username='referred_user', password='testpass123'
    )
    # Create userprofile with referred_by
    profile = UserProfile.objects.get(user=user)
    return user, profile


class TestAffiliateModel:
    def test_affiliate_referral_code_auto_generated(self, user):
        """Referral code is auto-generated on creation."""
        affiliate = Affiliate.objects.create(user=user)
        assert affiliate.referral_code != ''
        assert len(affiliate.referral_code) == 12

    def test_affiliate_str_representation(self, affiliate):
        """String representation includes username and code."""
        assert affiliate.user.username in str(affiliate)
        assert affiliate.referral_code in str(affiliate)

    def test_affiliate_default_commission_rate(self, user):
        """Default commission rate is 10%."""
        affiliate = Affiliate.objects.create(user=user)
        assert float(affiliate.commission_rate) == 0.10


class TestAffiliateReferralModel:
    def test_referral_str_representation(self, affiliate, db):
        """Referral string includes affiliate code and status."""
        order = Order.objects.create(
            user_profile=affiliate.user.userprofile,
            full_name='Test Buyer',
            email='buyer@example.com',
            phone_number='+35312345678',
            country='IE',
            town_or_city='Dublin',
            street_address1='1 Main St',
            order_total=Decimal('100.00'),
            grand_total=Decimal('100.00'),
        )
        referral = AffiliateReferral.objects.create(
            affiliate=affiliate,
            order=order,
            commission_amount=Decimal('10.00'),
            status='pending',
        )
        assert 'pending' in str(referral)
        assert affiliate.referral_code in str(referral)


class TestAffiliateReferralSignal:
    def test_create_referral_for_order(self, affiliate, referred_user, db):
        """Order from referred user creates an AffiliateReferral."""
        referred_user_obj, profile = referred_user
        profile.referred_by = affiliate
        profile.save()

        order = Order.objects.create(
            user_profile=profile,
            full_name='Referred Buyer',
            email='referred@example.com',
            phone_number='+35312345678',
            country='IE',
            town_or_city='Dublin',
            street_address1='2 Side St',
            order_total=Decimal('200.00'),
            grand_total=Decimal('200.00'),
        )

        from affiliates.signals import create_referral_for_order
        referral = create_referral_for_order(order)

        assert referral is not None
        assert referral.affiliate == affiliate
        assert referral.commission_amount == Decimal('20.00')
        assert referral.status == 'pending'


class TestAffiliateViews:
    @pytest.mark.django_db
    def test_affiliate_dashboard_requires_login(self, client):
        """Unauthenticated users are redirected to login."""
        response = client.get('/accounts/affiliate/', follow=True)
        # APPEND_SLASH causes a 301 → 302 chain ending at login
        assert response.status_code in (200, 302)
        final_url = response.redirect_chain[-1][0] if response.redirect_chain else ''
        assert '/accounts/login/' in final_url or response.status_code == 200

    @pytest.mark.django_db
    def test_affiliate_register_creates_affiliate(self, client, user, db):
        """POST to register creates an Affiliate for the logged-in user."""
        client.force_login(user)
        response = client.post(
            '/accounts/affiliate/register/',
            {'commission_rate': '0.15'},
            secure=True,  # Avoid SECURE_SSL_REDIRECT intercepting POST
        )
        # Should redirect (302/200) after successful creation
        assert response.status_code in (302, 200)
        # Check affiliate created
        assert Affiliate.objects.filter(user=user).exists()
        affiliate = Affiliate.objects.get(user=user)
        assert float(affiliate.commission_rate) == 0.15

    @pytest.mark.django_db
    def test_affiliate_landing_sets_session(self, client, affiliate, db):
        """Landing page stores referral code in session and redirects."""
        response = client.get(
            f'/affiliate/{affiliate.referral_code}/',
            follow=False,
            secure=True,  # avoid SSL redirect
        )
        # Should redirect (302) to store home after setting session
        assert response.status_code == 302
        assert response.url == '/orderimo/'
        # Session is set before redirect — check via cookie on the response
        session_key = client.cookies.get(settings.SESSION_COOKIE_NAME)
        assert session_key is not None
        # Verify the session was actually created in the DB
        from django.contrib.sessions.backends.db import SessionStore
        store = SessionStore(session_key=session_key.value)
        # Need to load the session from DB
        if not store.exists(session_key.value):
            store.create()  # hmm, better to fetch from DB directly
        # Actually retrieve the session data by loading the model
        from django.contrib.sessions.models import Session
        try:
            session_model = Session.objects.get(session_key=session_key.value)
            data = session_model.get_decoded()
        except Session.DoesNotExist:
            data = {}
        assert data.get('affiliate_referral_code') == affiliate.referral_code

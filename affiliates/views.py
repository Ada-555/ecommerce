from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings

from .models import Affiliate, AffiliateReferral


def generate_affiliate_link(referral_code, request=None):
    """Generates the full referral URL for a given referral code."""
    domain = settings.LIVE_LINK.rstrip('/')
    return f"{domain}/affiliate/{referral_code}/"


@login_required
def affiliate_dashboard(request):
    """Affiliate dashboard showing stats and referral link."""
    try:
        affiliate = request.user.affiliate
    except Affiliate.DoesNotExist:
        affiliate = None

    if not affiliate or not affiliate.is_active:
        messages.warning(
            request,
            "You don't have an active affiliate account. "
            "<a href='/accounts/affiliate/register/'>Register here</a>."
        )
        return redirect('affiliate_register')

    referrals = affiliate.referrals.select_related('order').order_by('-created_at')[:20]
    total_earnings = affiliate.total_earnings()
    pending_earnings = affiliate.pending_earnings()
    total_referrals = affiliate.total_referrals()
    referral_link = generate_affiliate_link(affiliate.referral_code, request)

    context = {
        'affiliate': affiliate,
        'referrals': referrals,
        'total_earnings': total_earnings,
        'pending_earnings': pending_earnings,
        'total_referrals': total_referrals,
        'referral_link': referral_link,
    }
    return render(request, 'affiliates/dashboard.html', context)


@login_required
def affiliate_register(request):
    """Allow a user to create or activate their affiliate account."""
    # If they already have one, redirect to dashboard
    try:
        affiliate = request.user.affiliate
        if affiliate.is_active:
            messages.info(request, 'You already have an active affiliate account.')
            return redirect('affiliate_dashboard')
    except Affiliate.DoesNotExist:
        affiliate = None

    if request.method == 'POST':
        commission_rate = request.POST.get('commission_rate', '0.10')
        try:
            commission_rate = float(commission_rate)
            if not (0 < commission_rate <= 1):
                raise ValueError()
        except (ValueError, TypeError):
            messages.error(request, 'Invalid commission rate. Use a value between 0.01 and 1.0.')
            return redirect('affiliate_register')

        affiliate = Affiliate.objects.create(
            user=request.user,
            commission_rate=commission_rate,
            is_active=True,
        )
        messages.success(request, 'Your affiliate account has been created!')
        return redirect('affiliate_dashboard')

    return render(request, 'affiliates/register.html')


def affiliate_landing(request, referral_code):
    """
    Landing page for an affiliate referral link.
    Sets the referral code in the session and redirects to the store.
    """
    try:
        affiliate = Affiliate.objects.get(referral_code=referral_code.upper(), is_active=True)
    except Affiliate.DoesNotExist:
        messages.error(request, 'Invalid or expired referral link.')
        return redirect('home')

    # Store referral code in session
    request.session['affiliate_referral_code'] = affiliate.referral_code
    messages.info(
        request,
        f"You're using a referral link from {affiliate.user.username}. "
        "Register or log in to earn rewards!"
    )
    # Redirect to the default store (orderimo)
    return redirect('orderimo_home')

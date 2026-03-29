from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.signals import user_signed_up
from django.dispatch import receiver


class AffiliateAccountAdapter(DefaultAccountAdapter):
    """
    Custom allauth adapter that links new users to affiliates
    when they registered via an affiliate referral link.
    """

    def save_user(self, request, user, form, commit=True):
        """Save the user and link referral if applicable."""
        super().save_user(request, user, form, commit=False)
        if commit:
            user.save()

        # Check session for affiliate referral code
        referral_code = request.session.get('affiliate_referral_code')
        if referral_code:
            from affiliates.signals import handle_referral_on_registration
            handle_referral_on_registration(user, referral_code)
            # Clear the session key after use
            if 'affiliate_referral_code' in request.session:
                del request.session['affiliate_referral_code']

        return user

import logging
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

logger = logging.getLogger(__name__)


@require_POST
@csrf_exempt
def subscribe(request):
    """
    Subscribe an authenticated user's email to the Mailchimp list
    for the current active store.
    Uses HTMX modal-trigger pattern — returns JSON for HTMX to display message.
    """
    email = request.POST.get('email', '').strip()

    if not email:
        return JsonResponse({'success': False, 'message': 'Email address is required.'}, status=400)

    # Use authenticated user email if available, otherwise use the provided one
    if request.user.is_authenticated:
        email = request.user.email

    if not email:
        return JsonResponse({'success': False, 'message': 'Could not determine email address.'}, status=400)

    # Determine store slug from session or default
    store_slug = request.session.get('active_store', 'orderimo')

    # Get the correct list ID for this store
    list_ids = getattr(settings, 'MAILCHIMP_LIST_IDS', {})
    list_id = list_ids.get(store_slug)

    if not list_id:
        logger.warning(f"No Mailchimp list ID configured for store: {store_slug}")
        return JsonResponse({'success': False, 'message': 'Newsletter signup is not configured for this store.'}, status=400)

    api_key = getattr(settings, 'MAILCHIMP_API_KEY', None)
    server = getattr(settings, 'MAILCHIMP_SERVER', None)

    if not api_key or not server:
        logger.warning("Mailchimp API key or server not configured.")
        return JsonResponse({'success': False, 'message': 'Newsletter service is not configured.'}, status=500)

    try:
        from mailchimp_marketing import Client as MailchimpClient
        from mailchimp_marketing.api_client import ApiClientError

        mc = MailchimpClient()
        mc.set_config({'api_key': api_key, 'server': server})

        # Add member with pending status (double opt-in)
        mc.lists.add_list_member(list_id, {
            'email_address': email,
            'status': 'pending',
        })

        logger.info(f"Newsletter subscription queued for {email} in list {list_id}")
        return JsonResponse({
            'success': True,
            'message': 'Check your email to confirm your subscription!',
        })

    except ApiClientError as e:
        # Mailchimp returns error details in the response body
        error_body = getattr(e, 'body', str(e))
        logger.error(f"Mailchimp API error: {error_body}")
        return JsonResponse({'success': False, 'message': f'Could not subscribe: {error_body}'}, status=500)

    except Exception as e:
        logger.exception(f"Unexpected error subscribing {email} to newsletter")
        return JsonResponse({'success': False, 'message': 'An unexpected error occurred.'}, status=500)

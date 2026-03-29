def compare_context(request):
    """Inject compare_ids list into template context."""
    return {
        'compare_ids': request.session.get('compare_ids', []),
    }

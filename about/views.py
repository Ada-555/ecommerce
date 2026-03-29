from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from .models import AboutPage
from .forms import AboutPageForm


def contact(request):
    """Contact page with message form."""
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', '')
        message_text = request.POST.get('message', '')
        if name and email and message_text:
            send_mail(
                subject=f'Contact from {name}: {subject}',
                message=f'Name: {name}\nEmail: {email}\n\n{message_text}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
            messages.success(request, 'Message sent! We will get back to you soon.')
        else:
            messages.error(request, 'Please fill in all fields.')
        return redirect('contact')
    return render(request, 'about/contact.html')


def faq(request):
    """FAQ page with accordion-style questions."""
    faqs = [
        {'q': 'How long does delivery take?', 'a': 'Standard delivery is 3-5 business days within Ireland.'},
        {'q': 'Can I return items?', 'a': 'Yes, we offer a 30-day return policy on all items.'},
        {'q': 'How do I track my order?', 'a': 'You will receive a tracking number via email once your order ships.'},
        {'q': 'Do you ship internationally?', 'a': 'Currently we ship within Ireland and the EU.'},
        {'q': 'How do I contact support?', 'a': 'Use our contact form or email hello@orderimo.com'},
        {'q': 'Is my payment information secure?', 'a': 'Yes, all payments are processed securely via Stripe.'},
    ]
    context = {'faqs': faqs}
    return render(request, 'about/faq.html', context)


def privacy_policy(request):
    """Privacy Policy page."""
    return render(request, 'about/privacy_policy.html')


def terms(request):
    """Terms & Conditions page."""
    return render(request, 'about/terms.html')


def cookies(request):
    """Cookies Policy page."""
    return render(request, 'about/cookies.html')


def accept_cookies(request):
    """Accept cookies and redirect to home."""
    request.session['cookies_consent'] = True
    return redirect('home')


def petshop_about(request):
    """About page for PetShop Ireland store."""
    return render(request, 'about/petshop_ie.html')


def digitalhub_about(request):
    """About page for DigitalHub store."""
    return render(request, 'about/digitalhub.html')


def about(request):
    """ Display list of about pages """
    about_pages = AboutPage.objects.all().order_by('-created_at')
    template = 'about/about.html'
    context = {'about_pages': about_pages}
    return render(request, template, context)


@login_required
def create_about_page(request):
    """ Create an about page """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = AboutPageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'You created a new About Page')
            return redirect('about')

    form = AboutPageForm()
    template = 'about/create_about_page.html'
    context = {'form': form}
    return render(request, template, context)


def about_page_detail(request, pk):
    """ Display an about page """
    about_page = get_object_or_404(AboutPage, pk=pk)

    if request.method == 'POST':
        form = AboutPageForm(request.POST, instance=about_page)
        if form.is_valid():
            form.save()
            return redirect('about')

    form = AboutPageForm(instance=about_page)
    template = 'about/about_page_detail.html'
    context = {'about_page': about_page, 'form': form}
    return render(request, template, context)


@login_required
def delete_about_page(request, pk):
    """ Delete an about page """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('about'))

    about_page = get_object_or_404(AboutPage, pk=pk)

    if request.method == "POST":
        username = request.POST.get("username")

        if username == request.user.username:
            about_page.delete()
            messages.success(request, 'About post deleted!')
            return redirect(reverse('about'))

        else:
            messages.error(
                request, 'Incorrect username. About page was not deleted.')

    template = 'about/about_page_detail.html'
    context = {
        'about_page': about_page,
    }

    return render(request, template, context)


@login_required
def edit_about_page(request, pk):
    """ Edit an about page """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only admins can do that.')
        return redirect(reverse('about'))

    about = get_object_or_404(AboutPage, pk=pk)

    if request.method == 'POST':
        form = AboutPageForm(request.POST, request.FILES, instance=about)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated about page!')
            return redirect(reverse('about_page_detail', kwargs={'pk': pk}))
        else:
            messages.error(
                request,
                'Failed to update about page. Please ensure the form is valid.'
                )
    else:
        form = AboutPageForm(instance=about)
        messages.info(request, f'You are editing {about.title}')

    template = 'about/edit_about_page.html'
    context = {
        'form': form,
        'about': about,
    }

    return render(request, template, context)

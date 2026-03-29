"""
Management command to send blog newsletter emails for existing published posts.

Usage:
  # Send newsletters for all published posts that haven't been sent yet
  python manage.py send_blog_newsletter

  # Send for a specific post by ID
  python manage.py send_blog_newsletter --id 1

  # Send for all published posts (force re-send even if already sent)
  python manage.py send_blog_newsletter --force

  # Scope to a specific store
  python manage.py send_blog_newsletter --store orderimo

  # Dry run (don't actually send, just report what would be sent)
  python manage.py send_blog_newsletter --dry-run
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from blog.models import BlogPage
from blog.newsletter import send_blog_newsletter, get_blog_subscribers


class Command(BaseCommand):
    help = 'Send blog newsletter emails for published BlogPage posts via Brevo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--id', type=int, default=None,
            help='Send newsletter for a specific BlogPage ID only',
        )
        parser.add_argument(
            '--store', type=str, default=None,
            help='Scope to a specific store slug (e.g., orderimo, petshop-ie)',
        )
        parser.add_argument(
            '--force', action='store_true',
            help='Re-send even if newsletter was already sent',
        )
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Show what would be sent without actually sending',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run'] = options['dry_run']
        force = options['force']
        store_filter = options['store']
        post_id = options['id']

        qs = BlogPage.objects.filter(is_published=True)

        if post_id:
            qs = qs.filter(pk=post_id)
        if store_filter:
            qs = qs.filter(store=store_filter)
        if not force:
            qs = qs.filter(newsletter_sent_at__isnull=True)

        posts = list(qs.order_by('created_at'))

        if not posts:
            self.stdout.write(self.style.WARNING('No posts found matching the criteria.'))
            return

        self.stdout.write(f"\n{'[DRY RUN] ' if dry_run else ''}Found {len(posts)} post(s) to process.\n")

        for post in posts:
            subscribers = get_blog_subscribers(post.store) if not dry_run else []
            self.stdout.write(
                f"  • '{post.title}' (store={post.store}, "
                f"subscribers={len(subscribers)}, "
                f"already_sent={post.newsletter_sent_at is not None})"
            )

        if dry_run:
            self.stdout.write(self.style.SUCCESS('\nDry run complete. No emails sent.'))
            return

        self.stdout.write('')
        success_count = 0
        fail_count = 0

        for post in posts:
            self.stdout.write(f"Sending newsletter for: {post.title} ... ", ending='')
            ok = send_blog_newsletter(post)
            if ok:
                BlogPage.objects.filter(pk=post.pk).update(newsletter_sent_at=timezone.now())
                self.stdout.write(self.style.SUCCESS('SENT'))
                success_count += 1
            else:
                self.stdout.write(self.style.ERROR('FAILED'))
                fail_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"\nDone: {success_count} sent, {fail_count} failed.")
        )

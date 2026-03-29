"""
Usage:
  python manage.py generate_blogs --store orderimo --topic "10 Essential Tech Gadgets"
  python manage.py generate_blogs --store petshop-ie --all  # generates all topics for store
  python manage.py generate_blogs --all  # generates for ALL stores

This command uses the MiniMax API to generate blog posts.
"""
import os
import re
import requests
from django.core.management.base import BaseCommand
from blog.models import BlogPage

MINIMAX_API_KEY = os.environ.get('MINIMAX_API_KEY', '')
MINIMAX_API_URL = 'https://api.minimax.chat/v1/text/chatcompletion_pro'

STORE_TOPICS = {
    'orderimo': [
        "10 Essential Tech Gadgets for Modern Living",
        "How to Start a Successful Dropshipping Business in 2026",
        "Top 5 Home Decor Trends This Season",
        "The Ultimate Guide to Online Shopping Safely",
        "Why Multi-Store E-commerce is the Future",
        "Budget-Friendly Home Upgrades Under €50",
        "Tech Gift Guide for Every Budget",
        "Sustainable Shopping: How to Make Eco-Friendly Choices",
    ],
    'petshop-ie': [
        "Complete Guide to Setting Up Your First Fish Tank",
        "Best Dog Breeds for Irish Apartment Living",
        "Seasonal Pet Care: Preparing Your Pet for Irish Weather",
        "Top 10 Must-Have Supplies for New Cat Owners",
        "Beginner's Guide to Bird Keeping in Ireland",
        "Pet Nutrition: What You Need to Know",
        "Small Pets: Housing and Care Requirements",
        "Fish Care 101: Starting Your First Aquarium",
    ],
    'digitalhub': [
        "How to Start an Online Course Business in 2026",
        "The Complete Guide to E-book Publishing",
        "Top 10 Digital Products That Sell Like Hotcakes",
        "Building a Passive Income with Digital Downloads",
        "Best Tools for Creating Online Courses",
        "How to Price Your Digital Products",
        "Digital vs Physical: Why Digital Wins for Entrepreneurs",
        "The Future of Learning: Online Courses in 2026",
    ],
}


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--store', type=str, default=None, help='Store slug')
        parser.add_argument('--topic', type=str, default=None, help='Specific topic')
        parser.add_argument('--all', action='store_true', help='Generate for all stores')

    def generate_blog_content(self, topic, store_slug):
        """Call MiniMax API to generate blog content."""
        system_prompt = f"""You are a professional e-commerce blog writer for {store_slug} store.
Write a comprehensive, engaging blog post about the given topic.
Format in HTML. Include:
- An H1 title
- An introduction (2 paragraphs)
- At least 5 H2 sections
- A conclusion with a call to action
- Relevant product mentions where natural
Total: 600-800 words.
Tone: professional, engaging, SEO-friendly."""

        if not MINIMAX_API_KEY:
            return self.generate_fallback_content(topic)

        headers = {
            'Authorization': f'Bearer {MINIMAX_API_KEY}',
            'Content-Type': 'application/json',
        }
        payload = {
            'model': 'MiniMax-Text-01',
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': f'Write a blog post about: {topic}'},
            ],
            'max_tokens': 1500,
        }
        try:
            resp = requests.post(MINIMAX_API_URL, headers=headers, json=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                return data.get('choices', [{}])[0].get('message', {}).get('content', '')
        except Exception as e:
            self.stdout.write(f'API error: {e}')
        return self.generate_fallback_content(topic)

    def generate_fallback_content(self, topic):
        """Generate basic placeholder content when API unavailable."""
        return f"""
<h1>{topic}</h1>
<p>This is a placeholder blog post about <strong>{topic}</strong>.
The AI content generation system is being configured.
This post will be replaced with full AI-generated content.</p>

<h2>Introduction</h2>
<p>Welcome to our comprehensive guide on {topic}. In this article, we'll explore everything you need to know about this topic and how it relates to our store.</p>

<h2>Key Points</h2>
<p>Here are the key points we'll cover in this detailed guide to {topic}. Our team has researched extensively to bring you the best information.</p>

<h2>Tips and Advice</h2>
<p>Whether you're a beginner or an expert, you'll find valuable insights here about {topic}. Our goal is to help you make informed decisions.</p>

<h2>Conclusion</h2>
<p>We hope this guide to {topic} has been helpful. Be sure to explore our related products and check back for more updates.</p>
"""

    def make_slug(self, title):
        """Create a URL-safe slug from title."""
        slug = re.sub(r'[^a-z0-9-]', '', title.lower().replace(' ', '-').replace("'", ''))
        return slug[:50]

    def handle(self, *args, **options):
        stores = [options['store']] if options['store'] else list(STORE_TOPICS.keys())

        for store in stores:
            if store not in STORE_TOPICS:
                self.stdout.write(f'Unknown store: {store}')
                continue

            topics = [options['topic']] if options['topic'] else STORE_TOPICS[store]

            for topic in topics:
                self.stdout.write(f'Generating blog for {store}: {topic}')
                content = self.generate_blog_content(topic, store)

                slug = self.make_slug(topic)
                blog, created = BlogPage.objects.get_or_create(
                    title=topic,
                    defaults={
                        'content': content,
                        'slug': slug,
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created: {topic}'))
                else:
                    self.stdout.write(f'Already exists: {topic}')

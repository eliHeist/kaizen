from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from blog.models import Post


class PostTests(TestCase):
    def make(self, **kwargs):
        fields = {'title': 'A post', 'excerpt': 'e', 'body': '<p>word</p>', 'cover': 'blog/x.jpg',
                  'status': Post.Status.PUBLISHED}
        fields.update(kwargs)
        return Post.objects.create(**fields)

    def test_published_excludes_drafts_and_future_posts(self):
        live = self.make()
        self.make(title='Draft', status=Post.Status.DRAFT)
        self.make(title='Future', published_at=timezone.now() + timedelta(days=1))
        self.make(title='Hidden', is_published=False)
        self.assertEqual(list(Post.objects.published()), [live])

    def test_slug_from_title(self):
        self.assertEqual(self.make(title='What to pack!').slug, 'what-to-pack')

    def test_reading_minutes(self):
        self.assertEqual(self.make(body='<p>' + 'word ' * 450 + '</p>').reading_minutes, 3)
        self.assertEqual(self.make(body='').reading_minutes, 1)

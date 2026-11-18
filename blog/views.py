from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from blog.models import Author, Category, Post, Tag
from main import seo

PER_PAGE = 9


def _listing(request, posts, template_context):
    q = (request.GET.get('q') or '').strip()
    if q:
        posts = posts.filter(Q(title__icontains=q) | Q(excerpt__icontains=q) | Q(body__icontains=q))
    page = Paginator(posts.select_related('author', 'category'), PER_PAGE).get_page(request.GET.get('page'))
    categories = Category.objects.annotate(
        n=Count('posts', filter=Q(posts__in=Post.objects.published()))
    ).filter(n__gt=0)
    return render(request, 'blog/post_list.html', {
        'page': page,
        'posts': page.object_list,
        'categories': categories,
        'q': q,
        'noindex': bool(q),
        **template_context,
    })


def post_list(request):
    posts = Post.objects.published()
    featured = None
    if not request.GET.get('page') and not request.GET.get('q'):
        featured = posts.filter(is_featured=True).select_related('author', 'category').first()
        if featured:
            posts = posts.exclude(pk=featured.pk)
    return _listing(request, posts, {
        'featured': featured,
        'heading': 'Travel journal',
        'intro': 'Stories, guides and practical tips for travelling in Uganda and East Africa.',
        'breadcrumbs': [('Blog', None)],
    })


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    return _listing(request, Post.objects.published().filter(category=category), {
        'heading': category.name,
        'intro': category.description,
        'archive': category,
        'breadcrumbs': [('Blog', reverse('blog:list')), (category.name, None)],
    })


def tag_detail(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    return _listing(request, Post.objects.published().filter(tags=tag), {
        'heading': f'#{tag.name}',
        'intro': f'Posts tagged “{tag.name}”.',
        'archive': tag,
        'noindex': True,  # tag pages are thin and overlap categories
        'breadcrumbs': [('Blog', reverse('blog:list')), (f'#{tag.name}', None)],
    })


def author_detail(request, slug):
    author = get_object_or_404(Author, slug=slug)
    return _listing(request, Post.objects.published().filter(author=author), {
        'heading': author.name,
        'intro': author.bio,
        'author': author,
        'archive': author,
        'breadcrumbs': [('Blog', reverse('blog:list')), (author.name, None)],
    })


def post_detail(request, slug):
    post = get_object_or_404(
        Post.objects.published().select_related('author', 'category').prefetch_related('tags'),
        slug=slug,
    )
    related = Post.objects.published().exclude(pk=post.pk)
    tag_ids = list(post.tags.values_list('pk', flat=True))
    if post.category_id or tag_ids:
        related = related.filter(Q(category_id=post.category_id) | Q(tags__in=tag_ids)).distinct()
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'related': related.select_related('category')[:3],
        'tours': post.itineraries.published().prefetch_related('destinations'),
        'places': post.places.published().select_related('destination'),
        'destinations': post.destinations.published(),
        'jsonld': seo.post(post),
        'breadcrumbs': [
            ('Blog', reverse('blog:list')),
            *([(post.category.name, post.category.get_absolute_url())] if post.category else []),
            (post.title, None),
        ],
    })

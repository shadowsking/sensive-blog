from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from blog.models import Comment, Post, Tag


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments__count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': post.tags.all(),
        'first_tag_title': post.tags.all()[0].title,
    }


def index(request):
    most_popular_posts = (
        Post.objects.popular(limit=5)
        .prefetch_related('author')
        .prefetch_with_tags()
        .fetch_with_comments_count()
    )
    most_popular_tags = Tag.objects.popular(limit=5)
    most_fresh_posts = (
        Post.objects.order_by('-published_at')
        .prefetch_related('author')
        .prefetch_with_tags()
        .fetch_with_comments_count()
    )[:5]

    context = {
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': most_popular_tags,
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = get_object_or_404(
        Post.objects.popular()
        .prefetch_related('author')
        .prefetch_with_tags()
        .prefetch_with_comments(),
        slug=slug
    )

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': post.comments.all(),
        'likes_amount': post.likes__count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': post.tags.all(),
    }

    most_popular_tags = Tag.objects.popular(limit=5)
    most_popular_posts = (
        Post.objects.popular(limit=5)
        .prefetch_related('author')
        .prefetch_with_tags()
        .fetch_with_comments_count()
    )
    context = {
        'post': serialized_post,
        'popular_tags': most_popular_tags,
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = get_object_or_404(Tag, title=tag_title)
    related_posts = (
        tag.posts.annotate(Count('comments'))[:20]
        .prefetch_related('author')
        .prefetch_with_tags()
    )

    most_popular_tags = Tag.objects.popular(limit=5)
    most_popular_posts = (
        Post.objects.popular(limit=5)
        .prefetch_related('author')
        .prefetch_with_tags()
        .fetch_with_comments_count()
    )

    context = {
        'tag': tag.title,
        'popular_tags': most_popular_tags,
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})

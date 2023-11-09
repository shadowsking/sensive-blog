from django.db import models
from django.db.models import Count, Prefetch
from django.urls import reverse
from django.contrib.auth.models import User


class PostQuerySet(models.QuerySet):
    def fetch_with_comments_count(self):
        post_ids = self.values_list('id', flat=True)
        ids_and_comments = dict(
            Post.objects.filter(id__in=post_ids)
            .annotate(comments__count=Count('comments'))
            .values_list('id', 'comments__count')
        )
        for post in self:
            post.comments__count = ids_and_comments.get(post.id)

        return self

    def popular(self, limit=None):
        return (
            self.annotate(Count('likes'))
            .order_by('-likes__count')
        )[:limit]

    def prefetch_with_tags(self):
        return self.prefetch_related(
            Prefetch(
                'tags',
                queryset=Tag.objects.annotate(posts_with_tag=Count('posts')),
            ),
        )

    def prefetch_with_comments(self):
        return self.prefetch_related(
            Prefetch(
                'comments',
                queryset=(
                    Comment.objects.order_by('-published_at')
                    .prefetch_related('author')
                )
            )
        )

    def year(self, year):
        return self.filter(published_at__year=year) \
            .order_by('published_at')


class TagQuerySet(models.QuerySet):
    def popular(self, limit=None):
        return (
            self.annotate(posts_with_tag=Count('posts'))
            .order_by('-posts_with_tag')
        )[:limit]


class Post(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    text = models.TextField('Текст')
    slug = models.SlugField('Название в виде url', max_length=200)
    image = models.ImageField('Картинка')
    published_at = models.DateTimeField('Дата и время публикации')

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        limit_choices_to={'is_staff': True})
    likes = models.ManyToManyField(
        User,
        related_name='liked_posts',
        verbose_name='Кто лайкнул',
        blank=True)
    tags = models.ManyToManyField(
        'Tag',
        related_name='posts',
        verbose_name='Теги')

    objects = PostQuerySet().as_manager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args={'slug': self.slug})

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'пост'
        verbose_name_plural = 'посты'


class Tag(models.Model):
    title = models.CharField('Тег', max_length=20, unique=True)

    objects = TagQuerySet().as_manager()

    def __str__(self):
        return self.title

    def clean(self):
        self.title = self.title.lower()

    def get_absolute_url(self):
        return reverse('tag_filter', args={'tag_title': self.slug})

    class Meta:
        ordering = ['title']
        verbose_name = 'тег'
        verbose_name_plural = 'теги'


class Comment(models.Model):
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name='Пост, к которому написан')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор')

    text = models.TextField('Текст комментария')
    published_at = models.DateTimeField('Дата и время публикации')

    def __str__(self):
        return f'{self.author.username} under {self.post.title}'

    class Meta:
        ordering = ['published_at']
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'

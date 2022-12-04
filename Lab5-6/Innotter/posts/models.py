from django.db import models
from django.db.models.signals import post_save, pre_delete, m2m_changed
from django.dispatch import receiver
from django.utils.timezone import localtime
from Innotter.producer import Statistics


class Post(models.Model):
    page = models.ForeignKey('pages.Page', on_delete=models.CASCADE, related_name='posts')
    content = models.CharField(max_length=180)
    reply_to = models.ForeignKey('posts.Post', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField('users.User', related_name='liked', blank=True)

    def __str__(self):
        return f'Post by {self.page.name} at {localtime(self.created_at).date()} at {localtime(self.created_at).time()}'


@receiver(post_save, sender=Post)
def new_post_handler(sender, instance, created, **kwargs):
    if created:
        Statistics().publish(page_pk=int(instance.page.pk), field='post', action='plus')


@receiver(pre_delete, sender=Post)
def delete_post(sender, instance, using, **kwargs):
    for user in instance.likes.all():
        Statistics().publish(page_pk=int(instance.page.pk), field='like', action='minus')
    Statistics().publish(page_pk=int(instance.page.pk), field='post', action='minus')


@receiver(m2m_changed, sender=Post.likes.through)
def like_handler(sender, instance, action, **kwargs):
    match action:
        case 'post_add':
            Statistics().publish(page_pk=int(instance.page.pk), field='like', action='plus')
        case 'post_remove':
            Statistics().publish(page_pk=int(instance.page.pk), field='like', action='minus')

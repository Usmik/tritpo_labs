from django.db import models
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from Innotter.producer import Statistics


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return f'{self.name}'


class Page(models.Model):
    name = models.CharField(max_length=80, unique=True)
    puid = models.CharField(max_length=30, unique=True)
    description = models.TextField()
    tags = models.ManyToManyField('pages.Tag', related_name='pages', blank=True)
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='pages')
    followers = models.ManyToManyField('users.User', related_name='follows', blank=True)
    is_private = models.BooleanField(default=False)
    follow_requests = models.ManyToManyField('users.User', related_name='requests', blank=True)
    unblock_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Name = {self.name}, puid = {self.puid}'


@receiver(post_save, sender=Page)
def new_page_handler(sender, instance, created, **kwargs):
    if created:
        Statistics().publish(page_pk=int(instance.pk), field='page', action='new')


@receiver(m2m_changed, sender=Page.followers.through)
def followers_handler(sender, instance, action, **kwargs):
    match action:
        case 'post_add':
            Statistics().publish(page_pk=int(instance.pk), field='follower', action='plus')
        case 'post_remove':
            Statistics().publish(page_pk=int(instance.pk), field='follower', action='minus')

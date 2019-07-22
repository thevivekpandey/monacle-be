from django.db import models
from analyst.models import Team, Question
from accounts.models import User


# Create your models here.


class FeedCard(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    data = models.TextField()
    message = models.TextField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='feed_cards', related_query_name='feed_card')
    question = models.ForeignKey(Question, on_delete=models.CASCADE,
                                 related_name='feed_cards',
                                 related_query_name='feed_card')
    card_key = models.CharField(max_length=100)

    class Meta:
        ordering = ('team', 'updated', 'created',)
        unique_together = (('team', 'question', 'card_key'),)


class Comment(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    text = models.CharField(max_length=800)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='comments', related_query_name='comment')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', related_query_name='comment')
    feed_card = models.ForeignKey(FeedCard, on_delete=models.CASCADE,
                                  related_name='comments',
                                  related_query_name='comment')


class Adept(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='adepts', related_query_name='adept')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='adepts', related_query_name='adept')
    feed_card = models.ForeignKey(FeedCard, on_delete=models.CASCADE,
                                  related_name='adepts',
                                  related_query_name='adept')

    class Meta:
        unique_together = (('team', 'user', 'feed_card'),)

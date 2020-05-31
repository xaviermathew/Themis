from django.db import models


class NewsIndex(models.Model):
    id = models.TextField()
    author = models.TextField()
    title = models.TextField()
    body = models.TextField()
    query = models.TextField()
    score = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'es_articles'

from themis.core.celery import app as celery_app


@celery_app.task(ignore_result=True)
def crawl_tweets_async(person_id):
    from themis.entity.models import Person

    person = Person.objects.get(pk=person_id)
    person.crawl_tweets()

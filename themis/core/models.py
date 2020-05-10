from django.db import models


class BaseModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_on', 'updated_on']
        get_latest_by = 'created_on'

    def get_uid(self):
        return '%s.%s:%s' % (self._meta.app_label, self._meta.model_name, self.pk)

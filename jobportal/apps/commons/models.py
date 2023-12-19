from django.db import models
import uuid

# Create your models here.

class BaseModel(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True #it doesent make a table in Database so we make in abstract class only for inheritance
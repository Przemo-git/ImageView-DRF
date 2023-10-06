from datetime import timedelta

from django.utils import timezone

from images_app.fields import FieldImage

from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from django.contrib.auth import get_user_model
import uuid

# Create your models here.

from django.contrib.auth.models import AbstractUser

USER_PLANS = (
    ('B', 'Basic'),
    ('P', 'Premium'),
    ('E', 'Enterprise'),
)


class ImageUser(AbstractUser):
    plan = models.CharField(max_length=1, choices=USER_PLANS, default='B')


class ImageLink(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING)  # usunięcie linku tylko
    image = models.ForeignKey('images_app.Image', on_delete=models.DO_NOTHING)  # kolejność?
    #
    valid_to = models.DateTimeField()
    code = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expiration_time = models.IntegerField(help_text='Set expiration date to link(Enterprise)', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.valid_to:
            # If valid_to is not set, calculate it based on expiration_time
            self.valid_to = timezone.now() + timedelta(seconds=self.expiration_time)
        super().save(*args, **kwargs)

    def is_valid(self):
        # Check if the link is still valid
        return self.valid_to > timezone.now()


class Image(models.Model):

    def image_file(self, filename):
        path = "images/originals/%s" % filename
        return path

    def thumbnail_file(self, filename):
        path = "images/thumbnails/%s" % filename
        return path

    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    name = models.CharField(FieldImage.NAME, max_length=255, null=False)
    image = models.ImageField(FieldImage.IMAGE, upload_to=image_file, null=False, blank=False)
    thumbnail_200 = ImageSpecField(
        source='image',
        processors=[ResizeToFill(200, 200)],
        format='JPEG',
        options={'quality': 60})

    thumbnail_400 = ImageSpecField(
        source='image',
        processors=[ResizeToFill(400, 400)],
        format='JPEG',
        options={'quality': 60})

    create_date = models.DateTimeField(FieldImage.CREATE_DATE, default=timezone.now)

    def __str__(self):
        return str(self.name)






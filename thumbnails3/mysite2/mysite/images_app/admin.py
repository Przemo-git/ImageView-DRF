from django.contrib import admin

from images_app.models import ImageUser, ImageLink, Image

# Register your models here.


admin.site.register(ImageUser)
admin.site.register(ImageLink)
admin.site.register(Image)

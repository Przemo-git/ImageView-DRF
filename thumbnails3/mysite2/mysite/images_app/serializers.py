from images_app.models import Image, ImageUser, ImageLink
from rest_framework import serializers, viewsets


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ImageUser
        fields = ['url', 'username', 'email', 'is_staff', 'plan']






class UploadImageSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Image
        extra_kwargs = {"owner": {"required": False, "allow_null": True}}
        fields = ('name', 'image', 'owner')


class ImageSerializer(serializers.ModelSerializer):
    thumbnail_200 = serializers.ReadOnlyField(source="thumbnail_200.url")
    thumbnail_400 = serializers.ReadOnlyField(source="thumbnail_400.url")
    tmp_url = serializers.ReadOnlyField()

    class Meta:
        model = Image
        fields = '__all__'


class BasicPlanImageSerializer(serializers.ModelSerializer):
    thumbnail_200 = serializers.ReadOnlyField(source="thumbnail_200.url")

    class Meta:
        model = Image
        fields = ('name', 'thumbnail_200')


class PremiumPlanImageSerializer(serializers.ModelSerializer):
    thumbnail_200 = serializers.ReadOnlyField(source="thumbnail_200.url")
    thumbnail_400 = serializers.ReadOnlyField(source="thumbnail_400.url")

    class Meta:
        model = Image
        fields = ('name', 'image', 'thumbnail_200', 'thumbnail_400')


class TempLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = ImageLink
        fields = '__all__'












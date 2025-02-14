import uuid
from datetime import timedelta
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField, FileField, CharField
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from . import models


@extend_schema_field(field=OpenApiTypes.BINARY)
class FileUploadFiled(FileField):
    pass


class LoginSerializer(ModelSerializer):
    username = CharField(required=True)
    password = CharField()

    def is_valid(self, raise_exception=False):
        if super().is_valid(raise_exception):
            username = self.validated_data.pop("username", None)
            password = self.validated_data.pop("password", None)
            user = authenticate(username=username, password=password)
            if user is None:
                if raise_exception:
                    raise ValidationError(code=401)
                return False

            self.validated_data["user"] = user
            self.validated_data["token"] = uuid.uuid4().hex
            self.validated_data["expired_at"] = timezone.now() + timedelta(seconds=settings.TOKEN_ACTIVE_TIME)
            return True

    class Meta:
        model = models.Authorization
        fields = ["username", "password"]


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class AuthorizationSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = models.Authorization
        fields = ["token", "user", "expired_at"]


class MutationSerializerMixin:
    def get_fields(self):
        fields = {}
        for name, field in super().get_fields().items():
            field.required = False
            fields[name] = field
        return fields


class RepositoryCreationSerializer(ModelSerializer):
    class Meta:
        model = models.Repository
        fields = ["name", "remark", "url"]


class RepositoryMutationSerializer(MutationSerializerMixin, ModelSerializer):
    class Meta:
        model = models.Repository
        fields = ["name", "remark"]


class RepositorySerializer(ModelSerializer):
    created_by = UserSerializer(read_only=True)
    updated_by = UserSerializer(read_only=True)

    class Meta:
        model = models.Repository
        fields = "__all__"


class MissionCreationSerializer(ModelSerializer):
    repository = PrimaryKeyRelatedField(queryset=models.Repository.objects.all())

    class Meta:
        model = models.Mission
        fields = ["repository", "playbook", "inventories"]


class MissionEventSerializer(ModelSerializer):
    class Meta:
        model = models.MissionEvent
        fields = '__all__'


class MissionSerializer(ModelSerializer):
    repository = RepositorySerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    updated_by = UserSerializer(read_only=True)

    class Meta:
        model = models.Mission
        fields = '__all__'


class MissionWithEventsSerializer(ModelSerializer):
    repository = RepositorySerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    updated_by = UserSerializer(read_only=True)
    events = MissionEventSerializer(read_only=True, many=True)

    class Meta:
        model = models.Mission
        fields = '__all__'

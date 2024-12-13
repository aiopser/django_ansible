from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Mission, Repository, Authorization
from .serializers import *
from .runner import Runner
from .tasks import execute


class AuthorizationViewSet(GenericViewSet):
    queryset = Authorization.objects.all()
    serializer_class = AuthorizationSerializer
    permission_classes = [AllowAny]

    @extend_schema("login", request=LoginSerializer, responses=AuthorizationSerializer)
    @action(methods=["post"], detail=False, permission_classes=[AllowAny])
    def login(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(AuthorizationSerializer(serializer.instance).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema("logout", request=None, responses=None)
    @action(detail=False, methods=["put"])
    def logout(self, request: Request, *args, **kwargs):
        try:
            Authorization.objects.filter(token=request.auth).delete()
        except Authorization.DoesNotExist:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema("logoutAll", request=None, responses=None)
    @action(detail=False, methods=["delete"])
    def logout(self, request: Request, *args, **kwargs):
        try:
            Authorization.objects.filter(user=request.user).delete()
        except Authorization.DoesNotExist:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class RepositoryViewSet(GenericViewSet):
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer

    @extend_schema("createRepository", request=RepositoryCreationSerializer, responses=RepositorySerializer)
    def create(self, request, *args, **kwargs):
        serializer = RepositoryCreationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(RepositorySerializer(serializer.instance).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema("listRepositories", responses=RepositorySerializer(many=True))
    def list(self, request, *args, **kwargs):
        res = self.paginate_queryset(self.queryset)
        serializer = RepositorySerializer(res, many=True)
        return self.get_paginated_response(serializer.data)

    @extend_schema("getRepository", responses=RepositorySerializer)
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = RepositorySerializer(instance)
        return Response(serializer.data)

    @extend_schema("updateRepository", responses=RepositorySerializer, request=RepositoryMutationSerializer)
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = RepositoryMutationSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response(RepositorySerializer(serializer.instance).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MissionViewSet(GenericViewSet):
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer

    @extend_schema("createMission", request=MissionCreationSerializer, responses=MissionSerializer)
    def create(self, request, *args, **kwargs):
        serializer = MissionCreationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            execute.delay(serializer.instance.id)
            return Response(data=MissionSerializer(serializer.instance).data)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema("cancelMission", request=None, responses=MissionSerializer)
    @action(methods=["put"], detail=True)
    def cancel(self, request, *args, **kwargs):
        instance = self.get_object()
        Runner.cancel(instance)
        return Response(data=MissionSerializer(instance).data)

    @extend_schema("listMissions", responses=MissionSerializer(many=True),
                   parameters=[OpenApiParameter(name="repository", type=OpenApiTypes.INT64)])
    def list(self, request: Request, *args, **kwargs):
        queryset = self.queryset
        repository = request.query_params.get("repository")
        if repository:
            queryset = queryset.filter(repository__id=repository)
        res = self.paginate_queryset(queryset)
        serializer = MissionSerializer(instance=res, many=True)
        return self.get_paginated_response(serializer.data)

    @extend_schema("getMission", responses=MissionWithEventsSerializer)
    def retrieve(self, request, *args, **kwargs):
        serializer = MissionWithEventsSerializer(self.get_object())
        return Response(serializer.data)

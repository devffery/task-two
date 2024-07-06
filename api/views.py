from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework import generics, status, viewsets, permissions, mixins, renderers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import action

# Create your views here.

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    renderer_classes = [renderers.JSONRenderer]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                self.perform_create(serializer)
                user = serializer.instance
                access_token = AccessToken.for_user(user)
                response_data = {
                    "status": "success",
                    "message": "Registration Successful",
                    "data": {
                        'accessToken': str(access_token),
                        "user": serializer.data
                    }
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            except Exception as e:
                response_data = {
                    "status": "Bad request",
                    "message": "Registration unsuccessful",
                    "statusCode": 400
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        else:
            errors = [{"field": field, "message": str(error)} for field, error_list in serializer.errors.items() for error in error_list]
            return Response({"errors": errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    renderer_classes = [renderers.JSONRenderer]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            response_data = {
                "status": "success",
                "message": "Login Successful",
                "data": serializer.validated_data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            errors = [{"field": field, "message": str(error)} for field, error_list in serializer.errors.items() for error in error_list]
            return Response({"errors": errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

class GetUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    lookup_field = 'pk'
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.JSONRenderer]

    def get_queryset(self):
        user_organizations = self.request.user.organizations.all()
        return User.objects.filter(organizations__in=user_organizations).distinct()

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        response_data = {
            "status": "success",
            "message": "Successful",
            "data": serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)

class OrganizationViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'
    serializer_class = OrganizationSerializer
    renderer_classes = [renderers.JSONRenderer]

    def get_queryset(self):
        return self.request.user.organizations.all()

    def get_serializer_class(self):
        if self.action == 'users':
            return AddOrganizationSerializer
        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        organizations = self.get_queryset()
        serializer = self.get_serializer(organizations, many=True)
        response_data = {
            "status": "success",
            "message": "Retrieval Successful",
            "data": {
                "organizations": serializer.data
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        organization = self.get_object()
        serializer = self.get_serializer(organization)
        response_data = {
            "status": "success",
            "message": "Query Successful",
            "data": serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                self.perform_create(serializer)
                response_data = {
                    "status": "success",
                    "message": "Organization created successfully",
                    "data": serializer.data
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            except Exception as e:
                response_data = {
                    "status": "Bad request",
                    "message": "Client error",
                    "statusCode": 400
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        else:
            errors = [{"field": field, "message": str(error)} for field, error_list in serializer.errors.items() for error in error_list]
            return Response({"errors": errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    @action(detail=True, methods=['post'])
    def users(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['userId']
            try:
                user = User.objects.get(userId=user_id)
            except User.DoesNotExist:
                response_data = {
                    "status": "User not found",
                    "message": "Client error",
                    "statusCode": 404
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
            organization = self.get_object()
            user.organizations.add(organization)
            user.save()
            response_data = {
                "status": "success",
                "message": "User Added to Organization successful"
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            errors = [{"field": field, "message": str(error)} for field, error_list in serializer.errors.items() for error in error_list]
            return Response({"errors": errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

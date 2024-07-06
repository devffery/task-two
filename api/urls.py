from django.urls import path
from .views import RegisterView, LoginView, GetUserView, OrganizationViewSet
from rest_framework.routers import DefaultRouter, APIRootView
from rest_framework import renderers

class CustomApiRootView(APIRootView):
    renderer_classes = [renderers.JSONRenderer]

class CustomRouter(DefaultRouter):
    APIRootView = CustomApiRootView

router = CustomRouter(trailing_slash=False)
router.register('api/organizations', OrganizationViewSet, 'organization')

urlpatterns = [
    path('auth/register', RegisterView.as_view()),
    path('auth/login', LoginView.as_view()),
    path('api/users/<str:pk>', GetUserView.as_view()),
] + router.urls

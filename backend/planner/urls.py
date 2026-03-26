from django.urls import path
from .views import GenerateCoursePlanView

urlpatterns = [
    path('generate/', GenerateCoursePlanView.as_view(), name='generate-plan'),
]

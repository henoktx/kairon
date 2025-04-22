from django.urls import path

from . import views


urlpatterns = [path("", views.WorkflowViewset.as_view(), name="create_workflow")]

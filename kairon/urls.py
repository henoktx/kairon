from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),
    path("workflows/", include("workflows.urls")),
    path("executions/", include("executions.urls")),
    path("api-auth/", include("rest_framework.urls")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

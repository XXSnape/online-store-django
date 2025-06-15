from django.urls import path

from .views import BannersListApiView, CatalogApiView, CategoryListApiView

app_name = "catalog_app"

urlpatterns = [
    path("api/categories", CategoryListApiView.as_view(), name="categories"),
    path("api/banners", BannersListApiView.as_view(), name="banners"),
    path("api/catalog", CatalogApiView.as_view(), name="catalog"),
]

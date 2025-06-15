from django.urls import path
from .views import (
    TagsListApiView,
    ProductDetailApiView,
    SaleListApiView,
    ProductLimitedListApiView,
    ProductPopularListApiView,
    CreateProductReviewApiView,
)


app_name = "products_app"

urlpatterns = [
    path("api/tags", TagsListApiView.as_view(), name="tags"),
    path("api/sales", SaleListApiView.as_view(), name="sales"),
    path(
        "api/products/limited",
        ProductLimitedListApiView.as_view(),
        name="products_limited",
    ),
    path(
        "api/products/popular",
        ProductPopularListApiView.as_view(),
        name="products_popular",
    ),
    path("api/product/<int:pk>", ProductDetailApiView.as_view(), name="product_detail"),
    path(
        "api/product/<int:pk>/reviews",
        CreateProductReviewApiView.as_view(),
        name="create_review",
    ),
]

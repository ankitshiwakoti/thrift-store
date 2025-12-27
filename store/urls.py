from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin-panel/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-panel/products/", views.admin_products, name="admin_products"),
    path("admin-panel/products/add/", views.admin_add_product, name="admin_add_product"),
    path("admin-panel/products/<int:product_id>/edit/", views.admin_edit_product, name="admin_edit_product"),
    path("admin-panel/products/<int:product_id>/delete/", views.admin_delete_product, name="admin_delete_product"),
    path("admin-panel/categories/", views.admin_categories, name="admin_categories"),
    path("admin-panel/categories/add/", views.admin_add_category, name="admin_add_category"),
    path(
    "admin-panel/categories/<int:category_id>/edit/",
    views.admin_edit_category,
    name="admin_edit_category",
),
path(
    "admin-panel/categories/<int:category_id>/delete/",
    views.admin_delete_category,
    name="admin_delete_category",
),

#public store views can be added here as well

 path("", views.home, name="home"),
    path("category/<int:category_id>/", views.category_products, name="category_products"),
    path("product/<int:product_id>/", views.product_detail, name="product_detail"),
    path("shop/", views.shop, name="shop"),
     path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    path("cart/", views.cart_detail, name="cart_detail"),
path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
path("cart/update/<int:item_id>/", views.cart_update, name="cart_update"),
path("cart/remove/<int:item_id>/", views.cart_remove, name="cart_remove"),
path("checkout/", views.checkout, name="checkout"),
path("order/success/<int:order_id>/", views.order_success, name="order_success"),
path("orders/", views.order_history, name="order_history"),
path("orders/<int:order_id>/", views.order_detail, name="order_detail"),


]

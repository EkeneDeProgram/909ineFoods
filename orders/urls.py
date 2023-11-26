from django.urls import path
from .views import *

urlpatterns = [
    path("add_to_cart/<int:item_id>/", AddToCartView.as_view(), name="add_to_cart"),
    path("update_cart_item/<int:item_id>/", UpdateCartItemView.as_view(), name="update_cart_item"),
    path("list_cart_items/", ListCartItemsView.as_view(), name="list_cart_items"),
    path("delete_cart_item/<int:item_id>/", DeleteCartItemView.as_view(), name="delete_cart_item"),
    path("delete_all_cart_items/", DeleteAllCartItemsView.as_view(), name='delete_all_cart_items'),
    path("make_order/", AddCartItemsToOrderView.as_view(), name='make_order'),
]
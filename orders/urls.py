from django.urls import path
from .views import *

urlpatterns = [
    # path("create_shopping_cart/", CreateShoppingCartView.as_view(), name='create-shopping-cart'),
    path("add_to_cart/<int:item_id>/", AddToCartView.as_view(), name="add-to-cart"),
    # path("view_shoppingcart/", ShoppingCartItemsView.as_view(), name="view-shoppingcart"),
    # path("delete_cart_item/<int:item_id>/", DeleteCartItemView.as_view(), name="delete-cart_item"),
    # path("update_cart_item/<int:item_id>/", UpdateCartItemView.as_view(), name="update-cart_item"),
    # path("create_order/<int:vendor_id>/", PlaceOrderView.as_view(), name="create_order"),

]
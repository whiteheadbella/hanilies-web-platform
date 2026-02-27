from django.urls import path

from .views import (
    ai_recommendations_page,
    about_page,
    cake_list,
    chatbot_api,
    chatbot_page,
    customer_home,
    gallery_manage,
    product_photo_delete,
    product_photo_set_hero,
    product_photos_view,
    gallery_view,
    package_list,
    shop_location_page,
)

urlpatterns = [
    path('home/', customer_home, name='customer_home'),
    path('', cake_list, name='cake_list'),
    path('cakes/', cake_list, name='cake_list'),
    path('gallery/', gallery_view, name='gallery_view'),
    path('gallery/manage/', gallery_manage, name='gallery_manage'),
    path('gallery/manage/<int:photo_id>/set-hero/',
         product_photo_set_hero, name='product_photo_set_hero'),
    path('product-photos/', product_photos_view, name='product_photos'),
    path('product-photos/<int:photo_id>/delete/',
         product_photo_delete, name='product_photo_delete'),
    path('packages/', package_list, name='package_list'),
    path("chatbot/", chatbot_page, name="chatbot_page"),
    path("chatbot/api/", chatbot_api, name="chatbot_api"),
    path("about/", about_page, name="about_page"),
    path("shop-location/", shop_location_page, name="shop_location_page"),
    path("ai-recommendations/", ai_recommendations_page,
         name="ai_recommendations_page"),
]

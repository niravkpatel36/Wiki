from django.urls import path
from . import views

app_name = "auctions" 

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("create/", views.create_listing, name="create_listing"),
    path("listing/<int:listing_id>/", views.listing_view, name="listing"),
    path("bid/<int:listing_id>/", views.place_bid, name="place_bid"),
    path("comment/<int:listing_id>/", views.add_comment, name="add_comment"),
    path("watchlist/", views.watchlist_view, name="watchlist"),
    path("toggle_watch/<int:listing_id>/", views.toggle_watch, name="toggle_watch"),
    path("close/<int:listing_id>/", views.close_auction, name="close_auction"),
    path("categories/", views.categories_view, name="categories"),
    path("categories/<int:category_id>/", views.category_listings, name="category_listings"),
]


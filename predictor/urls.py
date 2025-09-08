from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing_page, name="landing"),
    path("app/", views.home, name="home"),  # Your main app
    path("scrape/<str:coin>/", views.scrape_coin, name="scrape_coin"),
    path("predict/<str:coin>/", views.predict_coin, name="predict_coin"),
    path("display-data/", views.display_data, name="display_data"),
]

# from django.urls import path
# from . import views

# urlpatterns = [
#     path("", views.home, name="home"),
#     path("scrape/<str:coin>/", views.scrape_coin, name="scrape_coin"),
#     path("display/", views.display_data, name="display_data"),
#     path("predict/<str:coin>/", views.predict_coin, name="predict_coin"),
# ]

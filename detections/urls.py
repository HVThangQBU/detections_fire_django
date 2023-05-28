from .import views
from django.urls import path

urlpatterns = [
    path("", views.index, name="home"),
    path("video_feed/<feed_type>/<device>/", views.video_feed, name="video_feed"),
    path(
        "video_feed_one_camera/<feed_type>/<device>/",
        views.video_feed_one_camera,
        name="video_feed_one_camera",
    ),
    path("detail_camera/<int:id>", views.detailCamera, name="detail_camera"),
    path("load_detect", views.loadDetect, name="load_detect"),
    path(
        "detail_history/<int:id>",
        views.detailHistory,
        name="detail_history",
    ),
    path("logout", views.logout, name="logout"),
    path("signin", views.signin, name="signin"),
    path("signup", views.signup, name="signup"),
    path("mapcam", views.mapCamera, name="mapcam"),
    path("cameras", views.get, name="cameras"),
    path("search_detection", views.search_detection, name="search_detection"),
]

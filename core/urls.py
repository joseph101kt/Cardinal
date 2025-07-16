from django.urls import path
from . import views
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path("", views.index, name="index"),
    path("spaced_review", views.spaced_review, name="spaced_review"),
    path("deck_review/<int:deck_id>/", views.deck_review, name="deck_review" ),
    path("create_deck", views.create_deck, name="create_deck" ),


    path("api/review-card/", views.review_card, name="review_card"),
]
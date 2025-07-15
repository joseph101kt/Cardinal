from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required

import json

from .models import User, Deck, Card
from .models import get_due_cards_for_user

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "core/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "core/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "core/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "core/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "core/register.html")


@login_required
def index(request):
    my_decks = Deck.objects.filter(user=request.user)
    public_decks = Deck.objects.exclude(user=request.user).filter(is_public=True)
    return render(request, "core/index.html", {
        "my_decks": my_decks,
        "public_decks": public_decks,
    })

@login_required
def deck_review(request, deck_id):
    deck = get_object_or_404(Deck, id=deck_id)
    cards = deck.cards.all()
    return render(request, "core/review.html", {
        "cards": cards,
        "deck": deck,
        "spaced_mode": False
    })

@login_required
def spaced_review(request):
    due_cards = get_due_cards_for_user(request.user, limit=50)  # high enough for a session
    return render(request, "core/review.html", {
        "cards": due_cards,
        "spaced_mode": True
    })

@login_required
def create_deck(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        is_public = request.POST.get("is_public") == "on"
        try:
            uploaded_file = request.FILES.get("json_file")
        except:
            print("json file for card creation not found")

        deck = Deck.objects.create(
            user=request.user,
            name=name,
            description=description,
            card_count=0,
            is_public=is_public
        )

        # If file is uploaded, create cards
        if uploaded_file:
            import json
            card_data_list = json.load(uploaded_file)
            for card_data in card_data_list:
                Card.objects.create(deck=deck, card_data=card_data)
            deck.card_count = deck.cards.count()
            deck.save()

        return redirect("index")

    return render(request, "core/create_deck.html")
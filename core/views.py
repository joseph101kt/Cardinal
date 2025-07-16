from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from django.core.paginator import Paginator

import json

from .models import User, Deck, Card, UserCardData
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
    paginator = Paginator(cards, 1)
    page_number = request.GET.get('page')
    cards = paginator.get_page(page_number)
    return render(request, "core/review.html", {
        "cards": cards,
        "deck": deck,
        "spaced_mode": False
    })

@login_required
def spaced_review(request):
    due_cards = get_due_cards_for_user(request.user, limit=50)  # high enough for a session
    paginator = Paginator(due_cards, 1)
    page_number = request.GET.get('page')
    due_cards = paginator.get_page(page_number)
    return render(request, "core/review.html", {
        "cards": due_cards,
        "spaced_mode": True
    })

@login_required
def create_deck(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("json_file")

        if not uploaded_file:
            return JsonResponse({"error": "No file uploaded."}, status=400)

        try:
            deck_data = json.load(uploaded_file)

            # Validate top-level fields
            name = deck_data.get("name")
            description = deck_data.get("description", "")
            is_public = deck_data.get("is_public", True)
            cards = deck_data.get("cards", [])

            if not name or not isinstance(cards, list):
                return JsonResponse({"error": "Deck must have a name and a list of cards."}, status=400)

            # Create deck
            deck = Deck.objects.create(
                user=request.user,
                name=name,
                description=description,
                is_public=is_public
            )

            # Validate and create cards
            created_cards = []
            for card in cards:
                card_data = card.get("card_data")
                if not card_data:
                    continue
                card_obj = Card(deck=deck, card_data=card_data)
                card_obj.clean()  # manually run validation
                created_cards.append(card_obj)

            Card.objects.bulk_create(created_cards)

            return redirect("index")

        except json.JSONDecodeError as e:
            return JsonResponse({"error": f"Invalid JSON: {e}"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return render(request, "core/create_deck.html")

@login_required
def review_card(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            card_id = data.get("card_id")
            was_correct = data.get("was_correct")

            if card_id is None or was_correct is None:
                return JsonResponse({"error": "Missing data"}, status=400)

            # Call your static method
            UserCardData.update_user_card_data(request.user, card_id, was_correct)

            return JsonResponse({"status": "success"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=405)
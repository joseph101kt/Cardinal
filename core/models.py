from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    def __str__(self):
        return self.username

class Deck(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

class Card(models.Model):
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
    card_data = models.JSONField(null=True, blank=True)  # For MCQ only
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        data = self.card_data
        if not isinstance(data.get("options"), dict):
            raise ValidationError("Options must be a dictionary.")
        if len(data["options"]) < 2:
            raise ValidationError("At least two options are required.")
        if not any(data["options"].values()):
            raise ValidationError("At least one correct answer is required.")
    
    def get_card_data(self):

        data = self.card_data or {}

        question = data.get("question", "")
        options_dict = data.get("options", {})

        options = list(options_dict.keys())
        correct_answers = [opt for opt, correct in options_dict.items() if correct]

        return {
            "question": question,
            "options": options,
            "correct_answers": correct_answers
        }

class UserCardData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)

    total_reviews = models.PositiveIntegerField(default=0)
    correct = models.PositiveIntegerField(default=0)
    last_reviewed = models.DateTimeField(null=True)
    correct_streak = models.PositiveIntegerField(default=0)

class UserSessionData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)

    total_cards = models.PositiveIntegerField(default=0)
    correct_cards = models.PositiveIntegerField(default=0)

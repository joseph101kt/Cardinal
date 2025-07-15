from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist

from django.utils import timezone

from datetime import timedelta

class User(AbstractUser):
    def __str__(self):
        return self.username
    
class Deck(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="decks")
    name = models.CharField(max_length=128, default="No name provided.")
    description = models.CharField(max_length=128, default="No description provided.")
    card_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)

        
    def get_deck_data(self):
        return {
            "name": self.name,
            "description": self.description,
            "card_count": self.card_count
        }

class Card(models.Model):
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name="cards")
    card_data = models.JSONField(null=True, blank=True) # will contain: question, options, description
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        data = self.card_data
        if not isinstance(data.get("options"), dict):
            raise ValidationError("Options must be a dictionary.")
        if len(data["options"]) < 2:
            raise ValidationError("At least two options are required.")
        if not any(data["options"].values()):
            raise ValidationError("At least one correct answer is required.")
        
        question = data.get("question")
        if not isinstance(question, str) or not question.strip():
            raise ValidationError("Question must be a non-empty string.")

        description = data.get("description")
        if description is not None and not isinstance(description, str):
            raise ValidationError("Description must be a string.")
        
    
    def get_card_data(self):

        data = self.card_data or {}

        question = data.get("question", "")
        description = data.get("description", "")
        options_dict = data.get("options", {})

        options = list(options_dict.keys())
        correct_answers = [opt for opt, correct in options_dict.items() if correct]

        return {
            "question": question,
            "description": description,
            "options": options,
            "correct_answers": correct_answers
        }

class UserCardData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)

    total_reviews = models.PositiveIntegerField(default=0)
    correct = models.PositiveIntegerField(default=0)
    wrong = models.PositiveIntegerField(default=0)
    last_reviewed = models.DateTimeField(null=True)
    correct_streak = models.PositiveIntegerField(default=0)
    next_due_at =  models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'card')
    
    @staticmethod
    def get_user_card_data(user, card_id):
        try:
            return UserCardData.objects.get(user=user, card_id=card_id)
        except ObjectDoesNotExist:
            return UserCardData.objects.create(user=user, card_id=card_id)
    
    @staticmethod
    def update_user_card_data(user, card_id, was_correct):
        data, _ = UserCardData.objects.get_or_create(user=user, card_id=card_id)
        data.total_reviews += 1
        data.last_reviewed = timezone.now()

        if was_correct:
            data.correct += 1
            data.correct_streak += 1
            interval_days = [1, 2, 5, 10, 20]
            days = interval_days[min(data.correct_streak, len(interval_days) - 1)]
            data.next_due_at = timezone.now() + timedelta(days=days)
        else:
            data.correct_streak = 0
            data.wrong += 1
            data.next_due_at = timezone.now() + timedelta(hours=12)

        data.save()

def get_due_cards_for_user(user, limit=10):
    due_progresses = UserCardData.objects.filter(
        user=user,
        next_due_at__lte=timezone.now()
    ).order_by('next_due_at')[:limit]

    return [progress.card for progress in due_progresses]
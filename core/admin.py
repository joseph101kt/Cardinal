from django.contrib import admin

from .models import User, Deck, Card, UserCardData, UserSessionData


admin.site.register(User)
admin.site.register(Deck)
admin.site.register(Card)
admin.site.register(UserCardData)
admin.site.register(UserSessionData)
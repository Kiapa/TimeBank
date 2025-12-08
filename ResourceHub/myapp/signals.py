from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Transaction

@receiver(post_save, sender=Transaction)
def update_user_balances(sender, instance, created, **kwargs):
    """
    Updates the Profile balance when a new Transaction is recorded.
    Wrapped in atomic transaction to ensure data integrity.
    """
    if created:
        with transaction.atomic():
            # Deduct from Sender
            sender_profile = instance.sender.profile
            sender_profile.time_credits -= instance.amount
            sender_profile.save()

            # Add to Receiver
            receiver_profile = instance.receiver.profile
            receiver_profile.time_credits += instance.amount
            receiver_profile.save()
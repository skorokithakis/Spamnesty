from __future__ import unicode_literals

import shortuuid
from django.db import models
from django.db.utils import IntegrityError


def generate_key() -> str:
    "Create an key."
    return shortuuid.ShortUUID().random(8)


def generate_uuid() -> str:
    "Create a UUID for an object."
    return shortuuid.ShortUUID("abdcefghjkmnpqrstuvwxyz").random()[:8]


class CharIDModel(models.Model):
    """Base model that gives children string IDs."""
    id = models.CharField(max_length=30, primary_key=True,
            default=generate_uuid, editable=False)

    class Meta:
        abstract = True


class ConversationManager(models.Manager):
    def create(self, *args, **kwargs):
        """Create an object, retrying if there's an ID collision."""

        # Try to create new IDs for the object if one collides.
        tries = 10
        for x in range(tries):
            try:
                obj = super().create(*args, **kwargs)
            except IntegrityError:
                continue
            else:
                break
        else:
            raise IntegrityError("Could not find an ID after %s tries." % tries)

        return obj


class Conversation(CharIDModel):
    """The main conversation object."""
    sender_email = models.CharField(max_length=255)
    sender_name = models.CharField(max_length=255)

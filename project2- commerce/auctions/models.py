from email.policy import default
from unicodedata import category
from django.contrib.auth.models import AbstractUser
from django.db import models




class Listing(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(verbose_name="description")
    bid_init = models.FloatField(verbose_name="bid")
    image = models.URLField(verbose_name="image")
    category = models.CharField(max_length=200)
    closed = models.BooleanField(default=False)

class User(AbstractUser):
    watchlist = models.ManyToManyField(Listing, related_name="watchuser")

class Bidder(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    bid_price = models.FloatField(verbose_name="bid-price")
    listing_bid = models.ManyToManyField(Listing,  related_name="bid")

class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing")
    comment = models.TextField(verbose_name="comment")

class Creator(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="creator")

class Winner(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="won")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="winner")
    amt = models.FloatField(verbose_name="amount")




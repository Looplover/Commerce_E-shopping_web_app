from xml.dom.minidom import Comment
from django.contrib import admin
from .models import Bidder, User, Listing, Comments, Bidder

# Register your models here.
admin.site.register(User)
admin.site.register(Listing)
admin.site.register(Bidder)
admin.site.register(Comments)

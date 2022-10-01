from webbrowser import get
from django.contrib.auth import authenticate, login, logout, get_user
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Comments, Creator, Winner



def index(request):
    prices = {}
    listings = Listing.objects.filter(closed=False)
    for listing in listings:
        w = listing.winner.all()
        for i in w:
            prices[listing.id] = i.amt
    return render(request, "auctions/index.html", {
        "listings": listings, 
        "prices": prices,
        "watchlist": False,
        "category": False
    })


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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def listing(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    creator = Creator.objects.get(listing=listing)
    winner = Winner.objects.get(listing = listing)
    user = get_user(request)
    watchlist = user.watchlist.all()
    comments = listing.listing.all()
    if request.method == "POST":
        if request.POST.get("status", False) == "add":
            user.watchlist.add(listing)
        elif request.POST.get("status",False) == "remove":
            user.watchlist.remove(listing)
        elif request.POST.get("bid", False) == "bid":
            if request.POST.get("bidcost", False): 
                if float(request.POST.get("bidcost")) > winner.amt:
                    listing.bid.create(bidder=user, bid_price=request.POST.get("bidcost"))
                    winner.delete()
                    w = Winner.objects.create(listing=listing,amt=float(request.POST.get("bidcost")),user=get_user(request))
                    w.save()
                else:
                    return render(request, "auctions/listing.html", {
                        "listing": listing,
                        "winner": winner,
                        "watchlist": watchlist,
                        "creator": creator,
                        "message": "The bid is lesser than the current price",
                        "id": listing.id,
                        "comments": comments
                    })
            else:
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "winner": winner,
                    "watchlist": watchlist,
                    "creator": creator,
                    "message": "Invalid bid",
                    "id": listing.id,
                    "comments": comments
                })
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "winner": winner,
        "watchlist": watchlist,
        "creator": creator,
        "id": listing.id,
        "comments": comments
    })

def create(request):
    user = get_user(request)
    watchlist = user.watchlist.all()
    if request.method == "POST":
        l = Listing.objects.create(title=request.POST.get("title"),description=request.POST.get("description"),bid_init=request.POST.get("bid_init"),image=request.POST.get("image"),category=request.POST.get("category"))
        l.save()
        c = Creator.objects.create(user=get_user(request),listing=l)
        c.save()
        w = Winner.objects.create(user=get_user(request),listing=l,amt=float(request.POST.get("bid_init")))
        w.save()
        creator = Creator.objects.get(listing=l)
        return render(request, "auctions/listing.html", {
            "listing": Listing.objects.get(id = l.id),
            "winner": w,
            "watchlist": watchlist,
            "creator": creator,
            "id": l.id 
        })
    else:
        return render(request, "auctions/create.html")

def close(request):
    l_id = request.POST.get("id")
    l = Listing.objects.get(id=l_id)
    l.closed = True
    l.save()
    return listing(request, l.id)

def watchlist(request):
    prices = {}
    user = get_user(request)
    listings = user.watchlist.all()
    for listing in listings:
        w = listing.winner.all()
        for i in w:
            prices[listing.id] = i.amt
    return render(request, "auctions/index.html", {
        "listings": listings, 
        "prices": prices,
        "watchlist": True,
        "category": False
    })

def categories(request):
    listings = Listing.objects.filter(closed=False)
    categories = set()
    for listing in listings:
        categories.add(listing.category)
    return render(request, "auctions/categories.html", {
        "categories": list(categories)
    })

def category(request, category):
    prices = {}
    user = get_user(request)
    listings = Listing.objects.filter(category=category, closed=False)
    for listing in listings:
        w = listing.winner.all()
        for i in w:
            prices[listing.id] = i.amt
    return render(request, "auctions/index.html", {
        "listings": listings, 
        "prices": prices,
        "watchlist": False,
        "category": True
    })

def comment(request, listing_id):
    if request.method == "POST":
        l = Listing.objects.get(id=listing_id)
        c = Comments.objects.create(comment=request.POST.get("comment"),listing=l,user=get_user(request))
        c.save()
    return listing(request, listing_id)
    

from decimal import Decimal, InvalidOperation
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Listing, Bid, Comment, Category, Watchlist
from .forms import CreateListingForm, BidForm, CommentForm

User = get_user_model()


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("auctions:index")
        else:
            return render(request, "auctions/login.html", {"message": "Invalid username/password."})
    return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return redirect("auctions:index")


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirmation = request.POST.get("confirmation")

        if password != confirmation:
            messages.error(request, "Passwords must match.")
            return render(request, "auctions/register.html")

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
        except Exception:
            messages.error(request, "Username already taken.")
            return render(request, "auctions/register.html")

        login(request, user)
        messages.success(request, "Account created.")
        return redirect("auctions:index")
    return render(request, "auctions/register.html")

def index(request):
    listings = Listing.objects.filter(active=True).order_by('-created_at')
    return render(request, "auctions/index.html", {"listings": listings})


@login_required
def create_listing(request):
    if request.method == "POST":
        form = CreateListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user
            listing.save()
            messages.success(request, "Listing created.")
            return redirect("auctions:listing", listing_id=listing.id)
        else:
            messages.error(request, "Please correct errors below.")
    else:
        form = CreateListingForm()

    return render(request, "auctions/create_listing.html", {"form": form})


def listing_view(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    comments = listing.comments.order_by('-timestamp').all()
    bids = listing.bids.order_by('-amount').all()
    current_price = listing.current_price()
    in_watchlist = False
    if request.user.is_authenticated:
        in_watchlist = Watchlist.objects.filter(user=request.user, listing=listing).exists()

    bid_form = BidForm()
    comment_form = CommentForm()

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": comments,
        "bids": bids,
        "current_price": current_price,
        "in_watchlist": in_watchlist,
        "bid_form": bid_form,
        "comment_form": comment_form
    })

@login_required
def place_bid(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)

    if not listing.active:
        messages.error(request, "This auction is closed.")
        return redirect("auctions:listing", listing_id=listing.id)

    form = BidForm(request.POST)
    if form.is_valid():
        raw_amount = form.cleaned_data['amount']
        try:
            amount = Decimal(raw_amount)
        except (InvalidOperation, TypeError):
            messages.error(request, "Enter a valid amount.")
            return redirect("auctions:listing", listing_id=listing.id)

        current_top = listing.highest_bid()
        min_allowed = listing.starting_bid if not current_top else current_top.amount

        if amount <= min_allowed:
            messages.error(request, f"Your bid must be greater than current price (${min_allowed}).")
        else:
            Bid.objects.create(bidder=request.user, listing=listing, amount=amount)
            messages.success(request, "Bid placed.")
    else:
        messages.error(request, "Invalid bid form submission.")

    return redirect("auctions:listing", listing_id=listing.id)


@login_required
def add_comment(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.listing = listing
        comment.save()
        messages.success(request, "Comment added.")
    else:
        messages.error(request, "Comment cannot be empty.")
    return redirect("auctions:listing", listing_id=listing.id)

@login_required
def toggle_watch(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    watch_item, created = Watchlist.objects.get_or_create(user=request.user, listing=listing)
    if not created:
        watch_item.delete()
        messages.info(request, "Removed from watchlist.")
    else:
        messages.success(request, "Added to watchlist.")
    return redirect("auctions:listing", listing_id=listing.id)


@login_required
def watchlist_view(request):
    watch_items = Watchlist.objects.filter(user=request.user).select_related('listing')
    listings = [w.listing for w in watch_items]
    return render(request, "auctions/watchlist.html", {"listings": listings})

@login_required
def close_auction(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    if request.user != listing.seller:
        messages.error(request, "Only the seller can close this auction.")
        return redirect("auctions:listing", listing_id=listing.id)

    highest = listing.highest_bid()
    if highest:
        listing.winner = highest.bidder
    listing.active = False
    listing.closed_at = timezone.now()
    listing.save()
    messages.success(request, "Auction closed.")
    return redirect("auctions:listing", listing_id=listing.id)


def categories_view(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {"categories": categories})


def category_listings(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    listings = category.listings.filter(active=True)
    return render(request, "auctions/category_listings.html", {
        "category": category,
        "listings": listings
    })
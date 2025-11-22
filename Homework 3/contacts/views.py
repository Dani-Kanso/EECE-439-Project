from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect

from .forms import ContactForm, ContactSearchForm, RecommendationForm
from .models import Contact
from .recommendations import RecommendationEngine


def home(request):
    """Create a new contact from the synchronized doctor dataset."""

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("success")
    else:
        form = ContactForm()

    return render(request, "contacts/createcontact.html", {"form": form})


def success(request):
    return render(request, "contacts/success.html")


def index(request):
    return redirect("contacts-list")


def list_contacts(request):
    """Render a searchable table of contacts."""

    if request.GET:
        search_form = ContactSearchForm(request.GET)
    else:
        search_form = ContactSearchForm()
    contacts = Contact.objects.all()

    if search_form.is_valid():
        data = search_form.cleaned_data
        query = data.get("query")
        specialty = data.get("specialty")
        city = data.get("city")
        state = data.get("state")
        max_fee = data.get("max_fee")
        min_rating = data.get("min_rating")
        accepts_new_patients = data.get("accepts_new_patients")
        sort_by = data.get("sort_by") or "name"

        if query:
            contacts = contacts.filter(
                Q(name__icontains=query)
                | Q(hospital__icontains=query)
                | Q(specialty__icontains=query)
            )
        if specialty:
            contacts = contacts.filter(specialty__icontains=specialty)
        if city:
            contacts = contacts.filter(city__icontains=city)
        if state:
            contacts = contacts.filter(state__icontains=state)
        if max_fee is not None:
            contacts = contacts.filter(consultation_fee__lte=max_fee)
        if min_rating is not None:
            contacts = contacts.filter(rating__gte=min_rating)
        if accepts_new_patients:
            contacts = contacts.filter(accepts_new_patients=True)

        if sort_by == "rating":
            contacts = contacts.order_by("-rating", "name")
        elif sort_by == "fee":
            contacts = contacts.order_by("consultation_fee", "name")
        elif sort_by == "experience":
            contacts = contacts.order_by("-experience_years", "name")
        else:
            contacts = contacts.order_by("name")
    else:
        contacts = contacts.order_by("name")

    return render(
        request,
        "contacts/list.html",
        {
            "contacts": contacts,
            "search_form": search_form,
        },
    )


def edit_contact(request, pk):
    """Update a contact's information."""

    contact = get_object_or_404(Contact, pk=pk)
    if request.method == "POST":
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            return redirect("contacts-list")
    else:
        form = ContactForm(instance=contact)
    return render(request, "contacts/editcontact.html", {"form": form, "contact": contact})


def delete_contact(request, pk):
    """Delete a contact after confirmation."""

    contact = get_object_or_404(Contact, pk=pk)
    if request.method == "POST":
        contact.delete()
        return redirect("contacts-list")
    return render(request, "contacts/confirm_delete.html", {"contact": contact})


def recommend_contacts(request):
    """
    Provide recommendations by scoring contacts based on user preferences.
    """

    if request.GET:
        form = RecommendationForm(request.GET)
    else:
        form = RecommendationForm()
    recommendations = []
    query_executed = False

    if form.is_valid():
        normalized_values = [
            value for value in form.cleaned_data.values() if value not in [None, "", False]
        ]
        if normalized_values:
            query_executed = True
            data = form.cleaned_data
            contacts = Contact.objects.all()
            if data.get("specialty"):
                contacts = contacts.filter(specialty__icontains=data["specialty"])
            if data.get("city"):
                contacts = contacts.filter(city__icontains=data["city"])
            if data.get("state"):
                contacts = contacts.filter(state__icontains=data["state"])
            if data.get("max_fee") is not None:
                contacts = contacts.filter(consultation_fee__lte=data["max_fee"])
            if data.get("min_rating") is not None:
                contacts = contacts.filter(rating__gte=data["min_rating"])

            engine = RecommendationEngine()
            recommendations = engine.recommend(contacts, data)

    return render(
        request,
        "contacts/recommendations.html",
        {
            "form": form,
            "recommendations": recommendations,
            "query_executed": query_executed,
        },
    )

from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.db.models import Q
from urllib.parse import quote
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST
from django.utils.datastructures import MultiValueDict
from .forms import (
    BlogForm,
    CategoryForm,
    DestinationForm,
    TestimonialForm,
    TourPackageForm,
    ActivityForm,
)

from .models import (
    Blog,
    BookingEnquiry,
    Category,
    ContactMessage,
    Destination,
    GalleryImage,
    Testimonial,
    TourPackage,
    Activity,
    DestinationImage

)



# ============================================================
# ADMIN ACCESS DECORATOR
# ============================================================

def admin_required(view_func):

    @wraps(view_func)
    @login_required(login_url="admin_login")
    def wrapper(request, *args, **kwargs):

        if not request.user.is_staff:
            messages.error(
                request,
                "You do not have permission to access the admin dashboard."
            )

            logout(request)

            return redirect("admin_login")

        return view_func(
            request,
            *args,
            **kwargs
        )

    return wrapper


# ============================================================
# ADMIN LOGIN
# ============================================================

def admin_login(request):

    # Already logged in as an admin
    if request.user.is_authenticated:

        if request.user.is_staff:
            return redirect("admin_dashboard")

        logout(request)


    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )


        # Required fields
        if not username or not password:

            messages.error(
                request,
                "Username and password are required."
            )

            return render(
                request,
                "authenticate/login.html",
            )


        # Authenticate
        user = authenticate(
            request,
            username=username,
            password=password,
        )


        if user is not None and user.is_staff:

            login(
                request,
                user
            )

            messages.success(
                request,
                f"Welcome back, {user.username}!"
            )

            return redirect(
                "admin_dashboard"
            )


        messages.error(
            request,
            "Invalid username, password, or unauthorized access."
        )


    return render(
        request,
        "authenticate/login.html",
    )


# ============================================================
# ADMIN LOGOUT
# ============================================================

@admin_required
def admin_logout(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect(
        "admin_login"
    )






# ============================================================
# ADMIN DASHBOARD
# ============================================================

@admin_required
def admin_dashboard(request):

    now = timezone.now()

    month_start = now.replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )


    # ========================================================
    # STATISTICS
    # ========================================================

    stats = {

        "total_packages":
            TourPackage.objects.count(),

        "total_destinations":
            Destination.objects.count(),

        "total_blogs":
            Blog.objects.count(),

        "blogs_this_month":
            Blog.objects.filter(
                created_at__gte=month_start
            ).count(),

        "total_gallery":
            GalleryImage.objects.count(),

        "total_testimonials":
            Testimonial.objects.count(),

        "total_contacts":
            ContactMessage.objects.count(),

        "total_enquiries":
            BookingEnquiry.objects.count(),
    }


    # ========================================================
    # RECENT DATA
    # ========================================================

    recent_packages = (
        TourPackage.objects
        .order_by("-created_at")[:5]
    )

    recent_destinations = (
        Destination.objects
        .order_by("-created_at")[:5]
    )

    recent_blogs = (
        Blog.objects
        .order_by("-created_at")[:5]
    )

    recent_contacts = (
        ContactMessage.objects
        .order_by("-created_at")[:5]
    )

    recent_enquiries = (
        BookingEnquiry.objects
        .order_by("-created_at")[:5]
    )


    context = {

        "stats": stats,

        "recent_packages":
            recent_packages,

        "recent_destinations":
            recent_destinations,

        "recent_blogs":
            recent_blogs,

        "recent_contacts":
            recent_contacts,

        "recent_enquiries":
            recent_enquiries,
    }


    return render(
        request,
        "admin_pages/dashboard.html",
        context,
    )





# ============================================================
# BLOGS
# ============================================================

@admin_required
def admin_blog_list(request):

    blogs = Paginator(
        Blog.objects.order_by("-created_at"),
        10,
    ).get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "admin_pages/blog_list.html",
        {
            "blogs": blogs,
        },
    )


@admin_required
def blog_create(request):

    form = BlogForm(
        request.POST or None,
        request.FILES or None,
    )

    if form.is_valid():

        form.save()

        messages.success(
            request,
            "Blog created successfully."
        )

        return redirect(
            "admin_blog_list"
        )

    return render(
        request,
        "admin_pages/create_blog.html",
        {
            "form": form,
        },
    )


@admin_required
def blog_update(request, pk):

    blog = get_object_or_404(
        Blog,
        pk=pk,
    )

    form = BlogForm(
        request.POST or None,
        request.FILES or None,
        instance=blog,
    )

    if form.is_valid():

        form.save()

        messages.success(
            request,
            "Blog updated successfully."
        )

        return redirect(
            "admin_blog_list"
        )

    return render(
        request,
        "admin_pages/create_blog.html",
        {
            "form": form,
            "blog": blog,
        },
    )


@admin_required
def blog_delete(request, pk):

    blog = get_object_or_404(
        Blog,
        pk=pk,
    )

    if request.method == "POST":

        blog.delete()

        messages.success(
            request,
            "Blog deleted successfully."
        )

    return redirect(
        "admin_blog_list"
    )





# ============================================================
# TOUR PACKAGES
# ============================================================

@admin_required
def admin_package_list(request):

    packages = Paginator(
        TourPackage.objects.order_by("-created_at"),
        10,
    ).get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "admin_pages/package_list.html",
        {
            "packages": packages,
        },
    )


@admin_required
def package_create(request):

    form = TourPackageForm(
        request.POST or None,
        request.FILES or None,
    )

    if form.is_valid():

        form.save()

        messages.success(
            request,
            "Tour package created successfully."
        )

        return redirect(
            "admin_package_list"
        )

    return render(
        request,
        "admin_pages/create_package.html",
        {
            "form": form,
        },
    )


@admin_required
def package_update(request, pk):

    package = get_object_or_404(
        TourPackage,
        pk=pk,
    )

    form = TourPackageForm(
        request.POST or None,
        request.FILES or None,
        instance=package,
    )

    if form.is_valid():

        form.save()

        messages.success(
            request,
            "Tour package updated successfully."
        )

        return redirect(
            "admin_package_list"
        )

    return render(
        request,
        "admin_pages/create_package.html",
        {
            "form": form,
            "package": package,
        },
    )


@admin_required
def package_delete(request, pk):

    package = get_object_or_404(
        TourPackage,
        pk=pk,
    )

    if request.method == "POST":

        package.delete()

        messages.success(
            request,
            "Tour package deleted successfully."
        )

    return redirect(
        "admin_package_list"
    )




# ============================================================
# DESTINATIONS
# ============================================================

@admin_required
def admin_destination_list(request):

    destinations = Paginator(
        Destination.objects.order_by("-created_at"),
        10,
    ).get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "admin_pages/destination_list.html",
        {
            "destinations": destinations,
        },
    )


# ============================================================
# DESTINATIONS
# ============================================================

def _split_hero_and_extras(request):
    """First uploaded file = hero image, the rest = extra images."""
    files = request.FILES.getlist("image")
    hero_files = MultiValueDict({"image": files[:1]}) if files else None
    return hero_files, files[1:]


def _save_extra_destination_images(destination, extras):
    for f in extras:
        DestinationImage.objects.create(
            destination=destination,
            image=f,
        )


@admin_required
def destination_create(request):

    hero_files, extras = _split_hero_and_extras(request)

    form = DestinationForm(
        request.POST or None,
        hero_files,
    )

    if form.is_valid():

        destination = form.save()

        _save_extra_destination_images(destination, extras)

        messages.success(
            request,
            "Destination created successfully."
        )

        return redirect(
            "admin_destination_list"
        )

    return render(
        request,
        "admin_pages/create_destination.html",
        {
            "form": form,
        },
    )


@admin_required
def destination_update(request, pk):

    destination = get_object_or_404(
        Destination,
        pk=pk,
    )

    hero_files, extras = _split_hero_and_extras(request)

    form = DestinationForm(
        request.POST or None,
        hero_files,
        instance=destination,
    )

    if form.is_valid():

        form.save()

        # Remove extra images the admin ticked
        delete_ids = request.POST.getlist("delete_images")
        if delete_ids:
            for img in DestinationImage.objects.filter(
                destination=destination,
                pk__in=delete_ids,
            ):
                img.delete()

        _save_extra_destination_images(destination, extras)

        messages.success(
            request,
            "Destination updated successfully."
        )

        return redirect(
            "admin_destination_list"
        )

    return render(
        request,
        "admin_pages/create_destination.html",
        {
            "form": form,
            "destination": destination,
        },
    )
@admin_required
def destination_delete(request, pk):

    destination = get_object_or_404(
        Destination,
        pk=pk,
    )

    if request.method == "POST":

        destination.delete()

        messages.success(
            request,
            "Destination deleted successfully."
        )

    return redirect(
        "admin_destination_list"
    )





# ============================================================
# GALLERY
# ============================================================

@admin_required
def gallery_images(request):

    categories = (
        Category.objects
        .prefetch_related("images")
        .order_by("name")
    )

    return render(
        request,
        "admin_pages/image_list.html",
        {
            "categories": categories,
        },
    )


@admin_required
def add_image(request):

    categories = Category.objects.order_by(
        "name"
    )

    if request.method == "POST":

        category_id = request.POST.get(
            "category"
        )

        files = request.FILES.getlist(
            "images"
        )

        if not category_id:

            messages.error(
                request,
                "Please select a category."
            )

            return render(
                request,
                "admin_pages/add_image.html",
                {
                    "categories": categories,
                },
            )


        category = get_object_or_404(
            Category,
            pk=category_id,
        )


        if not files:

            messages.error(
                request,
                "Please select at least one image."
            )

            return render(
                request,
                "admin_pages/add_image.html",
                {
                    "categories": categories,
                },
            )


        for image_file in files:

            GalleryImage.objects.create(
                category=category,
                title=image_file.name,
                image=image_file,
            )


        messages.success(
            request,
            "Gallery images uploaded successfully."
        )

        return redirect(
            "list_image"
        )


    return render(
        request,
        "admin_pages/add_image.html",
        {
            "categories": categories,
        },
    )


@admin_required
def delete_image(request, image_id):

    image = get_object_or_404(
        GalleryImage,
        pk=image_id,
    )

    if request.method == "POST":

        image.delete()

        messages.success(
            request,
            "Gallery image deleted successfully."
        )

    return redirect(
        "list_image"
    )





# ============================================================
# CATEGORIES
# ============================================================

@admin_required
def category_list(request):

    categories = Category.objects.order_by(
        Lower("name")
    )

    return render(
        request,
        "admin_pages/category_list.html",
        {
            "categories": categories,
        },
    )


@admin_required
def add_category(request):

    form = CategoryForm(
        request.POST or None
    )

    if form.is_valid():

        form.save()

        messages.success(
            request,
            "Category added successfully."
        )

        return redirect(
            "category_list"
        )

    return render(
        request,
        "admin_pages/add_category.html",
        {
            "form": form,
        },
    )


@admin_required
def update_category(request, pk):

    category = get_object_or_404(
        Category,
        pk=pk,
    )

    form = CategoryForm(
        request.POST or None,
        instance=category,
    )

    if form.is_valid():

        form.save()

        messages.success(
            request,
            "Category updated successfully."
        )

        return redirect(
            "category_list"
        )

    return render(
        request,
        "admin_pages/add_category.html",
        {
            "form": form,
            "category": category,
        },
    )


@admin_required
def delete_category(request, pk):

    category = get_object_or_404(
        Category,
        pk=pk,
    )

    if request.method == "POST":

        category.delete()

        messages.success(
            request,
            "Category deleted successfully."
        )

    return redirect(
        "category_list"
    )






# ============================================================
# TESTIMONIALS
# ============================================================

@admin_required
def testimonial_list(request):

    testimonials = Paginator(
        Testimonial.objects.order_by("-created_at"),
        10,
    ).get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "admin_pages/review_list.html",
        {
            "testimonials": testimonials,
        },
    )


@admin_required
def testimonial_create(request):

    form = TestimonialForm(
        request.POST or None,
        request.FILES or None,
    )

    if form.is_valid():

        form.save()

        messages.success(
            request,
            "Testimonial created successfully."
        )

        return redirect(
            "review_list"
        )

    return render(
        request,
        "admin_pages/create_review.html",
        {
            "form": form,
        },
    )


@admin_required
def testimonial_update(request, pk):

    testimonial = get_object_or_404(
        Testimonial,
        pk=pk,
    )

    form = TestimonialForm(
        request.POST or None,
        request.FILES or None,
        instance=testimonial,
    )

    if form.is_valid():

        form.save()

        messages.success(
            request,
            "Testimonial updated successfully."
        )

        return redirect(
            "review_list"
        )

    return render(
        request,
        "admin_pages/create_review.html",
        {
            "form": form,
            "testimonial": testimonial,
        },
    )


@admin_required
def testimonial_delete(request, pk):

    testimonial = get_object_or_404(
        Testimonial,
        pk=pk,
    )

    if request.method == "POST":

        testimonial.delete()

        messages.success(
            request,
            "Testimonial deleted successfully."
        )

    return redirect(
        "review_list"
    )




# ============================================================
# CONTACT MESSAGES
# ============================================================

@admin_required
def view_contacts(request):

    contacts = Paginator(
        ContactMessage.objects.order_by("-created_at"),
        10,
    ).get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "admin_pages/view_contacts.html",
        {
            "contacts": contacts,
        },
    )


@admin_required
def delete_contact(request, pk):

    contact = get_object_or_404(
        ContactMessage,
        pk=pk,
    )

    if request.method == "POST":

        contact.delete()

        messages.success(
            request,
            "Contact message deleted successfully."
        )

    return redirect(
        "view_contacts"
    )




# ============================================================
# BOOKING ENQUIRIES
# ============================================================

@admin_required
def admin_enquiry_list(request):

    enquiries = Paginator(
        BookingEnquiry.objects.order_by("-created_at"),
        10,
    ).get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "admin_pages/enquiry_list.html",
        {
            "enquiries": enquiries,
        },
    )


@admin_required
def admin_enquiry_delete(request, pk):

    enquiry = get_object_or_404(
        BookingEnquiry,
        pk=pk,
    )

    if request.method == "POST":

        enquiry.delete()

        messages.success(
            request,
            "Booking enquiry deleted successfully."
        )

    return redirect(
        "admin_enquiry_list"
    )


@admin_required
def admin_activity_list(request):
 
    query = request.GET.get("q", "").strip()
 
    activities = Activity.objects.all()
 
    if query:
        activities = activities.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
        )
 
    page_obj = Paginator(
        activities,
        10,
    ).get_page(
        request.GET.get("page")
    )
 
    return render(
        request,
        "admin_pages/activity_list.html",
        {
            "activities": page_obj,
            "query": query,
        },
    )
 
 
@admin_required
def activity_detail(request, slug):
 
    activity = get_object_or_404(
        Activity,
        slug=slug,
    )
 
    return render(
        request,
        "admin_pages/activity_detail.html",
        {
            "activity": activity,
        },
    )
 
 
@admin_required
def activity_create(request):
 
    form = ActivityForm(
        request.POST or None,
        request.FILES or None,
    )
 
    if form.is_valid():
 
        form.save()
 
        messages.success(
            request,
            "Activity created successfully."
        )
 
        return redirect(
            "admin_activity_list"
        )
 
    return render(
        request,
        "admin_pages/activity_form.html",
        {
            "form": form,
        },
    )
 
 
@admin_required
def activity_update(request, slug):
 
    activity = get_object_or_404(
        Activity,
        slug=slug,
    )
 
    form = ActivityForm(
        request.POST or None,
        request.FILES or None,
        instance=activity,
    )
 
    if form.is_valid():
 
        form.save()
 
        messages.success(
            request,
            "Activity updated successfully."
        )
 
        return redirect(
            "admin_activity_list"
        )
 
    return render(
        request,
        "admin_pages/activity_form.html",
        {
            "form": form,
            "activity": activity,
        },
    )
 
 
@admin_required
def activity_delete(request, slug):
 
    activity = get_object_or_404(
        Activity,
        slug=slug,
    )
 
    if request.method == "POST":
 
        activity.delete()
 
        messages.success(
            request,
            "Activity deleted successfully."
        )
 
    return redirect(
        "admin_activity_list"
    )
 











#frontends

def home(request):
    return render(request, "frontends/home.html", {
        "destinations": Destination.objects.order_by("-created_at"),
        "recent_activities": Activity.objects.order_by("-created_at")[:3],
        "featured_packages": TourPackage.objects.order_by("-created_at"),
        "testimonials": Testimonial.objects.order_by("-created_at"),
    })
def about(request):
    return render(request, 'frontends/about.html', {
        'featured_packages': TourPackage.objects.all(),   # same query as home view
        'testimonials': Testimonial.objects.all(),    # same query as home view
    })

def activities(request):
    items = Activity.objects.all()  # Meta ordering (order, -created_at) applies
    return render(request, "frontends/activities.html", {"activities": items})

from django.shortcuts import render, get_object_or_404
from .models import Activity

def activity_detail(request, slug):
    activity = get_object_or_404(Activity, slug=slug)
    other_activities = Activity.objects.exclude(pk=activity.pk)
    return render(request, 'frontends/activity_detail.html', {
        'activity': activity,
        'other_activities': other_activities,
    })
from django.utils.text import slugify
def packages(request):
    items = TourPackage.objects.order_by("-created_at")

    grouped = {}
    other = []
    for p in items:
        name = " ".join((p.category or "").split())
        if not name:
            other.append(p)
            continue
        group = grouped.setdefault(
            name.lower(),
            {"value": slugify(name), "label": name, "packages": []},
        )
        group["packages"].append(p)

    groups = sorted(grouped.values(), key=lambda g: g["label"].lower())
    if other:
        groups.append({"value": "other", "label": "Other Packages", "packages": other})

    # ?category=south-kerala -> show only that category
    selected = request.GET.get("category", "").strip()
    if selected:
        groups = [g for g in groups if g["value"] == selected]

    return render(request, "frontends/packages.html", {
        "groups": groups,
        "selected": selected,
    })
def package_detail(request, slug):
    package = get_object_or_404(TourPackage, slug=slug)
    others = TourPackage.objects.exclude(pk=package.pk).order_by("-created_at")

    current = " ".join((package.category or "").split()).lower()

    grouped = {}
    other = []
    for p in others:
        name = " ".join((p.category or "").split())
        if not name:
            other.append(p)
            continue
        g = grouped.setdefault(name.lower(), {"key": name.lower(), "label": name, "packages": []})
        g["packages"].append(p)

    # A to Z, but the current package's category goes first
    sidebar_groups = sorted(
        grouped.values(),
        key=lambda g: (g["key"] != current, g["label"].lower()),
    )
    if other:
        sidebar_groups.append({"key": "other", "label": "Other Packages", "packages": other})

    return render(request, "frontends/package_detail.html", {
        "package": package,
        "sidebar_groups": sidebar_groups,
    })
def _save_booking_enquiry(data):
    """Save to BookingEnquiry using whichever matching fields the model has."""
    fields = {
        f.name: f
        for f in BookingEnquiry._meta.get_fields()
        if getattr(f, "concrete", False) and not f.primary_key
    }
 
    candidates = {
        "name": ["name", "full_name", "customer_name", "fullname"],
        "phone": ["phone", "phone_number", "mobile", "contact_number"],
        "email": ["email", "email_address"],
        "package": ["package", "package_name", "interest", "destination"],
        "start_date": ["start_date", "check_in", "from_date", "travel_date"],
        "end_date": ["end_date", "check_out", "to_date"],
        "guests": ["guests", "guest_count", "persons", "people", "number_of_guests", "adults"],
        "message": ["message", "notes", "comments", "special_requests", "details"],
        "channel": ["channel", "source"],
    }
 
    values = {}
    for key, names in candidates.items():
        raw = data.get(key, "")
        if raw == "":
            continue
        for fname in names:
            f = fields.get(fname)
            if not f or f.is_relation or fname in values:
                continue
            kind = f.get_internal_type()
            if kind in (
                "IntegerField",
                "PositiveIntegerField",
                "SmallIntegerField",
                "PositiveSmallIntegerField",
            ):
                try:
                    values[fname] = int(raw)
                except ValueError:
                    continue
            elif kind == "DateField":
                parsed = parse_date(raw)
                if not parsed:
                    continue
                values[fname] = parsed
            else:
                values[fname] = raw
            break
 
    try:
        BookingEnquiry.objects.create(**values)
        return True
    except Exception:
        return False
 
import re
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
NAME_RE = re.compile(r"[^\W\d_]+(?:[ .'’\-]+[^\W\d_]+)*\.?")   # letters only, no digits
PHONE_RE = re.compile(r"\+?\d{7,15}")


def valid_name(value):
    """Letters, spaces and . ' - only. No digits or symbols."""
    return 2 <= len(value) <= 60 and bool(NAME_RE.fullmatch(value))


def clean_phone(value):
    """Return the phone as digits (optional leading +), or None if invalid."""
    cleaned = re.sub(r"[\s\-()]", "", value)
    return cleaned if PHONE_RE.fullmatch(cleaned) else None


@require_POST
def booking_email(request):
    data = {
        "name": request.POST.get("name", "").strip(),
        "phone": request.POST.get("phone", "").strip(),
        "email": request.POST.get("email", "").strip(),
        "package": request.POST.get("package", "").strip(),
        "start_date": request.POST.get("start_date", "").strip(),
        "end_date": request.POST.get("end_date", "").strip(),
        "guests": request.POST.get("guests", "").strip(),
        "message": request.POST.get("message", "").strip(),
        "channel": request.POST.get("channel", "email").strip() or "email",
    }

    def bad(msg):
        return JsonResponse({"ok": False, "error": msg}, status=400)

    # ---- Name ----
    if not data["name"]:
        return bad("Name is required.")
    if not valid_name(data["name"]):
        return bad("Please enter a valid name (letters only, no numbers).")

    # ---- Phone ----
    if not data["phone"]:
        return bad("Phone number is required.")
    phone = clean_phone(data["phone"])
    if not phone:
        return bad("Please enter a valid phone number (7 to 15 digits).")
    data["phone"] = phone

    # ---- Email (optional, but must be valid if given) ----
    if data["email"]:
        try:
            validate_email(data["email"])
        except ValidationError:
            return bad("Please enter a valid email address.")

    # ---- Dates ----
    if not data["start_date"] or not data["end_date"]:
        return bad("Start date and end date are required.")
    start = parse_date(data["start_date"])
    end = parse_date(data["end_date"])
    if not start or not end:
        return bad("Please enter valid dates.")
    if start < timezone.localdate():
        return bad("Start date cannot be in the past.")
    if end < start:
        return bad("End date cannot be before the start date.")

    # ---- Guests (optional, but must be a sensible number if given) ----
    if data["guests"]:
        if not data["guests"].isdigit() or not (1 <= int(data["guests"]) <= 100):
            return bad("Please enter a valid number of guests.")

    # ---- Keep free-text fields to a sane length ----
    data["package"] = data["package"][:150]
    data["message"] = data["message"][:2000]

    # 1) Always save the enquiry first so the lead is never lost
    saved = _save_booking_enquiry(data)

    # 2) WhatsApp-only submissions just need saving
    if data["channel"] == "whatsapp":
        return JsonResponse({"ok": True, "saved": saved})

    # 3) Email notification
    body = (
        f"New booking enquiry from the website\n\n"
        f"Name: {data['name']}\n"
        f"Phone: {data['phone']}\n"
        f"Email: {data['email'] or '-'}\n"
        f"Package/Interest: {data['package'] or '-'}\n"
        f"Start date: {data['start_date']}\n"
        f"End date: {data['end_date']}\n"
        f"Guests: {data['guests'] or '-'}\n\n"
        f"Message:\n{data['message'] or '-'}\n"
    )

    recipient = getattr(settings, "BOOKING_NOTIFY_EMAIL", settings.DEFAULT_FROM_EMAIL)

    try:
        send_mail(
            subject=f"Booking enquiry - {data['name']}",
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
    except Exception:
        if saved:
            # Enquiry is stored, so don't scare the visitor
            return JsonResponse({"ok": True, "saved": True})
        return JsonResponse(
            {"ok": False, "error": "Could not send your enquiry. Please try WhatsApp."},
            status=500,
        )

    return JsonResponse({"ok": True, "saved": saved})
 
 

def booking_packages(request):
    return {"booking_packages": TourPackage.objects.order_by("-created_at")}
def booking_packages(request):
    cats = {}
    for c in TourPackage.objects.exclude(category="").values_list("category", flat=True):
        label = " ".join(c.split())
        cats.setdefault(label.lower(), label)

    locs = {}
    for l in Destination.objects.exclude(location="").values_list("location", flat=True):
        label = " ".join(l.split())
        locs.setdefault(label.lower(), label)

    return {
        "booking_packages": TourPackage.objects.order_by("-created_at"),
        "nav_categories": sorted(
            ({"label": v, "value": slugify(v)} for v in cats.values()),
            key=lambda x: x["label"].lower(),
        ),
        "nav_locations": sorted(
            ({"label": v, "value": slugify(v)} for v in locs.values()),
            key=lambda x: x["label"].lower(),
        ),
    }


def destinations(request):
    items = Destination.objects.order_by("-created_at")

    grouped = {}
    other = []
    for d in items:
        name = " ".join((d.location or "").split())
        if not name:
            other.append(d)
            continue
        g = grouped.setdefault(
            name.lower(),
            {"value": slugify(name), "label": name, "destinations": []},
        )
        g["destinations"].append(d)

    groups = sorted(grouped.values(), key=lambda g: g["label"].lower())
    if other:
        groups.append({"value": "other", "label": "Other Destinations", "destinations": other})

    # ?location=kerala -> show only that location
    selected = request.GET.get("location", "").strip()
    if selected:
        groups = [g for g in groups if g["value"] == selected]

    return render(request, "frontends/destinations.html", {
        "groups": groups,
        "selected": selected,
    })
def destination_detail(request, slug):
    destination = get_object_or_404(Destination, slug=slug)
    other_destinations = Destination.objects.exclude(pk=destination.pk).order_by("-created_at")
    return render(request, "frontends/destination_detail.html", {
        "destination": destination,
        "other_destinations": other_destinations,
    })

def gallery(request):
    # Only show categories that actually have images
    categories = (
        Category.objects
        .filter(images__isnull=False)
        .distinct()
        .order_by(Lower("name"))
    )
    images = GalleryImage.objects.select_related("category").order_by("-pk")

    return render(request, "frontends/gallery.html", {
        "categories": categories,
        "images": images,
    })
import json
import urllib.parse
import urllib.request

from django.core.exceptions import ValidationError
from django.core.validators import validate_email


CONTACT_INFO = {
    "address_lines": ["Malabar Routes"],
    "phone": "+91 9446 0626 66",
    "phone_link": "+919446062666",
    "email": "info@malabaroutes.com",
    "map_embed": "https://www.google.com/maps?q=10.166667,77.066667&z=10&output=embed",
    "map_directions": "https://www.google.com/maps/dir/?api=1&destination=10.166667,77.066667",
}


def verify_recaptcha(token, remote_ip=None):
    """Return True if Google confirms the reCAPTCHA token is valid."""
    if not token:
        return False

    payload = {
        "secret": settings.RECAPTCHA_SECRET_KEY,
        "response": token,
    }
    if remote_ip:
        payload["remoteip"] = remote_ip

    try:
        data = urllib.parse.urlencode(payload).encode()
        req = urllib.request.Request(
            "https://www.google.com/recaptcha/api/siteverify",
            data=data,
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode()).get("success", False)
    except Exception:
        return False


def contact(request):
    if request.method == "POST":
        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

        def fail(msg, status=400):
            if is_ajax:
                return JsonResponse({"ok": False, "error": msg}, status=status)
            messages.error(request, msg)
            return redirect("contact")

        def success():
            if is_ajax:
                return JsonResponse({"ok": True})
            messages.success(request, "Thank you! We have received your message.")
            return redirect("contact")

        # Honeypot: real visitors never fill this hidden field
        if request.POST.get("website"):
            return success()

        # reCAPTCHA check
        token = request.POST.get("g-recaptcha-response", "")
        if not verify_recaptcha(token, request.META.get("REMOTE_ADDR")):
            return fail("Please confirm that you are not a robot.")

        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()

        # ---- Required fields ----
        if not first_name or not last_name or not phone:
            return fail("First name, last name and phone are required.")

        # ---- Names: letters only, no numbers ----
        if not valid_name(first_name):
            return fail("First name should contain letters only, no numbers.")

        if not valid_name(last_name):
            return fail("Last name should contain letters only, no numbers.")

        # ---- Phone: 7 to 15 digits, optional leading + ----
        clean = clean_phone(phone)
        if not clean:
            return fail("Please enter a valid phone number (7 to 15 digits).")
        phone = clean

        # ---- Email (optional, but must be valid if given) ----
        if email:
            try:
                validate_email(email)
            except ValidationError:
                return fail("Please enter a valid email address.")

        # ---- Keep the message to a sane length ----
        message = message[:2000]

        # 1) Save first so the enquiry is never lost
        try:
            ContactMessage.objects.create(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                email=email or None,
                message=message,
            )
        except Exception:
            return fail("Could not save your message. Please try again.", 500)

        # 2) Email notification (a failure here must not hide the saved enquiry)
        body = (
            "New contact message from the website\n\n"
            f"Name: {first_name} {last_name}\n"
            f"Phone: {phone}\n"
            f"Email: {email or '-'}\n\n"
            f"Message:\n{message or '-'}\n"
        )
        recipient = getattr(
            settings,
            "CONTACT_NOTIFY_EMAIL",
            getattr(settings, "BOOKING_NOTIFY_EMAIL", settings.DEFAULT_FROM_EMAIL),
        )
        try:
            send_mail(
                subject=f"Contact enquiry - {first_name} {last_name}",
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
        except Exception:
            pass

        return success()

    return render(request, "frontends/contact.html", {
        "info": CONTACT_INFO,
        "recaptcha_site_key": settings.RECAPTCHA_SITE_KEY,
    })
def terms(request):
    return render(request, "frontends/terms.html", {
        
    })

def custom_404(request, exception=None):
    return render(request, "frontends/404.html", status=404)
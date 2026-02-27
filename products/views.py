import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from accounts.permissions import is_manager

from .forms import GalleryPhotoForm, HomeHeroUploadForm
from .models import Cake, EventPackage, GalleryPhoto


def customer_home(request):
    hero_upload_form = HomeHeroUploadForm()

    if request.method == "POST":
        if not request.user.is_authenticated or not is_manager(request.user):
            return render(request, "access_denied.html")

        hero_upload_form = HomeHeroUploadForm(request.POST, request.FILES)
        if hero_upload_form.is_valid():
            image_title = hero_upload_form.cleaned_data.get("title")
            GalleryPhoto.objects.create(
                title=image_title or f"Homepage Hero {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                image=hero_upload_form.cleaned_data["image"],
                uploaded_by=request.user,
                is_active=True,
                is_hero=True,
            )
            messages.success(request, "Homepage hero image updated.")
            return redirect("customer_home")

    featured_packages = (
        EventPackage.objects.select_related("category")
        .filter(is_active=True)
        .order_by("category__name", "package_set", "package_number")
    )

    set_map = {}
    for p in featured_packages:
        key = (p.category.name if p.category else "Uncategorized", p.package_set)
        if key not in set_map:
            set_map[key] = {
                "category": key[0],
                "set_name": key[1],
                "image": p.image,
                "start_price": p.base_price,
                "package_count": 1,
            }
        else:
            set_map[key]["package_count"] += 1
            if p.base_price < set_map[key]["start_price"]:
                set_map[key]["start_price"] = p.base_price
            if not set_map[key]["image"] and p.image:
                set_map[key]["image"] = p.image

    featured_sets = list(set_map.values())[:8]
    hero_photo = GalleryPhoto.objects.filter(
        is_hero=True,
        is_active=True,
        image__isnull=False,
    ).exclude(image="").first()
    hero_image = hero_photo.image if hero_photo else None

    return render(
        request,
        "products/customer_home.html",
        {
            "featured_sets": featured_sets,
            "hero_image": hero_image,
            "hero_upload_form": hero_upload_form,
        },
    )


def cake_list(request):
    cakes = Cake.objects.all()
    return render(request, "products/cake_list.html", {"cakes": cakes})


def get_season_recommendations():
    month = datetime.now().month
    if month == 12:
        return Cake.objects.filter(season_tags__name="Christmas")
    if month == 2:
        return Cake.objects.filter(season_tags__name="Valentine")
    if month in [3, 4, 5]:
        return Cake.objects.filter(season_tags__name="Graduation")
    return Cake.objects.all()


def gallery_view(request):
    photos = GalleryPhoto.objects.filter(
        is_active=True, image__isnull=False).exclude(image="")
    recommended_cakes = get_season_recommendations()
    all_cakes = Cake.objects.all()
    return render(
        request,
        "products/gallery.html",
        {"recommended_cakes": recommended_cakes,
            "all_cakes": all_cakes, "photos": photos},
    )


def product_photos_view(request):
    photos = GalleryPhoto.objects.filter(
        is_active=True, image__isnull=False).exclude(image="").order_by("-created_at")
    return render(request, "products/product_photos.html", {"photos": photos})


@login_required
def product_photo_delete(request, photo_id):
    if not is_manager(request.user):
        return render(request, "access_denied.html")

    if request.method != "POST":
        return redirect("product_photos")

    photo = get_object_or_404(GalleryPhoto, id=photo_id)
    photo.delete()
    messages.success(request, "Photo deleted.")
    return redirect("product_photos")


@login_required
def product_photo_set_hero(request, photo_id):
    if not is_manager(request.user):
        return render(request, "access_denied.html")

    if request.method != "POST":
        return redirect("gallery_manage")

    photo = get_object_or_404(GalleryPhoto, id=photo_id)
    photo.is_hero = True
    photo.save()
    messages.success(
        request, f'"{photo.title}" is now the homepage hero image.')
    return redirect("gallery_manage")


@login_required
def gallery_manage(request):
    if not is_manager(request.user):
        return render(request, "access_denied.html")
    form = GalleryPhotoForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        photo = form.save(commit=False)
        photo.uploaded_by = request.user
        photo.save()
        messages.success(request, "Gallery photo uploaded.")
    photos = GalleryPhoto.objects.all()
    return render(request, "products/gallery_manage.html", {"form": form, "photos": photos})


def package_list(request):
    packages = (
        EventPackage.objects.select_related("category")
        .prefetch_related("items", "season_tags")
        .filter(is_active=True)
        .order_by("-id")
    )

    def derived_category_name(package):
        text = f"{package.package_set} {package.name}".lower()

        if package.category and package.category.name == "Wedding":
            return "Wedding"

        if "party package" in text and (
            (package.category and package.category.name ==
             "Birthday") or not package.category
        ):
            return "Party Packages"

        if package.category:
            return package.category.name
        if "christening" in text:
            return "Christening"
        if "wedding" in text:
            return "Wedding"
        if "sweet corner" in text:
            return "Sweet Corner"
        if "birthday" in text:
            return "Birthday"
        return "Uncategorized"

    deduped = []
    seen = set()
    for package in packages:
        cat_name = derived_category_name(package)
        dedupe_key = (cat_name, package.package_set,
                      package.package_number or package.name)
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        package._derived_category_name = cat_name
        deduped.append(package)

    deduped.sort(key=lambda p: (p._derived_category_name,
                 p.package_set, p.package_number or 0, p.name))

    grouped = {}
    for package in deduped:
        category_name = package._derived_category_name
        grouped.setdefault(category_name, {})
        grouped[category_name].setdefault(package.package_set, [])
        grouped[category_name][package.package_set].append(package)

    grouped_packages = [
        {"category": category_name, "sets": [
            {"set_name": set_name, "packages": items} for set_name, items in sets.items()]}
        for category_name, sets in grouped.items()
    ]

    category_order = {
        "Birthday": 0,
        "Christening": 1,
        "Wedding": 2,
        "Sweet Corner": 3,
        "Party Packages": 4,
        "Uncategorized": 5,
    }
    grouped_packages.sort(
        key=lambda section: (
            category_order.get(section["category"], 99),
            section["category"].lower(),
        )
    )

    set_map = {}
    for p in packages:
        key = (p.category.name if p.category else "Uncategorized", p.package_set)
        if key not in set_map:
            set_map[key] = {
                "category": key[0],
                "set_name": key[1],
                "image": p.image,
                "start_price": p.base_price,
                "package_count": 1,
            }
        else:
            set_map[key]["package_count"] += 1
            if p.base_price < set_map[key]["start_price"]:
                set_map[key]["start_price"] = p.base_price
            if not set_map[key]["image"] and p.image:
                set_map[key]["image"] = p.image

    package_sets = sorted(set_map.values(), key=lambda x: (
        x["category"], x["set_name"]))

    return render(
        request,
        "products/package_list.html",
        {
            "grouped_packages": grouped_packages,
            "package_sets": package_sets,
        },
    )


def chatbot_page(request):
    return render(request, "products/chatbot.html")


def about_page(request):
    return render(request, "products/about.html")


def shop_location_page(request):
    return render(request, "products/shop_location.html")


def ai_recommendations_page(request):
    month = datetime.now().strftime("%B")
    packages = list(
        EventPackage.objects.filter(is_active=True).order_by("base_price")[:3]
    )
    match_scores = [95, 88, 84]
    recommendations = []
    for idx, package in enumerate(packages):
        recommendations.append(
            {
                "package": package,
                "match_score": match_scores[idx] if idx < len(match_scores) else 80,
            }
        )

    return render(
        request,
        "products/ai_recommendations.html",
        {"month": month, "recommendations": recommendations},
    )


@csrf_exempt
def chatbot_api(request):
    if request.method != "POST":
        return JsonResponse({"answer": "Invalid request."}, status=400)
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"answer": "Could not read message."}, status=400)

    question = (payload.get("question") or "").lower()
    if not question:
        return JsonResponse({"answer": "Please type your question."})

    if "price" in question or "how much" in question:
        cheapest = EventPackage.objects.filter(
            is_active=True).order_by("base_price").first()
        if cheapest:
            return JsonResponse(
                {"answer": f"Our packages start at P{cheapest.base_price}. You can browse full details in Event Packages."}
            )
    if "wedding" in question:
        count = EventPackage.objects.filter(
            is_active=True, category__name__icontains="wedding").count()
        return JsonResponse({"answer": f"We currently have {count} active Wedding packages."})
    if "birthday" in question:
        count = EventPackage.objects.filter(
            is_active=True, category__name__icontains="birthday").count()
        return JsonResponse({"answer": f"We currently have {count} active Birthday packages."})
    if "christening" in question:
        count = EventPackage.objects.filter(
            is_active=True, category__name__icontains="christening").count()
        return JsonResponse({"answer": f"We currently have {count} active Christening packages."})
    if "days" in question or "3 day" in question or "three day" in question:
        return JsonResponse({"answer": "Cake booking requires event date at least 3 days from today."})

    return JsonResponse(
        {"answer": "I can help with package categories, price range, and booking rules. Try: wedding packages, birthday packages, or minimum lead time."}
    )

import json
from collections import defaultdict
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from accounts.permissions import is_manager

from .forms import GalleryPhotoForm, HomeHeroUploadForm
from .models import Cake, EventPackage, GalleryPhoto


MONTH_OCCASION_MAP = {
    1: ["New Year"],
    2: ["Valentine", "Couples"],
    3: ["Graduation", "Engagement"],
    4: ["Wedding", "Anniversary"],
    5: ["Mother", "Graduation"],
    6: ["Father", "Wedding"],
    7: ["Siblings"],
    8: ["Couples", "Anniversary"],
    9: ["Wedding", "Engagement"],
    10: ["Halloween"],
    11: ["Thanksgiving", "Anniversary"],
    12: ["Christmas", "New Year"],
}


def get_month_occasions(month_number):
    return MONTH_OCCASION_MAP.get(month_number, ["Special Occasion"])


def _build_season_tag_query(occasion_keywords):
    query = Q()
    for keyword in occasion_keywords:
        query |= Q(season_tags__name__icontains=keyword)
    return query


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
    if not featured_packages.exists():
        featured_packages = EventPackage.objects.select_related("category").order_by(
            "category__name", "package_set", "package_number"
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
    month_number = datetime.now().month
    month_occasions = get_month_occasions(month_number)
    tagged_cakes = Cake.objects.filter(
        _build_season_tag_query(month_occasions)
    ).distinct()
    return tagged_cakes if tagged_cakes.exists() else Cake.objects.all()


def get_monthly_package_recommendations(month_number):
    month_occasions = get_month_occasions(month_number)
    tagged_packages = EventPackage.objects.filter(
        is_active=True
    ).filter(
        _build_season_tag_query(month_occasions)
    ).distinct().order_by("base_price")

    if tagged_packages.exists():
        return tagged_packages[:3]

    return EventPackage.objects.filter(is_active=True).order_by("base_price")[:3]


def _build_match_score(raw_score, base=55, cap=98):
    return max(base, min(cap, int(base + raw_score)))


def _get_user_package_signals(user):
    if not user.is_authenticated:
        return {}, set(), None

    from orders.models import OrderDetail

    history = list(
        OrderDetail.objects.filter(
            order__customer=user,
            order__status__in=["CONFIRMED", "COMPLETED"],
            package__isnull=False,
        )
        .select_related("package", "package__category")
    )
    if not history:
        return {}, set(), None

    package_qty = defaultdict(int)
    category_qty = defaultdict(int)
    weighted_price_total = 0
    weighted_qty_total = 0

    for row in history:
        qty = row.quantity or 1
        package_qty[row.package_id] += qty
        if row.package and row.package.category_id:
            category_qty[row.package.category_id] += qty
        weighted_price_total += float(row.price) * qty
        weighted_qty_total += qty

    preferred_categories = {
        cid for cid, _ in sorted(category_qty.items(), key=lambda kv: kv[1], reverse=True)[:2]
    }
    avg_price = (weighted_price_total /
                 weighted_qty_total) if weighted_qty_total else None
    return package_qty, preferred_categories, avg_price


def _get_user_cake_signals(user):
    if not user.is_authenticated:
        return {}, set(), None

    from orders.models import OrderDetail

    history = list(
        OrderDetail.objects.filter(
            order__customer=user,
            order__status__in=["CONFIRMED", "COMPLETED"],
            cake__isnull=False,
        )
        .select_related("cake", "cake__category")
    )
    if not history:
        return {}, set(), None

    cake_qty = defaultdict(int)
    flavor_qty = defaultdict(int)
    weighted_price_total = 0
    weighted_qty_total = 0

    for row in history:
        qty = row.quantity or 1
        cake_qty[row.cake_id] += qty
        if row.cake and row.cake.flavor:
            flavor_qty[row.cake.flavor.lower()] += qty
        weighted_price_total += float(row.price) * qty
        weighted_qty_total += qty

    preferred_flavors = {
        flavor for flavor, _ in sorted(flavor_qty.items(), key=lambda kv: kv[1], reverse=True)[:2]
    }
    avg_price = (weighted_price_total /
                 weighted_qty_total) if weighted_qty_total else None
    return cake_qty, preferred_flavors, avg_price


def get_rule_based_package_recommendations(user, month_occasions, limit=3):
    from orders.models import OrderDetail

    packages = list(
        EventPackage.objects.filter(is_active=True)
        .select_related("category")
        .prefetch_related("season_tags")
    )
    if not packages:
        return []

    package_map = {pkg.id: pkg for pkg in packages}
    scores = defaultdict(float)
    reasons = defaultdict(list)

    seasonal_ids = set(
        EventPackage.objects.filter(is_active=True)
        .filter(_build_season_tag_query(month_occasions))
        .values_list("id", flat=True)
    )
    for pid in seasonal_ids:
        scores[pid] += 14
        reasons[pid].append("Seasonal match")

    best_sellers = (
        OrderDetail.objects.filter(
            order__status__in=["CONFIRMED", "COMPLETED"], package__isnull=False
        )
        .values("package_id")
        .annotate(total_qty=Sum("quantity"))
        .order_by("-total_qty")[:10]
    )
    for rank, row in enumerate(best_sellers):
        pid = row["package_id"]
        if pid in package_map:
            scores[pid] += max(12 - rank, 3)
            reasons[pid].append("Best-selling package")

    user_pkg_qty, preferred_categories, avg_price = _get_user_package_signals(
        user)
    for pid, qty in user_pkg_qty.items():
        if pid in package_map:
            scores[pid] += min(qty * 10, 35)
            reasons[pid].append("Based on your previous orders")

    for pkg in packages:
        if pkg.category_id and pkg.category_id in preferred_categories:
            scores[pkg.id] += 8
            reasons[pkg.id].append("Matches preferred event category")

        if avg_price:
            distance = abs(float(pkg.base_price) - avg_price)
            if distance <= 500:
                scores[pkg.id] += 6
                reasons[pkg.id].append("Within your typical budget range")

    ranked = sorted(
        packages, key=lambda p: (-scores[p.id], p.base_price, p.name))[:limit]
    if not ranked:
        return []

    recommendations = []
    for pkg in ranked:
        rec_reasons = reasons[pkg.id][:2] or ["Trending recommendation"]
        recommendations.append(
            {
                "package": pkg,
                "match_score": _build_match_score(scores[pkg.id]),
                "reasons": rec_reasons,
            }
        )
    return recommendations


def get_rule_based_cake_recommendations(user, month_occasions, limit=3):
    from orders.models import OrderDetail

    cakes = list(Cake.objects.all().prefetch_related("season_tags"))
    if not cakes:
        return []

    cake_map = {cake.id: cake for cake in cakes}
    scores = defaultdict(float)
    reasons = defaultdict(list)

    seasonal_ids = set(
        Cake.objects.filter(_build_season_tag_query(
            month_occasions)).values_list("id", flat=True)
    )
    for cid in seasonal_ids:
        scores[cid] += 12
        reasons[cid].append("Seasonal cake design")

    best_sellers = (
        OrderDetail.objects.filter(
            order__status__in=["CONFIRMED", "COMPLETED"], cake__isnull=False)
        .values("cake_id")
        .annotate(total_qty=Sum("quantity"))
        .order_by("-total_qty")[:10]
    )
    for rank, row in enumerate(best_sellers):
        cid = row["cake_id"]
        if cid in cake_map:
            scores[cid] += max(10 - rank, 3)
            reasons[cid].append("Best-selling cake")

    user_cake_qty, preferred_flavors, avg_price = _get_user_cake_signals(user)
    for cid, qty in user_cake_qty.items():
        if cid in cake_map:
            scores[cid] += min(qty * 10, 35)
            reasons[cid].append("Based on your previous orders")

    for cake in cakes:
        if cake.flavor and cake.flavor.lower() in preferred_flavors:
            scores[cake.id] += 8
            reasons[cake.id].append("Matches your preferred flavor")

        if avg_price:
            distance = abs(float(cake.base_price) - avg_price)
            if distance <= 300:
                scores[cake.id] += 6
                reasons[cake.id].append("Within your typical budget range")

    ranked = sorted(
        cakes, key=lambda c: (-scores[c.id], c.base_price, c.name))[:limit]
    if not ranked:
        return []

    recommendations = []
    for cake in ranked:
        rec_reasons = reasons[cake.id][:2] or ["Trending recommendation"]
        recommendations.append(
            {
                "cake": cake,
                "match_score": _build_match_score(scores[cake.id]),
                "reasons": rec_reasons,
            }
        )
    return recommendations


def _get_package_recommendation_debug_rows(user, month_occasions, limit=10):
    from orders.models import OrderDetail

    packages = list(
        EventPackage.objects.filter(is_active=True)
        .select_related("category")
        .prefetch_related("season_tags")
    )
    if not packages:
        return []

    seasonal_ids = set(
        EventPackage.objects.filter(is_active=True)
        .filter(_build_season_tag_query(month_occasions))
        .values_list("id", flat=True)
    )

    bestseller_rank = {}
    best_sellers = (
        OrderDetail.objects.filter(
            order__status__in=["CONFIRMED", "COMPLETED"], package__isnull=False
        )
        .values("package_id")
        .annotate(total_qty=Sum("quantity"))
        .order_by("-total_qty")[:20]
    )
    for rank, row in enumerate(best_sellers):
        bestseller_rank[row["package_id"]] = rank

    user_pkg_qty, preferred_categories, avg_price = _get_user_package_signals(
        user)

    rows = []
    for pkg in packages:
        history_score = min(user_pkg_qty.get(pkg.id, 0) * 10, 35)
        seasonal_score = 14 if pkg.id in seasonal_ids else 0

        rank = bestseller_rank.get(pkg.id)
        bestseller_score = max(12 - rank, 3) if rank is not None else 0

        category_score = 8 if pkg.category_id and pkg.category_id in preferred_categories else 0

        budget_score = 0
        if avg_price is not None:
            distance = abs(float(pkg.base_price) - avg_price)
            if distance <= 500:
                budget_score = 6

        raw_score = history_score + seasonal_score + \
            bestseller_score + category_score + budget_score
        rows.append(
            {
                "name": pkg.name,
                "category": pkg.category.name if pkg.category else "Uncategorized",
                "price": pkg.base_price,
                "history_score": history_score,
                "bestseller_score": bestseller_score,
                "seasonal_score": seasonal_score,
                "category_score": category_score,
                "budget_score": budget_score,
                "raw_score": raw_score,
                "match_score": _build_match_score(raw_score),
            }
        )

    rows.sort(key=lambda row: (-row["raw_score"], row["price"], row["name"]))
    return rows[:limit]


def _get_cake_recommendation_debug_rows(user, month_occasions, limit=10):
    from orders.models import OrderDetail

    cakes = list(Cake.objects.all().prefetch_related("season_tags"))
    if not cakes:
        return []

    seasonal_ids = set(
        Cake.objects.filter(_build_season_tag_query(
            month_occasions)).values_list("id", flat=True)
    )

    bestseller_rank = {}
    best_sellers = (
        OrderDetail.objects.filter(
            order__status__in=["CONFIRMED", "COMPLETED"], cake__isnull=False)
        .values("cake_id")
        .annotate(total_qty=Sum("quantity"))
        .order_by("-total_qty")[:20]
    )
    for rank, row in enumerate(best_sellers):
        bestseller_rank[row["cake_id"]] = rank

    user_cake_qty, preferred_flavors, avg_price = _get_user_cake_signals(user)

    rows = []
    for cake in cakes:
        history_score = min(user_cake_qty.get(cake.id, 0) * 10, 35)
        seasonal_score = 12 if cake.id in seasonal_ids else 0

        rank = bestseller_rank.get(cake.id)
        bestseller_score = max(10 - rank, 3) if rank is not None else 0

        flavor_score = 8 if cake.flavor and cake.flavor.lower() in preferred_flavors else 0

        budget_score = 0
        if avg_price is not None:
            distance = abs(float(cake.base_price) - avg_price)
            if distance <= 300:
                budget_score = 6

        raw_score = history_score + seasonal_score + \
            bestseller_score + flavor_score + budget_score
        rows.append(
            {
                "name": cake.name,
                "flavor": cake.flavor,
                "price": cake.base_price,
                "history_score": history_score,
                "bestseller_score": bestseller_score,
                "seasonal_score": seasonal_score,
                "flavor_score": flavor_score,
                "budget_score": budget_score,
                "raw_score": raw_score,
                "match_score": _build_match_score(raw_score),
            }
        )

    rows.sort(key=lambda row: (-row["raw_score"], row["price"], row["name"]))
    return rows[:limit]


@login_required
def recommendation_debug_panel(request):
    if not is_manager(request.user):
        return render(request, "access_denied.html")

    month_number = datetime.now().month
    month = datetime.now().strftime("%B")
    month_occasions = get_month_occasions(month_number)

    user_candidates = User.objects.filter(
        order__isnull=False).distinct().order_by("username")

    selected_user = request.user
    selected_user_id = request.GET.get("user_id")
    if selected_user_id:
        try:
            selected_user = user_candidates.get(id=int(selected_user_id))
        except (ValueError, User.DoesNotExist):
            selected_user = request.user

    package_rows = _get_package_recommendation_debug_rows(
        selected_user, month_occasions, limit=12)
    cake_rows = _get_cake_recommendation_debug_rows(
        selected_user, month_occasions, limit=12)

    return render(
        request,
        "products/recommendation_debug.html",
        {
            "month": month,
            "month_occasions": month_occasions,
            "selected_user": selected_user,
            "user_candidates": user_candidates,
            "package_rows": package_rows,
            "cake_rows": cake_rows,
        },
    )


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
    if not packages.exists():
        packages = (
            EventPackage.objects.select_related("category")
            .prefetch_related("items", "season_tags")
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
    month_number = datetime.now().month
    month = datetime.now().strftime("%B")
    month_occasions = get_month_occasions(month_number)
    recommendations = get_rule_based_package_recommendations(
        request.user, month_occasions, limit=3
    )
    cake_recommendations = get_rule_based_cake_recommendations(
        request.user, month_occasions, limit=3
    )

    if not recommendations:
        fallback_packages = list(
            get_monthly_package_recommendations(month_number))
        recommendations = [
            {
                "package": pkg,
                "match_score": 75,
                "reasons": ["Seasonal fallback recommendation"],
            }
            for pkg in fallback_packages
        ]

    has_personalized_history = request.user.is_authenticated and any(
        "Based on your previous orders" in reason
        for rec in (recommendations + cake_recommendations)
        for reason in rec.get("reasons", [])
    )

    recommendation_basis = (
        "Personalized using your previous orders and best-selling items"
        if has_personalized_history
        else "Based on seasonal trends and best-selling items"
    )

    return render(
        request,
        "products/ai_recommendations.html",
        {
            "month": month,
            "month_occasions": month_occasions,
            "recommendations": recommendations,
            "cake_recommendations": cake_recommendations,
            "recommendation_basis": recommendation_basis,
        },
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

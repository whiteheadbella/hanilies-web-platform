from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from decimal import Decimal

from accounts.permissions import is_manager
from .forms import CustomizationForm
from products.models import AddOnCategory, AddOnItem, Cake


@login_required
def remove_addon_item(request, addon_id):
    if not is_manager(request.user):
        return render(request, "access_denied.html")

    if request.method != "POST":
        return redirect("customize_cake")

    addon = get_object_or_404(AddOnItem, id=addon_id)
    addon_name = addon.name
    addon.delete()
    messages.success(request, f"Add-on '{addon_name}' removed.")
    return redirect("customize_cake")


@login_required
def customize_cake(request):

    form = CustomizationForm(
        request.POST or None,
        request.FILES or None
    )
    selected_add_ons = set(str(v) for v in (form["add_ons"].value() or []))

    base_price = 0  # Prevent template errors on initial load

    if request.method == "POST" and form.is_valid():

        customization = form.save(commit=False)
        cake = customization.cake

        base_price = cake.base_price
        quantity = customization.quantity  # NEW

        # Pricing rules
        size_multiplier = {
            "SMALL": Decimal("1.0"),
            "MEDIUM": Decimal("1.2"),
            "LARGE": Decimal("1.5"),
        }

        layer_multiplier = {
            "1": Decimal("1.0"),
            "2": Decimal("1.4"),
            "3": Decimal("1.8"),
        }

        size_multi = size_multiplier.get(customization.size, Decimal("1.0"))
        layer_multi = layer_multiplier.get(
            customization.layers, Decimal("1.0"))

        # Save BEFORE ManyToMany operations
        customization.price = base_price * size_multi * layer_multi
        customization.save()

        # Save ManyToMany Add-Ons
        form.save_m2m()

        # Add-On pricing
        addon_total = sum(addon.price for addon in customization.add_ons.all())

        customization.price += addon_total

        # Quantity multiplier (CRITICAL)
        customization.price *= quantity

        customization.save()

        if request.POST.get("submit_action") == "add_to_cart":
            return redirect("add_customization_to_cart", customization_id=customization.id)

        from orders.models import CartItem

        cart_item = CartItem.objects.filter(
            customer=request.user,
            customization=customization,
        ).first()
        if not cart_item:
            CartItem.objects.create(
                customer=request.user,
                customization=customization,
                quantity=1,
                unit_price=customization.price,
            )

        return redirect("cart_view")

    addon_categories = AddOnCategory.objects.prefetch_related(
        "addonitem_set").all()
    category_priority = {
        "Decor": 0,
        "Food and Desserts": 1,
        "General": 2,
    }
    sorted_categories = sorted(
        addon_categories,
        key=lambda category: (
            category_priority.get(category.name, 99),
            category.name.lower(),
        ),
    )

    addon_category_sections = []
    for category in sorted_categories:
        hidden_categories = {"general", "decor", "food and desserts"}
        category_key = category.name.strip().lower()
        if category_key in hidden_categories:
            continue

        disable_manage_actions = (
            ("services" in category_key and "entertainment" in category_key)
            or ("giveaways" in category_key and "prints" in category_key)
        )
        show_event_packages_link = (
            ("adult" in category_key and "birthday" in category_key and "package" in category_key)
            or ("christening" in category_key and "package" in category_key)
            or ("sweet corner" in category_key and "adult" in category_key and "package" in category_key)
            or ("sweet corner" in category_key and "kids" in category_key and "birthday" in category_key and "package" in category_key)
            or ("party" in category_key and "package" in category_key)
            or ("wedding" in category_key and "package" in category_key)
        )

        seen_names = set()
        unique_items = []
        for addon in category.addonitem_set.all().order_by("name"):
            name_key = addon.name.strip().lower()
            if name_key in seen_names:
                continue
            seen_names.add(name_key)
            unique_items.append(addon)
        addon_category_sections.append({
            "name": category.name,
            "items": unique_items,
            "allow_manage_actions": not disable_manage_actions,
            "show_event_packages_link": show_event_packages_link,
        })

    cakes = Cake.objects.all().values("id", "base_price")
    cake_prices = {str(c["id"]): str(c["base_price"]) for c in cakes}

    return render(request, "customization/customize.html", {
        "form": form,
        "base_price": base_price,
        "addon_category_sections": addon_category_sections,
        "selected_add_ons": selected_add_ons,
        "cake_prices": cake_prices,
    })

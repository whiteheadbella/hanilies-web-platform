from django.contrib import admin
from .models import (
    SeasonTag,
    CakeCategory,
    Cake,
    EventCategory,
    EventPackage,
    EventPackageItem,
    GalleryPhoto,
    AddOnCategory,
    AddOnItem
)


# -------------------------
# SEASON TAG ADMIN
# -------------------------
@admin.register(SeasonTag)
class SeasonTagAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


# -------------------------
# CAKE CATEGORY ADMIN
# -------------------------
@admin.register(CakeCategory)
class CakeCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    search_fields = ("name",)


# -------------------------
# CAKE ADMIN
# -------------------------
@admin.register(Cake)
class CakeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "size", "flavor", "base_price")
    list_filter = ("category", "season_tags")
    search_fields = ("name", "flavor")
    filter_horizontal = ("season_tags",)  # ⭐ Important for ManyToMany UI


# -------------------------
# EVENT CATEGORY ADMIN
# -------------------------
@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    search_fields = ("name",)


# -------------------------
# EVENT PACKAGE ADMIN
# -------------------------
class EventPackageItemInline(admin.TabularInline):
    model = EventPackageItem
    extra = 0
    fields = ("item_group", "item_name", "quantity",
              "unit", "unit_price", "notes")


@admin.register(EventPackage)
class EventPackageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "category",
        "package_set",
        "package_number",
        "name",
        "base_price",
        "is_active",
    )
    list_filter = ("category", "package_set", "is_active", "season_tags")
    search_fields = ("name", "theme_style", "description", "inclusions")
    filter_horizontal = ("season_tags",)
    inlines = [EventPackageItemInline]
    readonly_fields = ()


@admin.register(GalleryPhoto)
class GalleryPhotoAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "uploaded_by",
                    "is_active", "is_hero", "created_at")
    list_filter = ("is_active", "is_hero")
    search_fields = ("title",)


# -------------------------
# ADD-ON CATEGORY ADMIN
# -------------------------
@admin.register(AddOnCategory)
class AddOnCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


# -------------------------
# ADD-ON ITEM ADMIN
# -------------------------
@admin.register(AddOnItem)
class AddOnItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "price")
    list_filter = ("category",)
    search_fields = ("name",)

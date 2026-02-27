import re

from django.core.management.base import BaseCommand

from products.models import (
    AddOnCategory,
    AddOnItem,
    EventCategory,
    EventPackage,
    EventPackageItem,
)


SEED_DATA = [
    {
        "category": "Sweet Corner",
        "category_description": "Dessert-focused event package bundles.",
        "package_set": "Hanilie's Sweet Corner Kid's B-Day",
        "theme_style": "Kids Birthday",
        "duration_hours": "3 to 4 hours from the start of the party",
        "packages": [
            {
                "package_number": 1,
                "name": "Hanilies Sweet Corner Package 1 (Kids)",
                "base_price": "4500.00",
                "description": "Starter sweet corner package with table setup.",
                "inclusions": [
                    "1 Chocolate Fountain",
                    "1 Jar Wafer Stick",
                    "24 Marshmallow on stick",
                    "24 Chocofudge Brownies",
                    "24 Themed Cupcakes",
                    "24 Chocochip Cookies",
                    "4 Kinds gummies/gums",
                    "24 Mini sliced cakes with frosting",
                    "With table setup",
                ],
            },
            {
                "package_number": 2,
                "name": "Hanilies Sweet Corner Package 2 (Kids)",
                "base_price": "6500.00",
                "description": "Mid sweet corner package with upgraded quantities.",
                "inclusions": [
                    "1 Chocolate Fountain",
                    "1 Jar Wafer Stick",
                    "30 Marshmallow on stick",
                    "30 Chocofudge Brownies",
                    "30 Themed Cupcakes",
                    "30 Chocochip Cookies",
                    "4 Kinds gummies/gums",
                    "30 Mini sliced cakes (Pandan) with frosting",
                    "30 Mini sliced cakes (Ube) with frosting",
                    "12 Blueberry shots",
                ],
            },
            {
                "package_number": 3,
                "name": "Hanilies Sweet Corner Package 3 (Kids)",
                "base_price": "9000.00",
                "description": "Premium sweet corner package.",
                "inclusions": [
                    "2 pcs themed cake (round 7\")",
                    "1 Chocolate Fountain",
                    "1 Jar Wafer Stick",
                    "36 Marshmallow on stick",
                    "36 Chocofudge Brownies",
                    "36 Themed Cupcakes",
                    "36 Chocochip Cookies",
                    "4 Kinds gummies/gums",
                    "36 Mini sliced cakes (Pandan) with frosting",
                    "36 Mini sliced cakes (Mocha) with frosting",
                    "15 Blueberry shots",
                    "15 Cake pops",
                ],
            },
        ],
    },
    {
        "category": "Sweet Corner",
        "category_description": "Dessert-focused event package bundles.",
        "package_set": "Hanilies Sweet Corner - Theme Adult",
        "theme_style": "Adults / Sweet Corner",
        "duration_hours": "3 to 4 hours from the start of the party",
        "packages": [
            {
                "package_number": 1,
                "name": "Hanilies Sweet Corner Package 1 (Basic)",
                "base_price": "4500.00",
                "description": "Theme: Adults / Sweet Corner / Basic Setup",
                "inclusions": [
                    "1 Tier Cake (8*3)",
                    "24 pcs Choco Fudge Brownies",
                    "24 pcs Cupcakes with Frosting",
                    "24 pcs Choco Chip Cookies",
                    "24 pcs Mini Sliced Cakes with Frosting",
                    "Table setup (for all events only 3-4 hours from the start of the party)",
                ],
            },
            {
                "package_number": 2,
                "name": "Hanilies Sweet Corner Package 2 (Standard)",
                "base_price": "6500.00",
                "description": "Theme: Sweet Corner / Standard Setup",
                "inclusions": [
                    "1 Tier Cake (9*3)",
                    "30 pcs Choco Fudge Brownies",
                    "30 pcs Cupcakes with Frosting",
                    "30 pcs Choco Chip Cookies",
                    "30 pcs Mini Sliced Cakes (Pandan)",
                    "30 pcs Mini Sliced Cakes (Ube)",
                    "Table setup (for all events only 3-4 hours from the start of the party)",
                ],
            },
            {
                "package_number": 3,
                "name": "Hanilies Sweet Corner Package 3 (Premium)",
                "base_price": "8500.00",
                "description": "Theme: Sweet Corner / Premium Setup",
                "inclusions": [
                    "2 Tier Cake (8*3 and 6*3)",
                    "36 pcs Choco Fudge Brownies",
                    "36 pcs Cupcakes with Frosting",
                    "36 pcs Choco Chip Cookies",
                    "36 pcs Mini Sliced Cakes (Pandan)",
                    "15 Blueberry shots",
                    "15 Mango shots",
                    "Table setup (for all events only 3-4 hours from the start of the party)",
                ],
            },
        ],
    },
    {
        "category": "Christening",
        "category_description": "Christening event packages.",
        "package_set": "Christening Packages",
        "theme_style": "Christening",
        "duration_hours": "3 to 4 hours from the start of the party",
        "packages": [
            {
                "package_number": 1,
                "name": "Christening Package A",
                "base_price": "6999.00",
                "description": "Theme: Christening / Standard Setup",
                "inclusions": [
                    "1 Tier Round Cake (8\")",
                    "18 pcs Cupcakes with Icing & Topper",
                    "18 pcs Loli Balloons with Print",
                    "2 Pillar Balloons",
                    "18 pcs Souvenir Baby Bottles with Celebrant's Picture",
                    "Backdrop Decor",
                    "Choice of 2x3 Tarp or Name of Celebrant",
                    "Free Use of Stage Lights & Accessories",
                ],
            },
            {
                "package_number": 2,
                "name": "Christening Package B",
                "base_price": "9999.00",
                "description": "Theme: Christening / Enhanced Setup",
                "inclusions": [
                    "2 Tier Round Cake (8\" / 6\")",
                    "24 pcs Cupcakes with Icing & Topper",
                    "24 pcs Loli Balloons with Print",
                    "2 Pillar Balloons",
                    "8 pcs Centerpiece Balloons",
                    "24 pcs Souvenir Baby Bottles with Celebrant's Picture",
                    "Table Setup & Backdrop Decor",
                    "Choice of 3x4 Tarp or Name of Celebrant",
                    "Free Use of Stage Lights & Accessories",
                ],
            },
            {
                "package_number": 3,
                "name": "Christening Package C",
                "base_price": "12999.00",
                "description": "Theme: Christening / Premium Full Setup",
                "inclusions": [
                    "3 Tier Round Cake (8\" / 7\" / 4\")",
                    "30 pcs Cupcakes with Icing & Topper",
                    "36 pcs Loli Balloons with Print",
                    "Stage Garland Balloons",
                    "36 pcs Souvenir Baby Bottles with Celebrant's Picture",
                    "20 pcs Invitations",
                    "Sweet Corner: Chocolate Fountain",
                    "30 pcs Mini Brownies",
                    "30 pcs Mini Donuts",
                    "10 pcs Custom Cookies",
                    "1 bottle Wafer Sticks",
                    "20 pcs Marshmallow on Stick",
                    "5 packs Gummy",
                    "Table Setup & Backdrop Decor",
                    "Choice of 3x4 Tarp or Name of Celebrant",
                    "Free Use of Stage Decoration, Lights & Accessories",
                ],
            },
        ],
    },
    {
        "category": "Birthday",
        "category_description": "Birthday event setup packages.",
        "package_set": "Party Packages",
        "theme_style": "Kids Party",
        "duration_hours": "3 to 4 hours from the start of the party",
        "packages": [
            {
                "package_number": 1,
                "name": "Party Package 1",
                "base_price": "5900.00",
                "description": "Entry-level themed birthday package.",
                "inclusions": [
                    "1 Layer themed cake",
                    "12 Theme cupcakes",
                    "12 Balloons with print",
                    "1 Table setup with skirting",
                    "Use of 3 kiddie tables and 12 chairs",
                    "Lights and sounds",
                ],
            },
            {
                "package_number": 2,
                "name": "Party Package 2",
                "base_price": "8900.00",
                "description": "Balanced party package with mascot and activities.",
                "inclusions": [
                    "2 Tier themed cake (8\" and 6\")",
                    "18 Theme cupcakes",
                    "1 Mascot",
                    "16 Balloons with print",
                    "1 Pinata",
                    "1 Pabitin",
                    "Lights and sounds",
                    "Table setup and decor",
                    "Use of 4 tables with 16 chairs",
                ],
            },
            {
                "package_number": 3,
                "name": "Party Package 3",
                "base_price": "10900.00",
                "description": "Full birthday package with sweet corner and venue styling.",
                "inclusions": [
                    "2 Tier themed cake (9\" and 6\")",
                    "24 Colored balloons",
                    "24 Loot bags with goodies",
                    "24 Party hats",
                    "1 Mascot",
                    "5 Games with prizes",
                    "1 Pinata and 1 Pabitin",
                    "Table setup and dessert corner",
                    "Chocolate fountain",
                    "30 Brownies",
                    "30 Cookies",
                    "4 Kinds gummies",
                    "1 Jar wafer stick",
                    "20 Marshmallows",
                    "Stage and table decoration",
                    "Use of 5 tables and 20 chairs",
                    "Lights and sounds",
                ],
            },
            {
                "package_number": 4,
                "name": "Party Package 4",
                "base_price": "14900.00",
                "description": "Large event package with host and expanded dessert corner.",
                "inclusions": [
                    "3 Tier themed cake (14\", 7\", 5\")",
                    "30 Theme cupcakes",
                    "1 Mascot",
                    "1 Host",
                    "6 Games with prizes",
                    "Pinata and Pabitin",
                    "30 Balloons with print",
                    "30 Loot bags",
                    "30 Party hats",
                    "Dessert corner",
                    "20 Marshmallow pops",
                    "40 Brownies",
                    "40 Cookies",
                    "40 Gummies",
                    "20 Marshmallow sticks",
                    "1 Jar wafer stick",
                    "Stage and venue decoration",
                    "10 Centerpieces",
                    "Free use of 20 kiddie chairs and 7 tables",
                    "Lights and sounds",
                ],
            },
            {
                "package_number": 5,
                "name": "Party Package 5",
                "base_price": "18900.00",
                "description": "Premium party package with full venue decor and larger dessert corner.",
                "inclusions": [
                    "3 Tier themed cake (10\")",
                    "40 Theme cupcakes",
                    "40 Balloons with print",
                    "40 Loot bags",
                    "40 Party hats",
                    "40 Giveaways",
                    "6 Games with prizes",
                    "1 Pinata and 1 Pabitin",
                    "Dessert corner",
                    "10 Choco fountain",
                    "40 Marshmallow pops",
                    "40 Brownies",
                    "40 Macarons",
                    "40 Cookies",
                    "4 Gummies",
                    "1 Jar wafer stick",
                    "Balloon and table setup",
                    "Whole venue decoration",
                    "12 Centerpieces",
                    "Free use of 40 kiddie chairs, 10 tables, lights and sounds",
                ],
            },
            {
                "package_number": 6,
                "name": "Party Package 6",
                "base_price": "25000.00",
                "description": "Top-tier party package with extensive decor and activities.",
                "inclusions": [
                    "3 Tier themed cake",
                    "50 Balloons with print",
                    "50 Theme cupcakes",
                    "50 Invitations",
                    "50 Loot bags",
                    "1 Pinata",
                    "1 Pabitin",
                    "9 Games",
                    "Dessert corner",
                    "Choco fountain",
                    "40 Cookies",
                    "40 Brownies",
                    "4 Gummies",
                    "Marshmallow pops",
                    "Chocolate fountain",
                    "Bubble machine",
                    "2 Mascots",
                    "1 Host",
                    "Stage and whole venue decor",
                    "15 Centerpieces",
                    "2 Letter standees",
                    "Photo setup and photobooth",
                    "Unlimited photo and print package",
                    "Free use of 4 kiddie chairs, 12 tables, lights and sounds",
                ],
            },
        ],
    },
    {
        "category": "Birthday",
        "category_description": "Birthday event setup packages.",
        "package_set": "Birthday Package Adult",
        "theme_style": "Adult Birthday",
        "duration_hours": "3 to 4 hours from the start of the party",
        "packages": [
            {
                "package_number": 1,
                "name": "Adult Birthday Package A",
                "base_price": "5999.00",
                "description": "Theme: Adult / Minimalist / Elegant",
                "inclusions": [
                    "1 Tier Cake with 15 Cupcakes",
                    "Table Setup",
                    "Stage Decoration",
                    "Name & Age of Celebrant",
                    "1 set Pillar Balloons",
                    "12 pcs Balloons with Print",
                    "Stage Accessories",
                    "Artificial Flowers",
                    "Grass Balls",
                    "Lights & Sounds",
                    "Pillar stand",
                ],
            },
            {
                "package_number": 2,
                "name": "Adult Birthday Package B",
                "base_price": "8999.00",
                "description": "Theme: Standard Theme",
                "inclusions": [
                    "2 Tier Cake with 24 Cupcakes",
                    "Table Setup",
                    "Stage Decoration",
                    "Name & Age of Celebrant",
                    "1 Garland Balloon",
                    "18 pcs Balloons with Print",
                    "Stage Accessories",
                    "Artificial Flowers",
                    "Grass Balls",
                    "Lights & Sounds",
                    "Pillar stand",
                ],
            },
            {
                "package_number": 3,
                "name": "Adult Birthday Package C",
                "base_price": "12999.00",
                "description": "Theme: Premium Birthday / Full Setup",
                "inclusions": [
                    "3 Tier Cake with 30 Cupcakes",
                    "Table Setup",
                    "Sweet Corner",
                    "30 pcs Brownies",
                    "30 pcs Mini Cakes",
                    "30 pcs Macarons",
                    "30 pcs Choco Chip Cookies",
                    "Chocolate Fountain",
                    "Wafer Sticks",
                    "Gummies",
                    "Stage Decoration",
                    "Name & Age of Celebrant",
                    "1 Garland Balloon",
                    "24 pcs Balloons with Print",
                    "Stage Accessories",
                    "Artificial Flowers",
                    "Grass Balls",
                    "Lights & Sounds",
                    "Pillar stand",
                ],
            },
        ],
    },
    {
        "category": "Wedding",
        "category_description": "Wedding reception and venue styling packages.",
        "package_set": "Wedding Packages",
        "theme_style": "Wedding",
        "duration_hours": "3 to 4 hours from the start of the event",
        "packages": [
            {
                "package_number": 1,
                "name": "Package 1",
                "base_price": "10000.00",
                "description": "Wedding starter package.",
                "inclusions": [
                    "Venue stage decor with lights and accessories",
                    "2 Tier cake with wine",
                    "Groom and bride table",
                    "Cake table",
                    "Parents table",
                    "Gift table",
                ],
            },
            {
                "package_number": 2,
                "name": "Package 2",
                "base_price": "15000.00",
                "description": "Wedding package with red carpet and upgraded setup.",
                "inclusions": [
                    "Stage decor with red carpet and lights",
                    "2 VIP tables",
                    "Groom and bride table",
                    "Cake table",
                    "Parents table",
                    "Gift table",
                    "2 Tier cake (flavor of your choice) with wine",
                ],
            },
            {
                "package_number": 3,
                "name": "Package 3",
                "base_price": "25000.00",
                "description": "Whole venue decor package.",
                "inclusions": [
                    "Whole venue decor",
                    "Welcome signage",
                    "Ceiling decor",
                    "Red carpet",
                    "Accessories and lights",
                    "2 VIP tables",
                    "Groom and bride table",
                    "Cake table",
                    "Parents table",
                    "Gift table",
                    "3 Tier cake with wine",
                ],
            },
            {
                "package_number": 4,
                "name": "Package 4",
                "base_price": "45000.00",
                "description": "Church and whole venue decor with sweet corner.",
                "inclusions": [
                    "Church and whole venue decor",
                    "Red carpet with welcome signage",
                    "Ceiling decor and lights",
                    "2 VIP tables",
                    "Groom and bride table",
                    "Cake table",
                    "Parents table",
                    "Gift table",
                    "Sweet corner",
                    "3 Tier cake with wine",
                    "50 Brownies",
                    "50 Slice cakes (flavor of your choice)",
                    "50 Cookies",
                    "50 Cupcakes (flavor of your choice)",
                ],
            },
            {
                "package_number": 5,
                "name": "Package 5",
                "base_price": "85000.00",
                "description": "Premium church and venue package with entourage inclusions.",
                "inclusions": [
                    "Church and whole venue decor",
                    "Red carpet with welcome signage",
                    "Ceiling decor and lights",
                    "Entourage dresses with accessories",
                    "Bridal car",
                    "50 Invitations",
                    "Bouquet and corsage on wedding day",
                    "Coordinator and makeup",
                    "2 VIP tables",
                    "Groom and bride table",
                    "Cake table",
                    "Parents table",
                    "Gift table",
                    "Sweet corner with 3 Tier cake and wine",
                    "80 Brownies",
                    "80 Slice cakes (flavor of your choice)",
                    "80 Cookies",
                    "80 Cupcakes (flavor of your choice)",
                    "Optional add-ons: Photographer, photobooth, lights and sound system, souvenirs",
                ],
            },
        ],
    },
]


def infer_group(text: str) -> str:
    lower = text.lower()
    if any(k in lower for k in ["cake", "cupcake", "brownies", "cookies", "donut", "macaron", "gummy", "marshmallow"]):
        return "Food and Desserts"
    if any(k in lower for k in ["balloon", "garland", "centerpiece", "backdrop", "decor", "stage", "table setup", "tarp"]):
        return "Decor"
    if any(k in lower for k in ["host", "photobooth", "coordinator", "mascot", "lights", "sounds"]):
        return "Services and Entertainment"
    if any(k in lower for k in ["invitation", "souvenir", "loot bag", "party hat"]):
        return "Giveaways and Prints"
    return "General"


def parse_line(line: str):
    clean = line.strip(" -")
    quantity = None
    unit = ""
    name = clean

    m = re.match(r"^(?P<qty>\d+)\s*(?P<unit>pcs|pc|packs|set|sets|jar|bottle)?\s*(?P<name>.+)$", clean, re.IGNORECASE)
    if m:
        quantity = int(m.group("qty"))
        unit = (m.group("unit") or "").lower()
        name = m.group("name").strip(" -")
    else:
        m2 = re.match(r"^(?P<name>.+?)\s*[-:]\s*(?P<qty>\d+)\s*(?P<unit>pcs|pc|packs|set|sets)?$", clean, re.IGNORECASE)
        if m2:
            name = m2.group("name").strip()
            quantity = int(m2.group("qty"))
            unit = (m2.group("unit") or "").lower()

    return {
        "item_group": infer_group(clean),
        "item_name": name,
        "quantity": quantity,
        "unit": unit,
        "notes": "",
    }


class Command(BaseCommand):
    help = "Seed event package categories, sets, and itemized inclusions."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing packages in seeded sets before inserting.",
        )

    def handle(self, *args, **options):
        reset = options["reset"]
        created_count = 0
        updated_count = 0
        item_count = 0
        addons_created = 0

        addon_category_map = {c.name: c for c in AddOnCategory.objects.all()}
        addon_item_keys = set(
            AddOnItem.objects.values_list("category_id", "name")
        )
        pending_addons = []

        for block in SEED_DATA:
            category, _ = EventCategory.objects.get_or_create(
                name=block["category"],
                defaults={"description": block["category_description"]},
            )

            if category.description != block["category_description"]:
                category.description = block["category_description"]
                category.save(update_fields=["description"])

            if reset:
                existing_qs = EventPackage.objects.filter(
                    category=category,
                    package_set=block["package_set"],
                )
                EventPackageItem.objects.filter(package__in=existing_qs).delete()
                existing_qs.delete()

            for item in block["packages"]:
                inclusions_text = "\n".join(item["inclusions"])
                defaults = {
                    "name": item["name"],
                    "theme_style": block["theme_style"],
                    "description": item["description"],
                    "inclusions": inclusions_text,
                    "duration_hours": block["duration_hours"],
                    "base_price": item["base_price"],
                    "is_active": True,
                }

                package, created = EventPackage.objects.update_or_create(
                    category=category,
                    package_set=block["package_set"],
                    package_number=item["package_number"],
                    defaults=defaults,
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

                EventPackageItem.objects.filter(package=package).delete()
                for line in item["inclusions"]:
                    payload = parse_line(line)
                    EventPackageItem.objects.create(package=package, **payload)
                    item_count += 1

                    addon_category_name = payload["item_group"]
                    addon_category = addon_category_map.get(addon_category_name)
                    if not addon_category:
                        addon_category = AddOnCategory.objects.create(name=addon_category_name)
                        addon_category_map[addon_category_name] = addon_category

                    addon_name = payload["item_name"][:150]
                    addon_key = (addon_category.id, addon_name)
                    if addon_key not in addon_item_keys:
                        pending_addons.append(
                            AddOnItem(
                                category=addon_category,
                                name=addon_name,
                                price="0.00",
                            )
                        )
                        addon_item_keys.add(addon_key)
                        addons_created += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Seeded: {package.package_set} - Package {package.package_number}"
                    )
                )

        if pending_addons:
            AddOnItem.objects.bulk_create(pending_addons)

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created: {created_count}, Updated: {updated_count}, Items: {item_count}, Add-ons created: {addons_created}"
            )
        )

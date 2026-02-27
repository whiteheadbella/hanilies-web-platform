from datetime import datetime
from .models import Cake

def get_season_recommendations():
    month = datetime.now().month

    if month == 12:
        return Cake.objects.filter(season_tags__name="Christmas")

    elif month == 2:
        return Cake.objects.filter(season_tags__name="Valentine")

    elif month in [3, 4, 5]:
        return Cake.objects.filter(season_tags__name="Graduation")

    return Cake.objects.all()
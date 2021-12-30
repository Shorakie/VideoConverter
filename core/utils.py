from datetime import timedelta

from django.db.models.aggregates import Sum
from django.utils.timezone import now

from apps.video.models import Video


def today_total_conversion(user):
    """
    Returns todays total duration of videos
    the result is the duration of Queued, Converting, Finished or Expired videos
    """
    today = now().replace(minute=0, hour=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    return (
        Video.objects.filter(uploader=user, upload_date__range=(today, tomorrow))
        .exclude(convert_status__in=[Video.FAILED])
        .aggregate(Sum('length', default=timedelta(0)))
    )['length__sum']

from datetime import timedelta

from apps.video.models import Video

from .utils import today_total_conversion


class RemainingConversionTimeMiddleware:
    """
    Adds `remaining_conversion_time` to responses of authenticated users
    the value is the total minutes left for the user to convert videos
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user and request.user.is_authenticated:
            remaining_conversion_time = max(
                Video.DAILY_CONVERT_TIME - today_total_conversion(request.user),
                timedelta(0),
            )

            # total in minutes
            remaining_conversion_time /= timedelta(minutes=1)
            response['remaining_conversion_time'] = remaining_conversion_time
        return response

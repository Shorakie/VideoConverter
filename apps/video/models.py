from datetime import timedelta
from time import time

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.timezone import now


def video_directory_path(_instance, filename):
    """
    Returns MEDIA_ROOT/source/<unix_timestamp>_<filename> file path
    """
    return f'source/{round(time() * 1000)}_{filename}'


class Video(models.Model):
    MP4 = 'MP4'
    AVI = 'AVI'
    MKV = 'MKV'
    THREE_GP = '3GP'
    ALLOWED_EXTENSIONS = [MP4, AVI, MKV, THREE_GP]
    TARGET_FORMAT_CHOICES = [
        (MP4, 'mp4'),
        (AVI, 'avi'),
        (MKV, 'mkv'),
        (THREE_GP, '3gp'),
    ]

    IN_QUEUE = 'INQ'
    FAILED = 'ERR'
    CONVERTING = 'CNV'
    FINISHED = 'FIN'
    EXPIRED = 'EXP'
    CONVERT_STATUS_CHOICES = [
        (IN_QUEUE, 'in queue'),
        (FAILED, 'failed'),
        (CONVERTING, 'converting'),
        (FINISHED, 'finished'),
        (EXPIRED, 'expired'),
    ]
    EXPIRES_AFTER = timedelta(hours=48)
    DAILY_CONVERT_TIME = timedelta(minutes=1000)

    id = models.AutoField(primary_key=True)

    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='uploader',
        on_delete=models.CASCADE,
        related_name='videos',
    )

    source_file = models.FileField(
        verbose_name='source file',
        upload_to=video_directory_path,
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)],
        null=True,
        blank=True,
    )

    name = models.CharField(max_length=64, verbose_name='name')

    converted_file = models.FileField(
        verbose_name='converted file', upload_to='converted/', null=True, blank=True
    )

    target_format = models.CharField(
        max_length=3, verbose_name='target format', choices=TARGET_FORMAT_CHOICES
    )

    length = models.DurationField(verbose_name='length')

    convert_status = models.CharField(
        max_length=3,
        verbose_name='convert status',
        choices=CONVERT_STATUS_CHOICES,
        default=IN_QUEUE,
    )

    upload_date = models.DateTimeField(
        verbose_name='upload date', default=now, editable=False
    )
    start_convert_date = models.DateTimeField(
        verbose_name='start convertion date', null=True, blank=True
    )
    finish_convert_date = models.DateTimeField(
        verbose_name='finish convertion date', null=True, blank=True
    )

    class Meta:
        managed = True
        db_table = 'videos'

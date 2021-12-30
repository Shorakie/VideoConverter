import json
from pathlib import Path

import ffmpeg
from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils.timezone import now
from django_celery_beat.models import ClockedSchedule, PeriodicTask

from .models import Video

logger = get_task_logger(__name__)


@shared_task(ignore_result=True, name='expire_video')
def expire_video(video_pk):
    video = Video.objects.get(pk=video_pk)

    # don't throw exception if the converted video is missing
    Path(video.converted_file.path).unlink(missing_ok=True)

    # update the video status and converted_file
    Video.objects.filter(pk=video_pk).update(
        converted_file='', convert_status=Video.EXPIRED
    )


@shared_task(bind=True, ignore_result=True, name='convert_video')
def convert_video(self, video_pk):
    video = Video.objects.get(pk=video_pk)
    target_format = video.target_format.lower()
    output_options = {}

    source_path = Path(video.source_file.path)
    dest_path = (
        source_path.parent.parent / 'converted' / f'{source_path.stem}.{target_format}'
    )

    # because of missing amr_nb encoder, use alternative codecs
    if target_format == '3gp':
        output_options['vcodec'] = 'h263'
        output_options['acodec'] = 'aac'

    # update the video status and set start_convert_date
    Video.objects.filter(pk=video_pk).update(
        start_convert_date=now(), convert_status=Video.CONVERTING
    )

    # Try converting the video
    try:
        ffmpeg.input(str(source_path)).output(str(dest_path), **output_options).run(
            overwrite_output=True, quiet=True
        )
    except ffmpeg.Error:
        # update the video status
        Video.objects.filter(pk=video_pk).update(convert_status=Video.FAILED)
        return

    # update the video status and set finish_convert_date
    finished_upload_datetime = now()
    Video.objects.filter(pk=video_pk).update(
        finish_convert_date=finished_upload_datetime,
        convert_status=Video.FINISHED,
        converted_file=f'converted/{source_path.stem}.{target_format}',
        source_file='',
    )

    clocked, _ = ClockedSchedule.objects.get_or_create(
        clocked_time=finished_upload_datetime + Video.EXPIRES_AFTER
    )
    PeriodicTask.objects.create(
        name=f'expire video {video_pk} task {self.request.id}',
        task='expire_video',
        clocked=clocked,
        one_off=True,
        args=json.dumps([video_pk]),
        start_time=now(),
    )

    # don't throw exception if the source video is missing
    source_path.unlink(missing_ok=True)

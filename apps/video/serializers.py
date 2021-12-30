from datetime import timedelta
from pathlib import Path

import ffmpeg
from django.core.validators import FileExtensionValidator
from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from apps.video.models import Video
from core.utils import today_total_conversion
from core.validators import VideoIntegrityValidator

from .tasks import convert_video


class VideoSerializer(serializers.ModelSerializer):
    remaining_expiration_time = serializers.SerializerMethodField()

    def get_remaining_expiration_time(self, instance):
        if instance.convert_status not in [Video.FINISHED, Video.EXPIRED]:
            return None

        expiration_datetime = instance.finish_convert_date + Video.EXPIRES_AFTER

        return serializers.DurationField().to_representation(
            max(expiration_datetime - now(), timedelta(0))
        )

    class Meta:
        model = Video
        fields = (
            'id',
            'name',
            'remaining_expiration_time',
            'converted_file',
            'target_format',
            'length',
            'convert_status',
            'upload_date',
            'start_convert_date',
            'finish_convert_date',
        )


class UploadVideoSerializer(serializers.ModelSerializer):
    file = serializers.FileField(
        source='source_file',
        validators=[
            FileExtensionValidator(allowed_extensions=Video.ALLOWED_EXTENSIONS),
            VideoIntegrityValidator(allowed_extensions=Video.ALLOWED_EXTENSIONS),
        ],
    )

    def validate(self, data):
        source_file = Path(data['source_file'].temporary_file_path())
        extension = Path(source_file.name).suffix[1:].lower()

        # Check if the source video extension is the same as target
        if extension == data['target_format'].lower():
            raise serializers.ValidationError(
                'Source video format and target format are the same.', 'same_format'
            )

        # Check if user has credit to convert the video
        probe = ffmpeg.probe(source_file)
        today_conversion_time = today_total_conversion(self.context['request'].user)
        video_duration = timedelta(seconds=float(probe['format']['duration']))
        if today_conversion_time + video_duration > Video.DAILY_CONVERT_TIME:
            raise PermissionDenied('Insufficient video convert time')
        return data

    def create(self, validated_data):
        source_file = validated_data['source_file']
        probe = ffmpeg.probe(Path(source_file.temporary_file_path()))
        duration_in_milliseconds = float(probe['format']['duration']) * 1000

        video = Video.objects.create(
            uploader=self.context['request'].user,
            length=timedelta(milliseconds=int(duration_in_milliseconds)),
            name=Path(source_file.name).stem,
            **validated_data
        )

        convert_video.delay(video.pk)

        return video

    class Meta:
        model = Video
        fields = (
            'file',
            'target_format',
        )

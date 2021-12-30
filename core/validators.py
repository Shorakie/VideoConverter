from pathlib import Path

import ffmpeg
from rest_framework.serializers import ValidationError


def container_from_extension(extension: str) -> str:
    if extension == 'mkv':
        return 'matroska'
    return extension


class VideoIntegrityValidator:
    messages = {
        'not_video': 'File is not a valid video file',
        'video_integrity': 'Video extension “%(extension)s” doesn\'t match the container.',
        'invalid_container': (
            'Video container “%(container)s” is not allowed. '
            'Allowed containers are: %(allowed_containers)s.'
        ),
    }

    def __init__(self, allowed_extensions=None):
        if allowed_extensions is not None:
            allowed_containers = [
                container_from_extension(allowed_extension.lower())
                for allowed_extension in allowed_extensions
            ]
        self.allowed_containers = allowed_containers

    def __call__(self, value):
        extension = Path(value.name).suffix[1:].lower()

        # check if the file is an actual video file, and retrieve the video metadata
        try:
            probe = ffmpeg.probe(value.temporary_file_path(), select_streams='V')
            if probe.get('streams', None) is None:
                raise ValidationError(self.messages['not_video'], 'not_video')
        except ffmpeg.Error as ffmpeg_error:
            raise ValidationError(
                self.messages['not_video'], 'not_video'
            ) from ffmpeg_error

        container = container_from_extension(extension)

        # check if the container is in allowed list
        if (
            self.allowed_containers is not None
            and container not in self.allowed_containers
        ):
            raise ValidationError(
                self.messages['invalid_video_file']
                % {
                    'container': container,
                    'allowed_containers': self.allowed_containers,
                },
                'invalid_video_file',
            )

        # match file extension with possible containers
        possible_containers = probe['format']['format_name'].lower().split(',')
        if container not in possible_containers:
            raise ValidationError(
                self.messages['video_integrity'] % {'extension': extension},
                'video_integrity',
            )

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.allowed_containers == other.allowed_containers
        )

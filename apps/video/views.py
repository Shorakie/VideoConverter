from django.core.files.uploadhandler import TemporaryFileUploadHandler
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.video.models import Video
from apps.video.serializers import UploadVideoSerializer, VideoSerializer


class VideoViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = VideoSerializer

    @action(methods=['POST'], detail=False, serializer_class=UploadVideoSerializer)
    def upload(self, request, *args, **kwargs):
        """
        Takes a video file and target_format and enqueues
        a task to convert the video file to that format
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        video = serializer.save()
        return Response(VideoSerializer(video).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrive a video instance
        """
        return super().retrieve(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        Return a paginated list of all users' submitted videos
        """
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        return Video.objects.filter(uploader=self.request.user).order_by('-upload_date')

    def initialize_request(self, request, *args, **kwargs):
        # Force TemporaryFileUploadHandler
        request.upload_handlers = [TemporaryFileUploadHandler(request)]
        return super().initialize_request(request, *args, **kwargs)

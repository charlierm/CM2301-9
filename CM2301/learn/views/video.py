from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core import serializers
from learn.models import Video
from learn.forms import *

@login_required
def create(request):
    form = VideoUploadForm()
    videos = Video.objects.all()
    return render(request, 'video_upload.html', {'videos': videos, 'form': form})

@login_required
def all(request):
    videos = Video.objects.all()
    return render(request, 'video_list.html', {'videos': videos})

@login_required
def video(request, video_id):
    Viewed.log_view(request, video_id)
    print video_id
    try:
        video = Video.objects.get(pk=video_id)
    except Video.DoesNotExist:
        raise Http404('Video %s does not exist' % (video_id))
    print video.uploaded_video
    return render(request, 'video_player.html', {'video': video})
            
@login_required
def submit(request, video_id):
    if request.method == 'POST':
        form = VideoUploadForm(data=request.POST, files=request.FILES)
        
        if form.is_valid():
            form.save()
            return HttpResponse("MOTHER FUCKER IT UPLOADED")

@login_required
def serve(request, video_id):
    """
    Serves a video media stream to the client, this view is used
    by the VideoJS player.
    """
    Viewed.log_view(request, video_id)
    video = Video.objects.get(pk=video_id)
    filename = video.uploaded_video.name.split('/')[-1]
    response = StreamingHttpResponse(video.uploaded_video, content_type='video/mp4')
    response['Content-length'] = video.uploaded_video.file.size
    return response

@login_required
def format_serve(request, video_format_id):
    """
    Serves a video media stream to the client, this view is used
    by the VideoJS player.
    """
    vf = VideoFormat.objects.get(pk=video_format_id)
    filename = vf.file.name.split('/')[-1]
    response = StreamingHttpResponse(vf.file)
    response['Content-Type'] = "video/%s" % (vf.format)
    response['Content-length'] = vf.file.file.size
    return response

@login_required
@require_http_methods(["POST", "GET"])
def conversion_progress(request, video_id):
    video = Video.objects.filter(pk=video_id)
    data = serializers.serialize('json', video, fields=('id','converting', 'conversion_progress'))
    return HttpResponse(data)

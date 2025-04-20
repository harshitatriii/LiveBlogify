import json
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, FileResponse
from rest_framework.decorators import api_view
from django.core.files.storage import default_storage
import os
import datetime

# Audio extraction
from moviepy import VideoFileClip

# Transcribe audio
import whisper

# Summarize text
from transformers import pipeline
from django.conf import settings

# Load Whisper and Summarization models once (for efficiency)
whisper_model = whisper.load_model("small")

# summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")


# ============================
# API Views
# ============================

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os

from django.shortcuts import render, redirect
from .models import UploadedVideo  # Assuming you have a model for storing videos
from .utils import process_video  # Import your audio extraction & transcription logic

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile



@csrf_exempt
def upload_video(request):
    if request.method == "POST" and request.FILES.get("video"):
        video_file = request.FILES["video"]

        # Save the video file
        file_path = default_storage.save(f"videos/{video_file.name}", ContentFile(video_file.read()))
        full_path = os.path.join(default_storage.location, file_path)

        return render(request, "upload_success_stepwise.html", {
            "video_path": file_path,  # like 'videos/something.mp4'
            "video_name": video_file.name
        })

    return render(request, "upload.html", {"error": "No video uploaded."})


def get_audio(request):
    video_rel_path = request.GET.get('video_path')
    audio_rel_path = request.GET.get('audio_path')

    if not video_rel_path or not audio_rel_path:
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    video_full_path = os.path.join(settings.MEDIA_ROOT, video_rel_path)
    audio_full_path = os.path.join(settings.MEDIA_ROOT, audio_rel_path)

    if not os.path.exists(video_full_path):
        return JsonResponse({'error': 'Video file not found'}, status=404)

    try:
        video_clip = VideoFileClip(video_full_path)
        audio_clip = video_clip.audio

        os.makedirs(os.path.dirname(audio_full_path), exist_ok=True)
        audio_clip.write_audiofile(audio_full_path, logger=None)

        audio_clip.close()
        video_clip.close()
    except Exception as e:
        return JsonResponse({'error': f'Audio extraction failed: {str(e)}'}, status=500)

    return FileResponse(open(audio_full_path, 'rb'), content_type='audio/mpeg')

def transcribe_audio(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        audio_file = data.get('audio_file')

        if not audio_file:
            return JsonResponse({'success': False, 'message': 'No audio file path provided'})

        try:
            model = whisper.load_model("base")
            file_path = os.path.join("media", audio_file)
            result = model.transcribe(file_path)
            return JsonResponse({'success': True, 'transcription': result['text']})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import os

@csrf_exempt
def summarize_text(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        file_path_from_input = request.POST.get('file')

        if uploaded_file:
            file_path = os.path.join(settings.MEDIA_ROOT, 'temp', uploaded_file.name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
        elif file_path_from_input:
            file_path = os.path.join(settings.MEDIA_ROOT, file_path_from_input)
        else:
            return JsonResponse({'success': False, 'message': 'No file provided!'}, status=400)

        if not os.path.exists(file_path):
            return JsonResponse({'success': False, 'message': 'File does not exist!'}, status=404)

        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()

        if len(text.strip()) == 0:
            return JsonResponse({'success': False, 'message': 'Text is empty!'}, status=400)

        summary = summarizer(text, max_length=150, min_length=50, do_sample=False)
        html = render_to_string('partials/summary_box.html', {
            'summary': summary[0]['summary_text']
        })
        return JsonResponse({'success': True, 'html': html})

    return JsonResponse({'success': False, 'message': 'Invalid request!'}, status=400)





import datetime
from django.conf import settings
import re

@csrf_exempt
def generate_blog(request):
    if request.method == 'POST':
        import json
        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)
        text = data.get('transcription', '')

        if not text:
            return JsonResponse({'success': False, 'message': 'No transcription text provided!'})

        # 1. Summarize
        summary = summarizer(text, max_length=150, min_length=50, do_sample=False)[0]['summary_text']

        # 2. Split into sentences
        sentences = re.split(r'(?<=[.!?]) +', summary.strip())
        intro = ' '.join(sentences[:2])
        body = ' '.join(sentences[2:-2]) if len(sentences) > 4 else ''
        conclusion = ' '.join(sentences[-2:])

        # 3. Extract a "quote" line
        quote = ''
        for s in sentences:
            if 'never' in s.lower() or 'always' in s.lower():
                quote = s.strip()
                break

        # 4. Simple title
        title = "Reflections on Creativity and Consistency"

        # 5. Create HTML content
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = f"blog_{timestamp}.html"
        file_path = os.path.join(settings.MEDIA_ROOT, "generated_blogs", file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        html_content = f""" 
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; margin: 20px; line-height: 1.7; color: #333; }}
                h1 {{ color: #2c3e50; }}
                p {{ margin-bottom: 16px; }}
                blockquote {{ font-style: italic; background: #f9f9f9; padding: 10px 20px; border-left: 5px solid #ccc; }}
                footer {{ margin-top: 30px; font-size: 0.9em; color: #999; }}
                .tags {{ margin-top: 10px; font-size: 0.9em; color: #555; }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <p><strong>By LiveBlogify AI | {datetime.datetime.now().strftime('%B %d, %Y')}</strong></p>

            <p>{intro}</p>
            <blockquote>{quote}</blockquote>
            <p>{body}</p>
            <p><strong>{conclusion}</strong></p>

            <hr>
            <p class="tags"><em>#inspiration #motivation #creativity</em></p>
        </body>
        </html>
        """

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(html_content)

        return render(request, 'blog_display.html', {
            'blog_html': html_content,
            'blog_title': title,
            'file_name': file_name
        })
    return JsonResponse({'success': False, 'message': 'Invalid request!'}, status=400)




@api_view(['GET'])
def download_blog(request, file_name):
    file_path = os.path.join(settings.MEDIA_ROOT, "generated_blogs", file_name)

    if not os.path.exists(file_path):
        return JsonResponse({'error': 'File not found'}, status=404)

    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=file_name)


# ============================
# Views for Rendering Templates
# ============================

def home_view(request):
    """Render the home page."""
    return render(request, 'home.html')


def upload_view(request):
    """Render the upload page."""
    return render(request, 'upload.html')

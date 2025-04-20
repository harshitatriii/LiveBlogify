from django.urls import path
from . import views

#  - Create API endpoints: 
#  1️⃣ File Upload API (Receives video file and stores it). 
#  2️⃣ Transcription API (Calls AI processing function). 
#  3️⃣ Summarization API (Calls AI model for summarization). 
#  4️⃣ Blog Retrieval API (Returns formatted blog content). 

# api endpoints :-

# POST /upload/
# POST /transcribe/
# POST /summarize/
# GET /blog/{file_id}/
# GET /download/{file_id}/
# DELETE /delete/{file_id}/

# Serve media files in development

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('upload/', views.upload_video, name='upload_video'),
    path('extract_audio/', views.get_audio, name='extract_audio'),
    path('transcribe-audio/', views.transcribe_audio, name='transcribe_audio'),
    path('summarize/', views.summarize_text, name='summarize_text'),
    path('generate-blog/', views.generate_blog, name='generate_blog'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




# 1) upload/ url path of api to upload video
# 2) core/extract-audio/ url path of api to extract audio
# 3) core/transcribe/ url path of api to transcribe the audio extracted
# 4) core/summarize/ url path of api to aummarize the text transcribed
# 5) core/generate-blog/ url path of api to generate the blog

# gajendra verma - Muskil Badi


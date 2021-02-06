from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from djangoProject import settings
from djangoProject.paths.artists import artists, artist_info, artist_comments, artist_comments_add, request
from djangoProject.paths.user import collect, login, register, verify, logout, profile, forgot_password, upload_picture
from djangoProject.queues import queue_email, artists_manager

# TODO
# -----
# TODO: Add activity history for each action
# TODO: Send an email when log in
# TODO: Add comments

urlpatterns = [
    path('user/login', login.login), # Login
    path('user/forgot-password', forgot_password.forgot_password_request),
    path('user/forgot-password/<str:token>', forgot_password.forgot_password_change),
    path('user/register', register.register),
    path('user/collect', collect.collect),
    path('user/profile', profile.profile),
    path('user/profile/edit/picture', upload_picture.upload), # TODO test
    path('user/profile/edit', collect.collect), # TODO Profile data edit
    path('user/verify/<str:token>', verify.verify), # Verify email
    path('user/logout', logout.logout),
    path('artists', artists.artists), # List of artists (filter by type, etc.)
    path('artists/gallery/add', artist_info.artist_info), # TODO upload image gallery
    path('artists/info', artist_info.artist_info), # Artist info
    path('artists/comments', artist_comments.artist_comments), # Artist comments
    path('artists/comments/add', artist_comments_add.artist_add_comments), # Artist add comments
    path('artists/request', request.request), # Request artist requests
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Add uploaded pictures
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Start queues
queue_email.queue_start()
artists_manager.queue_start()
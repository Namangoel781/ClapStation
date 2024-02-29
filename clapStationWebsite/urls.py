from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("", views.starting_page, name="starting-page"),
    path('postdelete/<int:id>',views.postdelete,name='postdelete'),
    path('groups/', views.groups_page, name='groups'),
    path('bands/', views.bands_page, name='bands'),
    path('academies/', views.academies_page, name='academies'),
    path('events/', views.events_page, name='events'),
    path('artists/', views.artists_page, name='artists'),
    path('about/', views.about_page, name='about'),
    path('contact/', views.contact_page, name='contact'),
    path('signup/', views.signin, name='signup'),
    path('login/', views.custom_login, name='login'),
    path('profile/', views.profile_page, name='profile'),
    path('logout/',views.custom_logout,name='logout'),
    path('toggle_like_dislike/<int:post_id>/',views.toggle_like_dislike, name='toggle_like_dislike'),
    path('add-live-video/', views.add_live_video, name='add-live-video'),
    path('livevideodelete/<int:id>/', views.livevideodelete, name='livevideo-delete'),
    path('add_comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('add_event/', views.add_event, name='add_event'),
    path('submit_rating/<int:post_id>/<int:rating>/', views.submit_rating, name='submit_rating'),
    path('add_Photo/', views.add_Photo, name='add_Photo'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root = settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()


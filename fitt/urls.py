from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('gymapp.urls')),
]

handler403 = 'gymapp.views.auth_views.forbidden'
handler404 = 'gymapp.views.auth_views.page_not_found'
handler500 = 'gymapp.views.auth_views.server_error'

admin.site.site_header = 'FITFOCUS Administration'
admin.site.site_title = 'FITFOCUS Admin'
admin.site.index_title = 'Inspect gym records'

from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static

from . import views

# Register app namespace : IMPORTANT !
app_name = "testapp"

urlpatterns = [
    # ex: /polls/
    path(
        route='',                           # string containing a URL pattern
        view=views.IndexView.as_view(),     # call the specified view function upon finding a matching pattern
        name='index'                        # set a name for URL
    ),
    # ex: /polls/5/
    path(route='<int:pk>/', view=views.DetailView.as_view(), name='detail'),
    # ex: /polls/5/results/
    path(route='<int:pk>/results/', view=views.ResultsView.as_view(), name='results'),
    # ex: /polls/5/vote/
    path(route='<int:pk>/vote/', view=views.vote, name='vote'),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

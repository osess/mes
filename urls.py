from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

'''
from django.contrib import admin
admin.autodiscover()
'''
#xadmin
import xadmin
xadmin.autodiscover()
from xadmin.plugins import xversion
xversion.register_models()

from pinax.apps.account.openid_consumer import PinaxConsumer

handler500 = "pinax.views.server_error"


urlpatterns = patterns("",
    url(r'xadmin/', include(xadmin.site.urls)),
    #url(r"^$", direct_to_template, {"template": "homepage.html",}, name="home"),
    url(r"^$", "serv.views.homepage", name="home"),
    url(r"^admin/invite_user/$", "pinax.apps.signup_codes.views.admin_invite_user", name="admin_invite_user"),
    #url(r"^admin/", include(admin.site.urls)),
    url(r"^about/", include("about.urls")),
    url(r"^account/", include("pinax.apps.account.urls")),
    url(r"^openid/", include(PinaxConsumer().urls)),
    url(r"^profiles/", include("idios.urls")),
    url(r"^notices/", include("notification.urls")),
    url(r"^announcements/", include("announcements.urls")),

    #add by xxd
    url(r"^companydepartment/", include("companydepartment.urls")),
    url(r"^technology/", include("technologies.urls")),
    url(r"^manufactureplan/", include("manufactureplan.urls")),
    url(r"^quality/", include("quality.urls")),
    url(r"^warehouse/", include("warehouse.urls")),
    url(r"^barcode/", include("yt_barcode.urls")),
    url(r"^report/", include("report.urls")),
    url(r"^file/", include("yt_file.urls")),
    url(r'^messages/', include('django_messages.urls')),
    url(r'^actstream/', include('actstream.urls')),
    url(r'session_security/', include('session_security.urls')),
    url(r"^yt_report/", include("yt_report.urls")),

    url(r"^about_us/$", direct_to_template, {"template": "direct_pages/about_us.html",}, name="about_us"),
    url(r"^contacts$", direct_to_template, {"template": "direct_pages/about_us.html",}, name="contacts"),


    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'^feedback/', include('djangovoice.urls')),
    url(r'^blog/', include('blog.urls')),
)

if settings.SERVE_MEDIA:
    urlpatterns += patterns("",
        url(r"", include("staticfiles.urls")),
    )

'''
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
'''
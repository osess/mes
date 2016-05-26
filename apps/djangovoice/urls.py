from django.conf.urls import include, patterns, url
from django.contrib.auth.views import login
from djangovoice.models import Feedback
from djangovoice.views import (
    FeedbackListView, FeedbackWidgetView, FeedbackSubmitView,
    FeedbackDetailView, FeedbackEditView, FeedbackDeleteView)
from djangovoice.feeds import LatestFeedback
from .utils import get_voice_extra_context

feedback_list_regex = '^(?P<list>all|open|closed|mine)'
feedback_dict = {
    'model': Feedback,
    'template_object_name': 'feedback'
}

urlpatterns = patterns(
    '',

    url(r'^$',
        view=FeedbackListView.as_view(),
        name='djangovoice_home'),

    url(r'%s/$' % feedback_list_regex,
        view=FeedbackListView.as_view(),
        name='djangovoice_list'),

    url(r'%s/(?P<type>[-\w]+)/$' % feedback_list_regex,
        view=FeedbackListView.as_view(),
        name='djangovoice_list_type'),

    url(
        r'%s/(?P<type>[-\w]+)/(?P<status>[-\w]+)/$' % feedback_list_regex,
        view=FeedbackListView.as_view(),
        name='djangovoice_list_type_status'),

    url(r'^widget/$',
        view=FeedbackWidgetView.as_view(),
        name='djangovoice_widget'),

    url(r'^submit/$',
        view=FeedbackSubmitView.as_view(),
        name='djangovoice_submit'),

    # override login template
    url(r'^signin/$',
        view=login,
        name='djangovoice_signin',
        kwargs={
            'template_name': 'djangovoice/signin.html',
            'extra_context': get_voice_extra_context()
        }),

    url(r'^(?P<pk>\d+)/$',
        view=FeedbackDetailView.as_view(),
        name='djangovoice_item'),

    url(r'^(?P<slug>\w+)/$',
        view=FeedbackDetailView.as_view(),
        name='djangovoice_slug_item'),

    url(r'^(?P<pk>\d+)/edit/$',
        view=FeedbackEditView.as_view(),
        name='djangovoice_edit'),

    url(r'^(?P<pk>\d+)/delete/$',
        view=FeedbackDeleteView.as_view(),
        name='djangovoice_delete'),

    url(r'^feeds/latest/$',
        view=LatestFeedback(),
        name='feeds_latest'),

    url(r'^votes/', include('qhonuskan_votes.urls'))
)

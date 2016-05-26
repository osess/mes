from qhonuskan_votes.compat import patterns, url

urlpatterns = patterns(
    'qhonuskan_votes.views',

    url(r'^vote/$', view='vote', name='qhonuskan_vote'))

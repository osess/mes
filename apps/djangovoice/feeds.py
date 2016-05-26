from django.contrib.syndication.views import Feed
from djangovoice.models import Feedback


class LatestFeedback(Feed):
    title = "Feedback"
    link = "/feedback/"
    description = "Latest feedback"

    def items(self):
        return Feedback.objects.filter(private=False).order_by('-created')[:10]

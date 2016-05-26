from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext

from django.contrib.auth.decorators import login_required
from django.contrib.syndication.views import Feed

from notification.models import *
from notification.decorators import basic_auth_required, simple_basic_auth_callback
from notification.feeds import NoticeUserFeed

from django.contrib.auth.models import User, Group

def notice_to_user(user, sender, message, notice_type, on_site=True):

	new_notice = Notice.objects.create(

                        recipient   = user,
                        sender      = sender,
                        message     = message,
                        notice_type = notice_type,
                        on_site     = on_site,
                    )


def notice_to_group(group, sender, message, notice_type, on_site=True):

	users_in_group = group.user_set.all()

	for user in users_in_group:
		new_notice = Notice.objects.create(

                            recipient   = user,
                            sender      = sender,
                            message     = message,
                            notice_type = notice_type,
                            on_site     = on_site,
                        )


def notice_to_all(sender, message, notice_type, on_site=True):

	all_users = User.objects.all()

	for user in all_users:
		new_notice = Notice.objects.create(

                            recipient   = user,
                            sender      = sender,
                            message     = message,
                            notice_type = notice_type,
                            on_site     = on_site,
                        )


def notice_to_groups(groups, sender, message, notice_type, on_site=True):

    users_list = []
    for group in groups:
        users_in_group = group.user_set.all()
        users_list += users_in_group

    users_list = list(set(users_list))
    for user in users_list:
        notice_to_user(user, sender, message, notice_type, on_site=True)


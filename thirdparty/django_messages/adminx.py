import xadmin
from xadmin.layout import *
from django.utils.translation import ugettext_lazy as _

from models import Message


class MessageAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    list_display = (
       'subject', 'body', 'sender', 'recipient',
       'sent_at', 'read_at', 'replied_at', 'sender_deleted_at',
       'recipient_deleted_at','group_recipient',
       )


    list_filter = ['subject', 'body', 'sender', 'recipient',
       'sent_at', 'read_at', 'replied_at', 'sender_deleted_at',
       'recipient_deleted_at',]
    search_fields = ['subject', 'body', 'sender', 'recipient',
       'sent_at', 'read_at', 'replied_at', 'sender_deleted_at',
       'recipient_deleted_at',]



  # subject = models.CharField(_("Subject"), max_length=120)
  #   body = models.TextField(_("Body"))
  #   sender = models.ForeignKey(AUTH_USER_MODEL, related_name='sent_messages', verbose_name=_("Sender"))
  #   recipient = models.ForeignKey(AUTH_USER_MODEL, related_name='received_messages', null=True, blank=True, verbose_name=_("Recipient"))
  #   parent_msg = models.ForeignKey('self', related_name='next_messages', null=True, blank=True, verbose_name=_("Parent message"))
  #   sent_at = models.DateTimeField(_("sent at"), null=True, blank=True)
  #   read_at = models.DateTimeField(_("read at"), null=True, blank=True)
  #   replied_at = models.DateTimeField(_("replied at"), null=True, blank=True)
  #   sender_deleted_at = models.DateTimeField(_("Sender deleted at"), null=True, blank=True)
  #   recipient_deleted_at = models.DateTimeField(_("Recipient deleted at"), null=True, blank=True)


  
    # recipient = models.ForeignKey(User, related_name="recieved_notices", verbose_name=_("recipient"))
    # sender = models.ForeignKey(User, null=True, related_name="sent_notices", verbose_name=_("sender"))
    # message = models.TextField(_("message"))
    # notice_type = models.ForeignKey(NoticeType, verbose_name=_("notice type"))
    # added = models.DateTimeField(_("added"), default=datetime.datetime.now)
    # unseen = models.BooleanField(_("unseen"), default=True)
    # archived = models.BooleanField(_("archived"), default=False)
    # on_site = models.BooleanField(_("on site"))


# xadmin.site.register(Message, MessageAdmin)
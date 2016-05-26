from django.db import models
from django.contrib.auth import user_logged_in, user_logged_out
from actstream import action

def user_action_in(sender, user, request, **kwargs):
     action.send(user, verb=u'log in')
user_logged_in.connect(user_action_in)

def user_action_out(sender, user, request, **kwargs):
     action.send(user, verb=u'log out')
user_logged_out.connect(user_action_out)

# #sample
# def post_save_action(sender, **kwargs):
#      action.send(kwargs['instance'], verb=u'a user created')
# post_save.connect(post_save_action, sender=User)

class Player(models.Model):
    state = models.IntegerField(default=0)
    
    def __unicode__(self):
        return '#%d' % self.pk
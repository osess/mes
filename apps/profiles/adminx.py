from models import Profile

import xadmin

class ProfileAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    list_display = (
       'name', 'about', 'location', 'website'
       )

    list_filter = ['name', 'about', 'location', 'website']
    search_fields = ['name']

# xadmin.site.register(Profile, ProfileAdmin)


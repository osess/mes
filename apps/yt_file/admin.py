'''
from django.contrib import admin
from yt_file.models import File
import reversion

class FileAdmin(reversion.VersionAdmin):
    pass

admin.site.register(File, FileAdmin)
'''
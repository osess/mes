from django.conf import settings
import magic
from extensions.custom_fields.encrypt import get_prep_value_encrypt,encryption_header_notin_field


from yt_file.models import *

# obj is the target content object
def yt_file_save(file, obj, display_name, path): 
    if file is not None:
        name = file.name
        content = file.read()
        file_type = magic.from_buffer(content)
        size = len(content)
        if size > int(settings.MAX_UPLOAD_SIZE):
            #TODO
            raise forms.ValidationError('Please keep filesize under %s.' % settings.MAX_UPLOAD_SIZE)
        
        imgtag = 0
        if "image" in file_type:
            imgtag = 1
        #use to technology, modify by xxd
        from django.contrib.contenttypes.models import ContentType
        if ContentType.objects.get_for_model(obj).model in ['technology']:
           imgtag = 0

        if display_name is None:
            display_name = name.split('.')[0]
        # if "T_" in file.name or "P_" in file.name:
        #     file = File(
        #         name = file.name,
        #         data = get_prep_value_encrypt(content,encryption_header_notin_field),#to see custom_fields.encrypt
        #         imgtag = imgtag,
        #         type = file_type,
        #         size = size,
        #         file = obj,
        #         display_name = display_name,
        #         path = path
        #     )
        #     file.save()
        # else:
        file = FileDirectory(
            name = file.name,
            data = file,
            imgtag = imgtag,
            type = file_type,
            size = size,
            file = obj,
            display_name = display_name,
            path = path
        )
        file.save()

        return 0

    return 1
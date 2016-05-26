#-*- coding: UTF-8 -*- 
import xadmin
from xadmin.layout import *
from xadmin.plugins.inline import Inline
from django.contrib.contenttypes.models import ContentType
from models import *
from django.utils.translation import ugettext, ugettext_lazy as _
from yt_barcode.views import BatchBarcodeAction

class TechnologyAdmin(object):

    def status_t(self, instance):
        technology_workflow_status = instance.technology_workflow_status
        if technology_workflow_status == 0:
            return '等待审核'
        if technology_workflow_status == 1:
            return '正在审核'
        if technology_workflow_status == 2:
            return '审核通过'
        if technology_workflow_status == 3:
            return '没有工艺文件'
    status_t.short_description = _("status")
    status_t.allow_tags = True
    status_t.is_column = True

    def technology_file(self, instance):
        content_type= ContentType.objects.get_for_model(instance)
        if instance.technology_workflow_status == 2 or instance.technology_workflow_approved:
            content_returned = "上传"
        else:
            content_returned = "<a data-hide='T' data-res-uri='/file/upload/%d/%d/' data-edit-uri='/file/upload/%d/%d/' class='details-handler' rel='tooltip' title='上传文件'>%s</a>" %(content_type.id, instance.id, content_type.id, instance.id, '上传')
        content_returned += "|<a href='/file/download/%d/'>下载</a>"%instance.T_file.id if instance.T_file else "|下载"
        return content_returned
    technology_file.short_description = _("technology_file")
    technology_file.allow_tags = True
    technology_file.is_column = True

    def program_file(self, instance):
        content_type= ContentType.objects.get_for_model(instance)
        if instance.T_file:
            '''
            if instance.technology_workflow_status == 2 or instance.technology_workflow_approved:
                content_returned = "上传"
            else:
            '''
            content_returned = "<a data-hide='P' data-res-uri='/file/upload/%d/%d/' data-edit-uri='/file/upload/%d/%d/' class='details-handler' rel='tooltip' title='上传文件'>%s</a>" %(content_type.id, instance.id, content_type.id, instance.id, '上传')
        else:
            content_returned = "上传"
        content_returned += "|<a href='/file/download/%d/'>下载</a>"%instance.P_file.id if instance.P_file else "|下载"
        return content_returned
    program_file.short_description = _("program_file")
    program_file.allow_tags = True
    program_file.is_column = True

    def D2_file(self, instance):
        content_type= ContentType.objects.get_for_model(instance)
        if instance.T_file:
            if instance.technology_workflow_status == 2 or instance.technology_workflow_approved:
                content_returned = "上传"
            else:
                content_returned = "<a data-hide='D2' data-res-uri='/file/upload/%d/%d/' data-edit-uri='/file/upload/%d/%d/' class='details-handler' rel='tooltip' title='上传文件'>%s</a>" %(content_type.id, instance.id, content_type.id, instance.id, '上传')
        else:
            content_returned = "上传"
        content_returned += "|<a href='/file/download/%d/'>下载</a>"%instance.D2_file.id if instance.D2_file else "|下载"
        return content_returned
    D2_file.short_description = _("D2_file")
    D2_file.allow_tags = True
    D2_file.is_column = True

    def D3_file(self, instance):
        content_type= ContentType.objects.get_for_model(instance)
        if instance.T_file:
            if instance.technology_workflow_status == 2 or instance.technology_workflow_approved:
                content_returned = "上传"
            else:
                content_returned = "<a data-hide='D3' data-res-uri='/file/upload/%d/%d/' data-edit-uri='/file/upload/%d/%d/' class='details-handler' rel='tooltip' title='上传文件'>%s</a>" %(content_type.id, instance.id, content_type.id, instance.id, '上传')
        else:
            content_returned = "上传"
        content_returned += "|<a href='/file/download/%d/'>下载</a>"%instance.D3_file.id if instance.D3_file else "|下载"
        return content_returned
    D3_file.short_description = _("D3_file")
    D3_file.allow_tags = True
    D3_file.is_column = True

    # def files_management(self, instance):
    #     content_type= ContentType.objects.get_for_model(instance)
    #     content_returned = "<a data-hide='T' data-res-uri='/file/upload/%d/%d/' data-edit-uri='/file/upload/%d/%d/' class='details-handler' rel='tooltip' title='上传文件'>%s</a>" %(content_type.id, instance.id, content_type.id, instance.id, '上传工艺文件')
    #     if instance.technology_workflow_status == 2:
    #         content_returned += " | "
    #         content_returned += "<a data-hide='P' data-res-uri='/file/upload/%d/%d/' data-edit-uri='/file/upload/%d/%d/' class='details-handler' rel='tooltip' title='上传文件'>%s</a>" %(content_type.id, instance.id, content_type.id, instance.id, '上传程式文件')
    #     else:
    #         content_returned += " | " + "上传程式文件"
    #     if instance.T_file:
    #         content_returned += " | "
    #         content_returned += "<a data-hide='D2' data-res-uri='/file/upload/%d/%d/' data-edit-uri='/file/upload/%d/%d/' class='details-handler' rel='tooltip' title='上传文件'>%s</a>" %(content_type.id, instance.id, content_type.id, instance.id, '上传二维图')
    #         content_returned += " | "
    #         content_returned += "<a data-hide='D3' data-res-uri='/file/upload/%d/%d/' data-edit-uri='/file/upload/%d/%d/' class='details-handler' rel='tooltip' title='上传文件'>%s</a>" %(content_type.id, instance.id, content_type.id, instance.id, '上传三维图')
    #     else:
    #         content_returned += " | " + "上传二维图" + " | " + "上传三维图"
    #     return content_returned
    # files_management.short_description = _("files management")
    # files_management.allow_tags = True
    # files_management.is_column = True

    list_display = ('name', 'product_symbol', 'product', 'description', 'publish_code', 'status_t', 'technology_file', 'program_file', 'D2_file', 'D3_file', 'status')
    list_display_links = ('name', 'description')
    list_display_links_details = True
    list_filter = ['name', 'status']
    search_fields = ['name', 'status']
    active_menu="technology"

    raw_id_fields = ('product',)
    show_detail_fields = ('product',)
    style_fields = {'materials': 'm2m_transfer'}
    exclude = ['workflow','code','materials', 'rev']
    #reversion_enable = True
    actions = [BatchBarcodeAction]

    form_layout = (
        Main(
            Fieldset(_('Technology Data'),
                'name', 'product', 'description', 'workflow', 'publish_code', 'materials', 'file_code', 'status',
                description=_("some comm fields, required")
            ),
            Fieldset(_('Manuafctureitem Quantity'),
                'each_product', 'spare_part', 'total',
                description=_("Manuafctureitem Quantity")
            ),
            Fieldset(_('Manuafctureitem Quality'),
                'one_piece', 'complete_set',
                description=_("Manuafctureitem Quality")
            ),
        ),
        Side(
            Fieldset(_('Workblank Data'),
                'workblank_mark', 'workblank_standard_code', 'workblank_hardness',
                'workblank_species', 'workblank_sectional_dimensions', 'workblank_length',
                'workblank_quantity', 'workblank_single_weight_kg', 'workblank_full_weight_kg'
            ),
        )
    )

class OperationGroupAdmin(object):

    def thumbnails1(self, instance):
        content_type= ContentType.objects.get_for_model(instance)
        if instance.technology.T_file:
            content_returned = "<a data-hide='TU1' data-res-uri='/file/upload/%d/%d/' data-edit-uri='/file/upload/%d/%d/' class='details-handler' rel='tooltip' title='上传文件'>%s</a>" %(content_type.id, instance.id, content_type.id, instance.id, '上传')
        else:
            content_returned = "上传"
        content_returned += "|<a href='/file/download/%d/'>下载</a>"%instance.TU1_file.id if instance.TU1_file else "|下载"
        return content_returned
    thumbnails1.short_description = _("thumbnails") + "1"
    thumbnails1.allow_tags = True
    thumbnails1.is_column = True

    def thumbnails2(self, instance):
        content_type= ContentType.objects.get_for_model(instance)
        if instance.technology.T_file:
            content_returned = "<a data-hide='TU2' data-res-uri='/file/upload/%d/%d/' data-edit-uri='/file/upload/%d/%d/' class='details-handler' rel='tooltip' title='上传文件'>%s</a>" %(content_type.id, instance.id, content_type.id, instance.id, '上传')
        else:
            content_returned = "上传"
        content_returned += "|<a href='/file/download/%d/'>下载</a>"%instance.TU2_file.id if instance.TU2_file else "|下载"
        return content_returned
    thumbnails2.short_description = _("thumbnails") + "2"
    thumbnails2.allow_tags = True
    thumbnails2.is_column = True

    def thumbnails3(self, instance):
        content_type= ContentType.objects.get_for_model(instance)
        if instance.technology.T_file:
            content_returned = "<a data-hide='TU3' data-res-uri='/file/upload/%d/%d/' data-edit-uri='/file/upload/%d/%d/' class='details-handler' rel='tooltip' title='上传文件'>%s</a>" %(content_type.id, instance.id, content_type.id, instance.id, '上传')
        else:
            content_returned = "上传"
        content_returned += "|<a href='/file/download/%d/'>下载</a>"%instance.TU3_file.id if instance.TU3_file else "|下载"
        return content_returned
    thumbnails3.short_description = _("thumbnails") + "3"
    thumbnails3.allow_tags = True
    thumbnails3.is_column = True


    list_display = ('order', 'name', 'description', 'technology', 'Job', 'device', 'thumbnails1', 'thumbnails2', 'thumbnails3')
    list_display_links = ('name', 'description')
    list_display_links_details = True
    active_menu="technology"
    search_fields = ['name']
    list_filter = ['name', 'technology', 'Job', 'device']
    exclude = ['materials']
    #reversion_enable = True


class OperationAttributeInline(object):
    model = OperationAttribute
    extra = 1
    style = 'table'
    exclude = ['display_value', 'is_published', 'ext_code', 'difference']

class OperationAdmin(object):
    list_display = ('order', 'name', 'description', 'operation_group', 'period', 'operation_type')
    list_display_links = ('name', 'description')
    list_display_links_details = True
    active_menu="technology"
    search_fields = ['name']
    list_filter = ['name', 'operation_group', 'period']
    exclude = ['state', 'product', 'tools', 'need_attribute']
    #reversion_enable = True

    Inline(OperationAttribute)
    inlines = [OperationAttributeInline]

# class OperationAttributeAdmin(object):

#     model_icon = 'cog'
#     hidden_menu = False
#     list_display = ('operation', 'attribute', 'absolute_value', 'difference')
#     list_filter = ['operation', 'attribute', 'absolute_value']
#     search_fields = ['operation', 'attribute', 'absolute_value']
#     exclude = ['display_value', 'is_published', 'ext_code']
# xadmin.site.register(OperationAttribute, OperationAttributeAdmin)

xadmin.site.register(Technology, TechnologyAdmin)
xadmin.site.register(OperationGroup, OperationGroupAdmin)
xadmin.site.register(Operation, OperationAdmin)

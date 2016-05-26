# coding:utf-8
from django.shortcuts import render_to_response, get_object_or_404, render, redirect
from django.http import HttpResponse
from django.template import RequestContext, loader, Context
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from xadmin.plugins.actions import BaseActionView

import base64
from hubarcode.code128 import Code128Encoder
from models import Barcode

class BatchBarcodeAction(BaseActionView):

    action_name = "batch_barcode"
    description = _(u'Batch barcode')
    model_perm = 'change'
    
    def do_action(self, queryset):
        html = '<table border=1>'
        number_per_row = 3
        barcode_list = []
        count = 0
        for query in queryset:
            try:
                barcode_item = Barcode.objects.get(code=query.code,name=query.name)
            except:
                barcode_item = add_barcode(query.code, query.name)
            barcode_list.append(barcode_item)

            if count < number_per_row:
                if count == 0:
                    html += '<tr>'
                html += '<td align="center"><br>' + barcode_item.name + '<br><img src="data:image/jpeg;base64,'+ barcode_item.base64_code + '"/><br><br></td>'
                count += 1
                if count == number_per_row:
                    count = 0
                    html += '</tr>'
            
        if html[-4:] != '</tr>':
            html += '</tr></table>'
        else:
            html += '</table>'

        return TemplateResponse(self.request, 'barcode.html', {
            'barcode_list':barcode_list, 'html':html,
        })

def add_barcode(code, name, bar_width=1):
    new_barcode = Barcode.objects.create(
        code        = code,
        name        = name,
        base64_code = base64.b64encode(Code128Encoder(code).get_imagedata(bar_width=bar_width))
    )
    return new_barcode

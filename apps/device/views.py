# -*- coding:utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.utils.simplejson.encoder import JSONEncoder
from django.contrib.contenttypes.models import ContentType
from models import Knife
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericRelation
from django.contrib.contenttypes import generic
from warehouse.models import Location, ItemJournal, DeviceEntry, Item
from django.contrib.auth.models import User


def add_knife(request):

    return render(request, 'add_knife.html', {

        })


def knife_entry(request):

    print"++++++++++++++++++++++"
    print "knife_entry"

def db(request):
            # for i in xrange(knife_in_warehouse+1, knife_in_warehouse+1+qty):
            #     new_deviceentry = DeviceEntry.objects.create(
            #         journal       = inventory,
            #         item          = transport_list_detail.item,
            #         internal_code = transport_list_detail.internal_code + '%02d' % (i),
            #         location      = warehouse,
            #         qty           = 1,
            #         updated_by    = user,
            #         usage_time    = 0,
            #         )

    # for i in xrange(1, 9):
    #     try:
    #         new_knife = Knife.objects.create(
    #             name = u'飞刀',
    #             code = 'FD' + '%03d' % (i)
    #             )
    #     except:
    #         pass


    qty = [
9,#1
3,
2,
1,
13,
6,
3,
1,
9,
1,
2,
5,
6,
2,
9,
1,
1,
6,
3,
6,
4,
1,
14,
2,
5,
2,
2,
3,
1,
13,
8,
1,
9,
17,
18,
2,
2,
8,
1,
3,
1,
2,
3,
18,
2,
1,
1,
2,
2,
25,
4,
2,
4,
2,
1,
4,
3,
8,
19,
1,
5,
4,
2,
1,
1,
1,
1,
7,
1,
1,
1,
1,
1,
1,
1,
1,
2,
2,
1,
1,
1,
1,
1,
1,
2,
1,
1,
2,
2,
2,
2,
2,
1,
1,
3,
1,
2,
2,
1,
2,
1,
1,
1,
1,
1,
1,

4,#2
2,
5,
5,
8,
19,
8,
5,
10,
6,
7,
6,
8,
7,
10,
4,
4,






1, #3
2,
1,
2,
3,
2,
1,
4,
3,
1,
1,
1,
2,
2,
1,
5,
2,
2,
2,
1,
1,
2,
9,
3,
2,
2,
2,
2,
2,
3,
2,
2,
1,
1,
1,
1,
4,
4,
3,
3,
5,
5,
40,
30,
30,
59,
39,
39,
59,
60,
39,

12,#4
4,
1,
1,
2,
5,
1,
7,
3,
9,
2,
6,
6,
1,
5,

1,#5
1,
1,
1,
1,
1,
1,
1,
2,
1,
1,
2,
1,
15,
4,
5,
3,
3,
2,
3,
1,
6,
6,
5,
4,
1,
2,
9,
1,
1,
14,
7,
15,
9,
2,
10,
10,
2,
5,
0,
2,
4,
3,
10,
7,
4,
4,
2,
1,
2,
0,
1,
2,
0,
1,
2,
1,
1,
2,
1,
1,
1,
1,
1,
1,

3,#6
2,
3,
3,
1,
4,
2,
1,
]




    for i in xrange(1,263): 

        knife = Knife.objects.get(id=i)
        
        invertory = ItemJournal.objects.get(id=1)
        warehouse = Location.objects.get(id=1)
        user = User.objects.get(id=1)
       
        try:
            item = Item.objects.get(code=knife.code)
        except:
            item = Item.objects.create(
                code = knife.code,
                content_type = ContentType.objects.get(app_label="device", model="knife"),
                object_id = knife.id,
                updated_by = user,
                )

        knife_in_warehouse = DeviceEntry.objects.filter(internal_code__startswith=knife.code).count()
        add_number = abs(qty[i-1] - knife_in_warehouse)
        
        if add_number > 0:
        # for i in xrange(knife_in_warehouse+1, knife_in_warehouse+1+add_number):
            try:
                for i in xrange(1, qty[i-1]+1):
                    new_deviceentry = DeviceEntry.objects.create(
                        journal       = invertory,
                        item          = item,
                        internal_code = knife.code + '%02d' % (i),
                        location      = warehouse,
                        qty           = 1,
                        updated_by    = user,
                        usage_time    = 0,
                        )
            except:
                pass


    return redirect('#')

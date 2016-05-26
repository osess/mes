# coding=utf-8
from models import *
from django.test.client import Client
from django.test import TestCase

from django.core.urlresolvers import reverse

from constants import INVENTORY
import sys

def dumpdata():
    from django.core.management import call_command
    sys.stdout = open('dumped_data.json', 'w')
    call_command('dumpdata', 'warehouse', format='json', indent=4, )
    sys.stdout.close()
    sys.stdout = sys.__stdout__

class SimpleTest(TestCase):
    fixtures = ('warehouse_test_data',)
    
    def test_basic_addition(self):
        from django.contrib.auth.models import User
        user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        
        l1 = Location.objects.get(id=1)
        l2 = Location.objects.get(id=2)
        item = Item.objects.get(code='1001')
        #add 10 each of the base items to l1
        ItemJournal.objects.change(INVENTORY, Item.objects.get(code="1001"), l1, 10, 1)
        ItemJournal.objects.change(INVENTORY, Item.objects.get(code="1002"), l1, 10, 1)
        ItemJournal.objects.change(INVENTORY, Item.objects.get(code="1003"), l1, 10, 1)
        ItemJournal.objects.change(INVENTORY, Item.objects.get(code="1004"), l1, 10, 1)
        ItemJournal.objects.change(INVENTORY, Item.objects.get(code="1005"), l1, 10, 1)
        
        
        self.assertEqual(10, item.inventory()) #10 of item in total
        self.assertEqual(10, item.inventory(l1)) #10 of item in l1
        ItemJournal.objects.move(item, l1, l2, 2, 1) #move 2 to l2
        self.assertEqual(2, item.inventory(l2)) #2 in l2
        self.assertEqual(8, item.inventory(l1)) #8 in l1
        
        #move a single level BOM item from l1 to l2
        j = ItemJournal.objects.move(Item.objects.get(code='1006'), l1, l2, 1, 1)
        self.assertEqual(3, item.inventory(l2)) #now 3 in l2
        self.assertEqual(7, item.inventory(l1)) #and 7 in l1
        
        #move double level BOM item from l1 to l2
        j = ItemJournal.objects.move(Item.objects.get(code='1007'), l1, l2, 1, 1)
        self.assertEqual(5, item.inventory(l2)) #should be +2 in l2
        self.assertEqual(5, item.inventory(l1)) #and -2 in l1
        self.assertEqual(8, j.entries.all().count()) #8 transactions
        entries_list = j.entries.all().order_by('created_at')
        self.assertEqual('<ItemEntry: MOVEMENT;1004;001;-1.0>', repr(entries_list[0]))
        self.assertEqual('<ItemEntry: MOVEMENT;1003;001;-1.0>', repr(entries_list[1]))
        self.assertEqual('<ItemEntry: MOVEMENT;1001;001;-2.0>', repr(entries_list[2]))
        self.assertEqual('<ItemEntry: MOVEMENT;1002;001;-2.0>', repr(entries_list[3]))
        self.assertEqual('<ItemEntry: MOVEMENT;1004;002;1.0>', repr(entries_list[4]))
        self.assertEqual('<ItemEntry: MOVEMENT;1003;002;1.0>', repr(entries_list[5]))
        self.assertEqual('<ItemEntry: MOVEMENT;1001;002;2.0>', repr(entries_list[6]))
        self.assertEqual('<ItemEntry: MOVEMENT;1002;002;2.0>', repr(entries_list[7]))
        
        
        
        test_item = Item.objects.get_by_natural_key('1002')
        test_item.prices.create(starting_at='2010-01-01', amount='5.0')
        from decimal import Decimal
        self.assertEqual(test_item.current_price.amount, Decimal('5.0'))
        
        baseprice=10
        index =1
        for item in Item.objects.all():
            price = ItemPrice(item=item, amount='%s.59' % (baseprice * index))
            index+=1
            price.save()
        dumpdata()
        
        
        self.assertEqual(test_item.current_price.amount, Decimal('20.59'))
        
        
        
        
        
        
class ComplesTests(TestCase):
    fixtures = ('warehouse_test_transactions',)
    
    def test_location_inventory(self):
        item = Item.objects.get(code='1002')
        locations = item.location_inventory()
        l1 = locations[0]
        self.assertEqual(l1.code,'001')
        self.assertEqual(l1.qty_sum, 7)
        
        
    
    def test_web_index(self):
        c = Client(enforce_csrf_checks=True)
        url = reverse('warehouse_index')
        response = c.get(url, follow=True)
        self.assertEqual(200, response.status_code)
       
    def test_web_item_list(self):
        itemcount = Item.objects.all().count()
        self.assertTrue(itemcount>0)
        c = Client(enforce_csrf_checks=True)
        url = reverse('warehouse_item_index')
        response = c.get(url, follow=True)
        self.assertEqual(200, response.status_code)
        self.assertTrue(response.context['item_list'])
        self.assertContains(response, '<tr', itemcount)
        item = Item.objects.all()[0]
        self.assertContains(response, item.get_absolute_url(), 1, msg_prefix=response.content)
        self.assertContains(response, 'asdf', 1)
        self.assertNotContains(response, '<br>')
    
    def test_web_item_detail(self):
        
        c = Client(enforce_csrf_checks=False)
        url = reverse('warehouse_item_detail',  kwargs={'item_code':'1002'})
        
        response = c.get(url, follow=True)
        self.assertEqual(200, response.status_code)
        self.assertTrue(response.context['item_form'])
        
        
        self.assertContains(response, '<td>7.0</td><td>3.0</td><td>0</td>', 1, msg_prefix=response.content)
        form = response.context['item_form']
        data={}
        #print "%r" % form
        for field in form:            
            data[field.name]=form.initial.get(field.name)
        #changing description 
        data['description']='test'
        response = c.post(url, data, follow=True)
        self.assertEqual(200, response.status_code, response.content)
        item = Item.objects.get(code='1002')
        self.assertEqual(item.description, 'test')
        #changeing code
        data['code']='xxxx'
        response = c.post(url, data, follow=True)
        self.assertEqual(200, response.status_code, response.content)
        form = response.context['item_form']
        self.assertFalse(form.errors, form.errors)
        item = Item.objects.get(code='xxxx')
        self.assertEqual(item.description, 'test')
        
        
        

__test__ = {"doctest": """
testing of warehouse

>>> from django.db.models import Sum
>>> item1 = Item(code='1', description='test 1', updated_by_id=1)
>>> item1.save()
>>> item1.id >0
True
>>> item2 = Item(code='2', description='test 2', updated_by_id=1)
>>> item2.save()
>>> item3 = Item(code='3', description='test 3', updated_by_id=1)
>>> item3.save()
>>> item3.bom.create(item=item1, qty=1, updated_by_id=1)
<BomEntry: 3:test 3 1:test 1(1)>

>>> item3.bom.create(item=item2, qty=1, updated_by_id=1)
<BomEntry: 3:test 3 2:test 2(1)>

>>> l1 = Location(code='1', description='default location', updated_by_id=1)
>>> l1.save()
>>> l2 = Location(code='2', description='location 2', updated_by_id=1)
>>> l2.save()
>>> j = ItemJournal.objects.change(INVENTORY, item1, l1, 2, updated_by_id=1)
>>> ItemEntry.objects.filter(item=item1).aggregate(Sum('qty'))
{'qty__sum': 2.0}

>>> j = ItemJournal.objects.change(INVENTORY, item2, l1, 3, updated_by_id=1)
>>> ItemEntry.objects.filter(item=item2).aggregate(Sum('qty'))
{'qty__sum': 3.0}
 
>>> item2.inventory()
3.0
>>> item2.inventory(l2)
0
>>> item1.code
'1'
>>> item2.code
'2'

An item with BOM really affects the BOM items not itself
>>> j = ItemJournal.objects.change(INVENTORY, item3, l1, 2, updated_by_id=1)
>>> item2.inventory()
5.0
>>> item1.inventory()
4.0

"""}


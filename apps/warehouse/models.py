# coding=utf-8
from django.db.models import Model, CharField, FloatField, IntegerField, PositiveSmallIntegerField
from django.db.models import DateTimeField, ForeignKey, BooleanField, ManyToManyField
from django.db.models import DecimalField, DateField, SmallIntegerField
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.db.models import Sum
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from managers import LocationManager, ItemManager, BomEntryManager
from managers import ItemJournalManager
from constants import *

from datetime import timedelta, date

#by lxy
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericRelation
from django.contrib.contenttypes import generic
from yt_barcode.models import Barcode
import base64
from hubarcode.code128 import Code128Encoder
from yt_barcode.views import add_barcode 
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


#__all__ = ['Location', 'Item', 'BomEntry', 'ItemJournal', 'ItemEntry', 'ItemPrice']

#change the choices ''store_house' and 'factory' to 1 and 2
LOCATION_TYPE_CHOICES = (
    (1, _('store_house')),
    (2, _('factory')),
    (3, _('Scrap')),
)
class Location(Model):
    #change theverbose name 'description' to 'name'. by lxy
    name = CharField(_('location name'), max_length=100)
    type = SmallIntegerField(choices=LOCATION_TYPE_CHOICES, default=1, verbose_name=_("location type"))
    code = CharField(_('location code'), max_length=25, unique=True)
    description = CharField(_('location description'), max_length=100, blank=True, null=True)
    lon = FloatField(_('longitude'), blank=True, null=True)
    lat = FloatField(_('latitude'), blank=True, null=True)
    created_at = DateTimeField(_('created at'), auto_now_add=True)
    updated_at = DateTimeField(_('updated at'), auto_now=True)
    updated_by = ForeignKey(User, verbose_name=_("updated_by"))
    objects = LocationManager()

    class Meta:
        verbose_name = _('location')
        verbose_name_plural = _('locations')
        ordering = ('type', '-updated_at')

    def __unicode__(self):
        return u'%s' % (self.name,)

    def natural_key(self):
        return (self.code,)

class ItemJournal(Model):
    TYPE_CHOICES = (
        ('INVENTORY', _('Inventory')),
        ('MOVEMENT', _('Movement')),
        ('IMPORT', _('Import')),
        ('DAMAGE', _('Damage')),
        ('TOTAL', _('Total')),
        ('SALES', _('Sales')),
        ('PURCHASE', _('Purchase')),
        ('SCRAP', _('Scrap')),
        ('SCRAPINVENTORY', _('SrapInventory')),
    )


    created_at = DateTimeField(_('created at'), auto_now_add=True)
    journal_type = CharField(_('journal type'), max_length=10, choices=TYPE_CHOICES)
    note = CharField(_('note'), max_length=100)
    updated_by = ForeignKey(User, verbose_name=_("updated_by"))
    objects = ItemJournalManager()

    class Meta:
        verbose_name = _('item journal')
        verbose_name_plural = _('item journals')

    def __unicode__(self):

        #return u'%s' % (self.journal_type)
        #by lxy
        return u'%s' % (self.get_journal_type_display())

    def change(self, item, at_location, qty):
        bom_list = item.bom.all()
        if len(bom_list) > 0:
            for bom in bom_list:
                if bom.item.bom.all().count() > 0:
                    self.change(bom.item, at_location, (bom.qty * qty))
                else:
                    self.entries.create(item=bom.item, location=at_location, qty=(bom.qty * qty), related_item=item, updated_by_id=self.updated_by_id)
        else:
            self.entries.create(item=item, location=at_location, qty=qty, updated_by_id=self.updated_by_id)


class Item(Model):
    code = CharField(_('item code'), max_length=25, blank=True, null=True)

    #by lxy
    content_type = ForeignKey(ContentType, blank=True, null=True)
    object_id = IntegerField(blank=True, null=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    #description = CharField(_('description'), max_length=100, blank=True, null=True)
    #identifier = CharField(_('identifier'), max_length=50, blank=True, null=True)
    created_at = DateTimeField(_('created at'), auto_now_add=True)
    updated_at = DateTimeField(_('updated at'), auto_now=True)
    #updated_by = ForeignKey(User, verbose_name=_("updated_by"))
    #blocked = BooleanField(default=False, verbose_name=_("blocked"))
    
    objects = ItemManager()

    class Meta:
        verbose_name = _('item')
        verbose_name_plural = _('items')
        ordering = ('id',)
        unique_together = ('content_type', 'object_id')

    def __unicode__(self):
        return u"%s" % (self.content_object,)

    @property
    def name(self):
        return self.content_object.name

    def natural_key(self):
        return (self.code,)

    @property
    def itementry(self):
        inventory   = ItemJournal.objects.get(id=1)
        itementries = self.item_entries.filter(journal=inventory)
        if itementries.count() == 0:
            return None
        elif itementries.count() == 1:
            return itementries[0]
        else:
            return None

    @property
    def warehouse_itementry(self):
        itementries = self.item_entries.filter(journal_id=1,location__type=1)
        if itementries:
            return itementries[0]
        else:
            return None

    @property
    def factory_itementry(self):
        itementries = self.item_entries.filter(journal_id=1,location__type=2)
        if itementries:
            return itementries[0]
        else:
            return None

    @property
    def qty(self):
        if self.itementry:
            return self.itementry.qty
        else:
            return 0
            
    def get_absolute_url(self):
        return reverse('warehouse_item_detail', kwargs={'item_code':self.code})

    def inventory(self, location=None):
        '''
        returns items in inventory for a location (if given) or all.
        '''
        if location:
            sum = self.item_entries.filter(location=location).aggregate(Sum('qty'))['qty__sum']
        else:
            sum = self.item_entries.all().aggregate(Sum('qty'))['qty__sum']
        if sum:
            return sum
        else:
            return 0

    def location_inventory(self):
        '''
        Return Locations for the item and it's aggregated .qty_sum
        for self
        '''
        #from warehouse.db import SumCase
        #locations = Location.objects.aggregate(qty_sum=SumCase('item_entries__qty',  when=self.id ))

        #TODO: Fixa och använd SumCase eller möjligtvis .extra i stället
        sql = """SELECT loc.*,
            Sum(CASE WHEN (ie.item_id=%(item)s) THEN ie.qty ELSE 0 END) as qty_sum
            FROM warehouse_location loc LEFT JOIN
             warehouse_itementry ie ON ie.location_id = loc.id
             GROUP BY ie.location_id
             ORDER BY loc.code
        """
        locations = Location.objects.raw(sql % {'item': self.id})
        return locations

    @property
    def current_price(self):
        '''
        Returns the correct price for today
        '''
        return self.price_for(date.today())

    def price_for(self, for_date):
        return self.prices.get(Q(starting_at__lte=for_date),
                               Q(ending_at__gt=for_date)|
                               Q(ending_at__isnull=True))

    #by lxy
    @property
    def content_object_name(self):
        return self.content_object

    #by xxd
    @property
    def is_device(self):
        item_type = ContentType.objects.get_for_model(self.content_object)
        if item_type.model == 'device':
            return True
        else:
            return False

    @property
    def is_knife(self):
        item_type = ContentType.objects.get_for_model(self.content_object)
        if item_type.model == 'knife':
            return True
        else:
            return False

    @property
    def is_tool(self):
        item_type = ContentType.objects.get_for_model(self.content_object)
        if item_type.model == 'tool':
            return True
        else:
            return False

#by lxy, xxd
CHOICE_TRANSPORT_CATEGORY = (
    (1, _("Output")),
    (2, _("Input")),
    (3, _("Scrap")),#报废
    (4, _("Borrow")),#借出
    (5, _("Return")),#归还
)

CHOICE_STATE = (
    (1, _("Waitting")),
    (2, _("Already Output")),
    (3, _("Already Input")),
    (4, _("Already Scrap")),
    (5, _("Error")),
)

class BomEntry(Model):
    parent = ForeignKey(Item, related_name='bom', blank=True, null=True, verbose_name=_("product"))
    item = ForeignKey(Item, verbose_name=_("item"))
    unit = CharField(max_length=25, blank=True, verbose_name=_("unit"))
    qty = FloatField(_('quantity'))
    created_at = DateTimeField(_('created at'), auto_now_add=True)
    updated_at = DateTimeField(_('updated at'), auto_now=True)
    updated_by = ForeignKey(User, verbose_name=_("updated_by"))
    objects = BomEntryManager()
    
    productionline = ForeignKey('manufactureplan.ProductionLine', blank=True, null=True, related_name='boms', verbose_name=_("productionline"))
    state = PositiveSmallIntegerField(choices=CHOICE_STATE, default=1, verbose_name=_("bom state"))
    bom_category = PositiveSmallIntegerField(choices=CHOICE_TRANSPORT_CATEGORY, default=1, verbose_name=_("bom_category"))
    note = CharField(max_length=25, blank=True, verbose_name=_("note"))
    finish_time = DateTimeField(_('finsih_time'))

    class Meta:
        verbose_name = _('BOM entry')
        verbose_name_plural = _('BOM entries')
        unique_together = (('productionline', 'parent', 'item'),)

    def __unicode__(self):
        return u'%s %s(%d)' % (self.parent, self.item, self.qty)

    @property
    def sum_qty(self):
        item_entries = ItemEntry.objects.filter(item=self.item,journal_id=1,location_id=1)
        sum_qty = 0
        if item_entries:
            for item_entry in item_entries:
                sum_qty += item_entry.qty
        return sum_qty
    @property
    def is_enough(self):
        if self.sum_qty < self.qty:
            return False
        else:
            return True

    def natural_key(self):
        return self.parent.natural_key() + self.item.natural_key()
    natural_key.dependencies = ['warehouse.item']

    #by xxd
    @property
    def manufactureplan(self):
        return self.productionline.manufactureplan

CHOICE_LIST_CATEGORY = (
    (1, _("ManufactureItem")),  
    (2, _("Device")),
    (3, _("Knife")),
    (4, _("Tool")),
    (5, _("Material")),
)


#by lxy
class TransportList(Model):
    internal_code = CharField(max_length=25, blank=True, null=True, verbose_name=_("internal_code"))
    list_category = PositiveSmallIntegerField(choices=CHOICE_LIST_CATEGORY, verbose_name=_("list_category"))
    transport_category = PositiveSmallIntegerField(choices=CHOICE_TRANSPORT_CATEGORY, verbose_name=_("transport_category"))
    state = PositiveSmallIntegerField(choices=CHOICE_STATE, default=1, verbose_name=_("transport list state"))
    created_at = DateTimeField(_('created at'), auto_now_add=True)
    updated_at = DateTimeField(_('updated at'), auto_now=True)
    updated_by = ForeignKey(User, related_name="transportlists", verbose_name=_("updated_by"))

    productionline = ForeignKey('manufactureplan.ProductionLine', blank=True, null=True, related_name='transport_lists', verbose_name=_("productionline"))
    
    applicat = ForeignKey(User, related_name="my_transportlists", verbose_name=_("applicat"))
    
    class Meta:
        verbose_name = _('TransportList')
        verbose_name_plural = _('TransportLists')
        unique_together = ('list_category', 'transport_category', 'productionline')

    def __unicode__(self):
        return u'%s | %s' % (self.get_list_category_display(), self.get_transport_category_display())

    @property
    def file(self):
        if self.productionline.manufactureplan.file:
            return self.productionline.manufactureplan.file
        else:
            return None

    #by xxd
    @property
    def is_applied(self):
        is_applied = True
        for transport_detail in self.transport_list_details.all():
            if not transport_detail.is_applied:
                is_applied = False
                break
        return is_applied

    @property
    def is_enough(self):
        for transport_detail in self.transport_list_details.all():
            if not transport_detail.is_enough:
                return False
        return True

    @property
    def detail_values(self):
        detail_values = "<a name='show_transportlist_modal' hide='"
        detail_values += str(self.id) + "' model_title='" + self.__unicode__()
        detail_values += "' data-toggle='modal' href='#TransportListDetail'>"
        for detail_value in self.transport_list_details.all():
            detail_values += detail_value.item.name
            detail_values += ":"
            detail_values += str(detail_value.qty)
            detail_values += " "
            detail_values += detail_value.unit
            detail_values += " | "
        if detail_values.endswith(" | "):
            detail_values = detail_values[0:-3]
        detail_values += "</a>"
        return detail_values

    @property
    def details(self):
        detail_values = "<a name='show_transportlist_modal' hide='%s' model_title='%s' \
                         data-toggle='modal' href='#TransportListDetail'>%s</a>" % \
                         (str(self.id), self.__unicode__(), unicode(_("detail")))
        return detail_values


#by lxy
class TransportListDetail(Model):
    transport_list = ForeignKey(TransportList, related_name = "transport_list_details", verbose_name=_("transport_list"))
    item_entry_code = CharField(max_length=25, blank=True, null=True, verbose_name=_("item_entry_code"))
    item = ForeignKey(Item, related_name = "transport_list_detail", verbose_name=_("item"))
    qty = FloatField(_('quantity'), default=1)
    unit = CharField(max_length=25, blank=True, null=True, verbose_name=_("unit"))
    # state = PositiveSmallIntegerField(choices=CHOICE_STATE, default=1, verbose_name=_("transport list detail state"))
    created_at = DateTimeField(_('created at'), auto_now_add=True)
    updated_at = DateTimeField(_('updated at'), auto_now=True)
    updated_by = ForeignKey(User, verbose_name=_("updated_by"))

    #by xxd
    content_type = ForeignKey(ContentType, blank=True, null=True)
    object_id = IntegerField(blank=True, null=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    location = ForeignKey(Location, related_name="transport_list_details", verbose_name=_("location"))
    note     = CharField(max_length=25, blank=True, null=True, verbose_name=_("note"))
    
    class Meta:
        verbose_name = _('TransportListDetail')
        verbose_name_plural = _('TransportListDetails')

    def __unicode__(self):

        return u'%s' % (self.item)

    #by xxd
    @property
    def is_applied(self):
        if self.item_entry_code:
            return True
        else:
            return False

    @property
    def is_enough(self):
        #if self.item.content_type.model == 'device':
        #    return True
        #else:
        if 1:
            if self.inventory < self.qty:
                return False
            else:
                return True

    @property
    def inventory(self):
        inventory = ItemJournal.objects.get(id=1)
        warehouse = Location.objects.get(id=1)
        item_entries = ItemEntry.objects.filter(
            item__id=self.item_id,
            journal = inventory,
            location = warehouse
        )
        if len(item_entries) > 0:
            return len(item_entries) #item_entries[0].qty
        return 0

#by xxd
class Application(Model):
    manufactureplan = ForeignKey('manufactureplan.ManufacturePlan', related_name='applications', verbose_name=_("manufactureplan"))
    technology      = ForeignKey('technologies.Technology', related_name="applications", verbose_name=_("technology"))
    created_at      = DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name        = _('Application')
        verbose_name_plural = _('Applications')
        unique_together     = ('manufactureplan', 'technology')
        ordering            = ('-created_at',)

    def __unicode__(self):
        return u'%s | %s' % (self.manufactureplan, self.technology)



class ItemEntry(Model):
    journal         = ForeignKey(ItemJournal, related_name='entries', verbose_name=_('journal'))
    created_at      = DateTimeField(_('created at'), auto_now_add=True)
    internal_code   = CharField(_('internal_code'), max_length=25, blank=True, null=True)
    item            = ForeignKey(Item, related_name='item_entries', verbose_name =_('item'))
    location        = ForeignKey(Location, related_name='item_entries', verbose_name =_('location'))
    unit            = CharField(max_length=25, blank=True, verbose_name=_("unit"))
    qty             = FloatField(_('quantity'), default=0)
    #related_item = ForeignKey(Item, related_name='related_entries', blank=True, null=True)
    #arrive_factury_date = DateField(blank=True, null=True, verbose_name=_("arrive_factury_date"))
    updated_by = ForeignKey(User, verbose_name =_('updated_by'))
    arrive_factury_date = DateField(blank=True, null=True, verbose_name=_("arrive_factury_date"))

    owner    = ForeignKey('customer.Customer', related_name='item_entries', blank=True, null=True, verbose_name=_("material owner"))
    furnace_batch   = CharField(max_length=125, blank=True, null=True, verbose_name=_("material furnace_batch"))
    
    transport_list_detail = ForeignKey(TransportListDetail, related_name='item_entry', blank=True, null=True, verbose_name=_("transport_list_detail"))

    class Meta:
        verbose_name = _('item entry')
        verbose_name_plural = _('item entrys')
        ordering = ('-created_at',)

    def __unicode__(self):
        return u'%s:%s' % (self.item,self.internal_code if self.internal_code else "")

    @property
    def code(self):
        return self.internal_code

    @property
    def name(self):
        return self.item.name

    @property
    def in_service(self):
        return self.location.type == 2

class DeviceEntry(ItemEntry):
    usage_time = IntegerField(max_length=255, default=0, verbose_name=_("usage_time"))
    origin_place     = CharField(max_length=255, blank=True, null=True, verbose_name=_("origin place"))
    
    class Meta:
        verbose_name = _('device entry')
        verbose_name_plural = _('device entrys')

    @property
    def is_using(self):
        return True
        
    @property
    def item_content_type(self):
        return self.item.content_type.name
        
class ItemPrice(Model):
    item = ForeignKey(Item, related_name='prices', verbose_name=_('item'))
    amount = DecimalField(verbose_name=_('price'), max_digits=8, decimal_places=2)
    starting_at = DateField(default=date.today)
    ending_at = DateField(blank=True, null=True, default=None)

    def save(self, end_previous=True, *args, **kwargs):
        super(ItemPrice, self).save(*args, **kwargs)
        if end_previous:
            
            '''
            Making sure that the previous price for this item ends at
            a appropriate date.
            '''
            try:
                prev = self.get_previous_by_starting_at(item=self.item)
                prev.ending_at=self.starting_at -timedelta(days=1)
                prev.save()
            except ItemPrice.DoesNotExist:
                #nothing to do..., first in line
                pass

class Expense(Model):

    date = DateField(_('date'))
    cost = FloatField(_('cost'), max_length=25)
    prepay = FloatField(_('prepay'), blank=True, null=True, max_length=25)

    class Meta:
        verbose_name = _('expense')
        verbose_name_plural = _('expenses')

    def __unicode__(self):
        cost = self.cost
        prepay = self.prepay
        if prepay == None:
            return u'%s, %s'% (self.date, cost)
        else:
            return u'%s, %s, %s'% (self.date, cost, prepay )


class ElectricityCharge(Model):

    date = DateField(_('date'))
    kilowatt = FloatField(_('kilowatt'), max_length=25)
    expense = ForeignKey(Expense, verbose_name=_('expense'))

    class Meta:
        verbose_name = _('electricity charge')
        verbose_name_plural = _('electricity charges')


CHOICE_TRANSFER_CATEGORY = (
    (1, _("Output")),  
    (2, _("Import")),
    (3, _("Borrow")),
    (4, _("Return")),
    #(5, _("Sharpen")),
)
class TransferList(Model):
    applicat            = ForeignKey(User, related_name='transfer_list', verbose_name=_("applicat transfer_list"))   
    accept_date         = DateField(verbose_name=_("accept_date transfer_list"))
    transfer_category   = PositiveSmallIntegerField(choices=CHOICE_TRANSFER_CATEGORY, verbose_name=_("transfer_category"))
    state               = PositiveSmallIntegerField(choices=CHOICE_STATE, default=1, verbose_name=_("transfer_list state"))
    
    device_entries      = ManyToManyField(DeviceEntry, blank=True, null=True, related_name="transfer_list", verbose_name=_("device_entries"))
    
    created_at          = DateTimeField(_('created at'), auto_now_add=True)
    updated_at          = DateTimeField(_('updated at'), auto_now=True)
    #updated_by          = ForeignKey(User, related_name='created_transfers_list', verbose_name=_("updated_by transfer_list"))

    class Meta:
        verbose_name = _('TransferList')
        verbose_name_plural = _('TransferLists')

    def __unicode__(self):
        return u'%s | %s' % (self.applicat, self.get_transfer_category_display())

    def save(self, *args, **kwargs):
        super(TransferList, self).save(*args, **kwargs)

        for device_entry in self.device_entries.all():
            #set inventory qty
            if self.transfer_category in [1,3,5]:
                device_entry.qty -= 1
            elif self.transfer_category in [2,4]:
                device_entry.qty += 1
            device_entry.save()
from django.db.models import TextField

class EntryLog(Model):
    item_entry = ForeignKey(ItemEntry, related_name='entry_logs', verbose_name=_("item entry"))
    log = TextField(max_length=255, blank=True, null=True, verbose_name=_("entry log"))
    date_added = DateTimeField(auto_now_add=True, verbose_name=_("date_added"))

    class Meta:
        verbose_name = _('EntryLog')
        verbose_name_plural = _('EntryLogs')

    def __unicode__(self):
        return u'%s' % (self.log)

class TransportDetailRecord(Model):
    name          = CharField(max_length=128, unique=False, blank=True, null=True, verbose_name=_('component name'))
    category      = CharField(max_length=128, unique=False, blank=True, null=True, verbose_name=_('category'))
    norm_code     = CharField(max_length=255, unique=False, blank=True, null=True, verbose_name=_("norm_code"))
    cad_code      = CharField(max_length=128, unique=False, blank=True, null=True, verbose_name=_('cad_code'))
    furnace_batch = CharField(max_length=125, unique=False, blank=True, null=True, verbose_name=_("material furnace_batch"))
    unit          = CharField(max_length=128, unique=False, blank=True, null=True, verbose_name=_('unit'))
    amount        = IntegerField(max_length=128, unique=False, blank=True, null=True, verbose_name=_('amount'))
    note          = CharField(max_length=128, unique=False, blank=True, null=True, verbose_name=_('transport note'))
    transport_list_detail = ForeignKey(TransportListDetail, unique=True, verbose_name=_('transport list detail'))
    transport_list_number = CharField(max_length=128, unique=False, blank=True, null=True, verbose_name=_('transport list number'))
    
    created_at    = DateTimeField(_('created at'), auto_now_add=True)
    updated_at    = DateTimeField(_('updated at'), auto_now=True)
    from_item_entry  = ForeignKey(ItemEntry, related_name='transport_detail_from', blank=True, null=True, verbose_name=_('from item entry'))
    to_item_entry    = ForeignKey(ItemEntry, related_name='transport_detail_to', blank=True, null=True, verbose_name=_('to item entry'))
    from_inventory   = IntegerField(max_length=50, default=0, verbose_name=_('from inventory'))
    to_inventory     = IntegerField(max_length=50, default=0, verbose_name=_('to inventory'))
    inventory_item_entry    = ForeignKey(ItemEntry, related_name='transport_detail_inventory', blank=True, null=True, verbose_name=_('inventory item entry'))
    inventory_qty   = IntegerField(max_length=50, verbose_name=_('inventory qty'))
    
    @property
    def list_category(self):
        pass

    @property
    def transport_category(self):
        pass

    @property
    def scrap_item_entry(self):
        if self.transport_list_detail.transport_list.transport_category == 3:
            return self.to_item_entry
        else:
            return None

    @property
    def scrap_qty(self):
        if self.transport_list_detail.transport_list.transport_category == 3:
            return self.to_inventory
        else:
            return None

    class Meta:
        verbose_name = _('TransportDetailRecord')
        verbose_name_plural = _('TransportDetailRecords')

    def __unicode__(self):
        return u'%s' % (self.name)
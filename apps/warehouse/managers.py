# coding=utf-8
'''
Created on Jan 12, 2011

@author: peterm
'''
from django.db.models import Manager
from constants import MOVEMENT

__all__ = ['LocationManager',
           'ItemManager',
           'BomEntryManager',
           'ItemJournalManager']

class LocationManager(Manager):
    def get_by_natural_key(self, code):
        return self.get(code=code)
    
class ItemManager(Manager):
    def get_by_natural_key(self, code):
        return self.get(code=code)
    
class BomEntryManager(Manager):
    def get_by_natural_key(self, parent_code, item_code):
        return self.get(parent__code=parent_code, item__code=item_code)

class ItemJournalManager(Manager):
    #TODO: howto ensure all this is done as a transaction?
    def move(self, item, from_location, to_location, qty, updated_by_id):
        journal = self.model(journal_type=self.model.TYPE_CHOICES[MOVEMENT][0], updated_by_id=updated_by_id)
        journal.save()
        journal.change(item, from_location, qty * -1)
        journal.change(item, to_location, qty)
        return journal
    
    def change(self, type_no, item, at_location, qty, updated_by_id):
        journal = self.model(journal_type=self.model.TYPE_CHOICES[type_no][0], updated_by_id=updated_by_id)
        journal.save()
        journal.change(item, at_location, qty)
        return journal

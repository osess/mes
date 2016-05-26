from django.conf.urls.defaults import *
from django.conf import settings

from views import products

urlpatterns = patterns('netwizard.weboffer.views',
  url(r'produkty/$', products.list, name='weboffer-product-list'),
  url(r'produkty/(?P<category>\d+)/$', products.list, name='weboffer-product-list'),
  url(r'produkty/(?P<category_name>[a-z-0-9]+),(?P<category>\d+)/$', products.list, name='weboffer-product-list'),
  url(r'produkt/(?P<id>\d+).html$', products.detail, name='weboffer-product-page'),
  url(r'produkt/(?P<slug>[a-z0-9-_]+).html$', products.detail, name='weboffer-product-detail'),
  url(r'produkt/(?P<id>\d+).html$', products.detail, name='weboffer-product-detail'),
  url(r'$', products.list, name='weboffer-product-list'),
)
   

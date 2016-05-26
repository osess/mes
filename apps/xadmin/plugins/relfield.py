from django.db import models
from django.utils.html import escape
from django.utils.text import Truncator
from django.utils.translation import ugettext as _
from django import forms
from xadmin.sites import site
from xadmin.views import BaseAdminPlugin, ModelFormAdminView
from xadmin.util import vendor

try:
    from django.utils.html import format_html
except ImportError:
    # support django < 1.5. Taken from django.utils.html
    from django.utils import six
    def conditional_escape(text):
        """
Similar to escape(), except that it doesn't operate on pre-escaped strings.
"""
        if isinstance(text, SafeData):
            return text
        else:
            return escape(text)

    def format_html(format_string, *args, **kwargs):
        """
Similar to str.format, but passes all arguments through conditional_escape,
and calls 'mark_safe' on the result. This function should be used instead
of str.format or % interpolation to build up small HTML fragments.
"""
        args_safe = map(conditional_escape, args)
        kwargs_safe = dict([(k, conditional_escape(v)) for (k, v) in
                            six.iteritems(kwargs)])
        return mark_safe(format_string.format(*args_safe, **kwargs_safe))

class ForeignKeySearchWidget(forms.TextInput):

    def __init__(self, rel, admin_view, attrs=None, using=None):
        self.rel = rel
        self.admin_view = admin_view
        self.db = using
        super(ForeignKeySearchWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        to_opts = self.rel.to._meta
        if attrs is None:
            attrs = {}
        if "class" not in attrs:
            attrs['class'] = 'select-search'
        else:
            attrs['class'] = attrs['class'] + ' select-search'
        attrs['data-search-url'] = self.admin_view.get_admin_url(
            '%s_%s_changelist' % (to_opts.app_label, to_opts.module_name))
        attrs['data-placeholder'] = _('Search %s') % to_opts.verbose_name
        attrs['data-choices'] = '?'
        if self.rel.limit_choices_to:
            for i in list(self.rel.limit_choices_to):
                attrs['data-choices'] += "&_p_%s=%s" % (i, self.rel.limit_choices_to[i])
            attrs['data-choices'] = format_html(attrs['data-choices'])
        if value:
            attrs['data-label'] = self.label_for_value(value)

        return super(ForeignKeySearchWidget, self).render(name, value, attrs)

    def label_for_value(self, value):
        key = self.rel.get_related_field().name
        try:
            obj = self.rel.to._default_manager.using(
                self.db).get(**{key: value})
            return '%s' % escape(Truncator(obj).words(14, truncate='...'))
        except (ValueError, self.rel.to.DoesNotExist):
            return ""

    @property
    def media(self):
        return vendor('select.js', 'select.css', 'xadmin.widget.select.js')


class RelateFieldPlugin(BaseAdminPlugin):

    def get_field_style(self, attrs, db_field, style, **kwargs):
        # search able fk field
        if style == 'fk-ajax' and isinstance(db_field, models.ForeignKey):
            if (db_field.rel.to in self.admin_view.admin_site._registry) and \
                    self.has_model_perm(db_field.rel.to, 'view'):
                db = kwargs.get('using')
                return dict(attrs or {}, widget=ForeignKeySearchWidget(db_field.rel, self.admin_view, using=db))
        return attrs

site.register_plugin(RelateFieldPlugin, ModelFormAdminView)

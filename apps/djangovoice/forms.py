from django import forms
from djangovoice.models import Feedback


class WidgetForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = (
            'email', 'type', 'anonymous', 'private', 'title', 'description')


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        exclude = ('status', 'user', 'slug', 'duplicate')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(FeedbackForm, self).__init__(*args, **kwargs)

        # add class to fix width of title input and textarea:
        for field_name in ['title', 'description']:
            field = self.fields[field_name]
            field.widget.attrs.update({'class': 'input-block-level'})

        # change form fields for user authentication status:
        if self.user is not None and self.user.is_authenticated():
            deleted_fields = ['email']
        else:
            deleted_fields = ['anonymous', 'private']

        for field_name in deleted_fields:
            del self.fields[field_name]

        # add tabindex attribute to fields:
        for index, field in enumerate(list(self.fields.values()), 1):
            field.widget.attrs.update({'tabindex': index})

    def clean(self):
        cleaned_data = super(FeedbackForm, self).clean()

        return cleaned_data

    def clean_email(self):
        field = self.cleaned_data.get('email')

        if field is None and self.user is not None:
            field = self.user.email

        return field

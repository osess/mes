import uuid
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseNotFound
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.views.generic import DeleteView, DetailView, FormView, ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from djangovoice.models import Feedback, Type
from djangovoice.forms import WidgetForm, FeedbackForm
from djangovoice.mixins import VoiceMixin
from djangovoice.settings import ALLOW_ANONYMOUS_USER_SUBMIT


class FeedbackDetailView(VoiceMixin, DetailView):
    template_name = 'djangovoice/detail.html'
    model = Feedback

    def get(self, request, *args, **kwargs):
        feedback = self.get_object()

        if feedback.private:
            # Anonymous private feedback can be only accessed with slug
            if (not request.user.is_staff
                    and not 'slug' in kwargs
                    and feedback.user is None):
                raise PermissionDenied

            if (not request.user.is_staff
                    and request.user != feedback.user
                    and feedback.user is not None):
                raise PermissionDenied

        return super(FeedbackDetailView, self).get(request, *args, **kwargs)


class FeedbackListView(VoiceMixin, ListView):
    template_name = 'djangovoice/list.html'
    model = Feedback
    paginate_by = 10

    def get_queryset(self):
        f_list = self.kwargs.get('list', 'open')
        f_type = self.kwargs.get('type', 'all')
        f_status = self.kwargs.get('status', 'all')
        f_filters = {}
        # Tag to display also user's private discussions
        f_showpriv = False

        # add filter for list value, and define title.
        if f_list in ['open', 'closed']:
            f_filters.update(dict(status__status=f_list))

        elif f_list == 'mine':
            f_filters.update(user=self.request.user)

        # add filter for feedback type.
        if f_type != 'all':
            f_filters.update(dict(type__slug=f_type))

        # add filter for feedback status.
        if f_status != 'all':
            f_filters.update(dict(status__slug=f_status))

        # If user is checking his own feedback, do not filter by private
        # for everyone's discussions but add user's private feedback
        if not self.request.user.is_staff and f_list != 'mine':
            f_filters.update({'private': False})
            f_showpriv = True

        if f_showpriv and self.request.user.is_authenticated():
            # Show everyone's public discussions and user's own private
            # discussions
            queryset = self.model.objects.filter(
                Q(**f_filters) | Q(user=self.request.user, private=True))
        else:
            queryset = self.model.objects.filter(**f_filters)

        queryset = queryset.order_by('-vote_score', '-created')

        return queryset

    def get_context_data(self, **kwargs):
        f_list = self.kwargs.get('list', 'open')
        f_type = self.kwargs.get('type', 'all')
        f_status = self.kwargs.get('status', 'all')

        title = _("Feedback")

        if f_list == 'open':
            title = _("Open Feedback")

        elif f_list == 'closed':
            title = _("Closed Feedback")

        elif f_list == 'mine':
            title = _("My Feedback")

        # update context data
        data = super(FeedbackListView, self).get_context_data(**kwargs)
        data.update({
            'list': f_list,
            'status': f_status,
            'type': f_type,
            'navigation_active': f_list,
            'title': title
        })

        return data

    def get(self, request, *args, **kwargs):
        f_list = kwargs.get('list')

        if f_list == 'mine' and not request.user.is_authenticated():
            to_url = (
                reverse('django.contrib.auth.views.login') +
                '?next=%s' % request.path)

            return redirect(to_url)

        return super(FeedbackListView, self).get(request, *args, **kwargs)


class FeedbackWidgetView(FormView):
    template_name = 'djangovoice/widget.html'
    form_class = WidgetForm

    def get(self, request, *args, **kwargs):
        return super(FeedbackWidgetView, self).get(request, *args, **kwargs)

    def get_initial(self):
        return {'type': Type.objects.get(pk=1)}

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        return super(FeedbackWidgetView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        feedback = form.save(commit=False)
        if form.cleaned_data.get('anonymous') != 'on':
            feedback.user = self.request.user
        feedback.save()

        messages.add_message(
            self.request, messages.SUCCESS, _("Thanks for feedback."))

        return redirect('djangovoice_widget')

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR,
                             _("Form is invalid."))

        return super(FeedbackWidgetView, self).form_invalid(form)


class FeedbackSubmitView(VoiceMixin, FormView):
    template_name = 'djangovoice/form.html'
    form_class = FeedbackForm

    def get_context_data(self, **kwargs):
        return super(FeedbackSubmitView, self).get_context_data(**kwargs)

    def dispatch(self, request, *args, **kwargs):
        # if project doesn't allow anonymous user submission, check
        # authentication:
        if (not ALLOW_ANONYMOUS_USER_SUBMIT
                and not request.user.is_authenticated()):
            login_url = reverse('django.contrib.auth.views.login')
            return redirect(login_url + '?next=%s' % request.path)

        return super(FeedbackSubmitView, self).dispatch(
            request, *args, **kwargs)

    def get_form_kwargs(self):
        # define user in form, some form data return fields for user
        # authentication.
        kwargs = super(FeedbackSubmitView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})

        return kwargs

    def form_valid(self, form):
        feedback = form.save(commit=False)

        if self.request.user.is_anonymous() and ALLOW_ANONYMOUS_USER_SUBMIT:
            feedback.private = True
            feedback.anonymous = True

        elif not form.cleaned_data.get('anonymous', False):
            feedback.user = self.request.user

        if not feedback.user:
            feedback.slug = uuid.uuid1().hex[:10]

        feedback.save()

        # If there is no user, show the feedback with slug
        if not feedback.user:
            response = redirect('djangovoice_slug_item', slug=feedback.slug)

        else:
            response = redirect(feedback)

        return response


class FeedbackEditView(FeedbackSubmitView):
    template_name = 'djangovoice/form.html'
    form_class = FeedbackForm

    def get_object(self):
        return Feedback.objects.get(pk=self.kwargs.get('pk'))

    def get_form_kwargs(self):
        kwargs = super(FeedbackEditView, self).get_form_kwargs()
        kwargs.update({'instance': self.get_object()})

        return kwargs

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        if not form_class:
            raise HttpResponseNotFound

        return super(FeedbackEditView, self).get(request, *args, **kwargs)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        return super(FeedbackEditView, self).post(request, *args, **kwargs)


class FeedbackDeleteView(VoiceMixin, DeleteView):
    template_name = 'djangovoice/delete.html'

    def get_object(self):
        return Feedback.objects.get(pk=self.kwargs.get('pk'))

    def get_context_data(self, **kwargs):
        return super(FeedbackDeleteView, self).get_context_data(**kwargs)

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        # FIXME: should feedback user have delete permissions?
        feedback = self.get_object()
        if not request.user.is_staff and request.user != feedback.user:
            raise HttpResponseNotFound

        return super(FeedbackDeleteView, self).get(request, *args, **kwargs)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        feedback = self.get_object()
        feedback.delete()

        return redirect('djangovoice_home')

#-*- coding: UTF-8 -*- 
from django.db import models
from django.contrib.auth.models import User
from companydepartment.models import Department
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields import AutoSlugField

BENEFIT_CHOICES = (
        (1, _("SocialSecurity")),
        (2, _("Benefit")),
)

class BenefitType(models.Model):
    name = models.CharField(max_length=30,unique=True, verbose_name=_("benefit type name"))
    display_name = models.CharField(max_length=30, verbose_name=_("display name"))
    code = models.CharField(max_length=30, verbose_name=_("benefit code"))
    category = models.PositiveSmallIntegerField(choices=BENEFIT_CHOICES, verbose_name=_("benefit category"), blank=True, null=True)
    appear_on_payslip = models.BooleanField(default=False, verbose_name=_("appera on payslip"))
    active = models.BooleanField(default=True, verbose_name=_("benefit active"))

    order = models.IntegerField(default=99, verbose_name=_("benefit order"))
    amount_fix = models.FloatField(default=0.00,blank=True, verbose_name=_("amount fix"))
    amount_percentage = models.FloatField(default=0.00,blank=True, verbose_name=_("amount percentage"))
    amount_code = models.TextField(default='0.00', blank=True, verbose_name=_("amount code"))
    placeholder = models.CharField(default='0.00', max_length=30, verbose_name=_("placeholder"))
    note = models.CharField(max_length=30, verbose_name=_("note"))

    class Meta:
        verbose_name_plural = _('BenefitType')
        verbose_name = _('BenefitType')
        ordering = ('category','order','name',)

    def __unicode__(self):
        return "%s" %(self.name)


IMPORTANCE_CHOICES = (
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
    (6, 6),
    (7, 7),
    (8, 8),
    (9, 9),
    (10, 10),
)
class Position(models.Model):
    name = models.CharField(max_length=75, unique=True, verbose_name=_("posotion name"))
    importance = models.PositiveSmallIntegerField(choices=IMPORTANCE_CHOICES, blank=True, null=True, verbose_name=_("importance"))
    private_description = models.TextField(blank=True, help_text=_("This is private and never displayed to the public via the website."), verbose_name=_("private desc"))
    public_description = models.TextField(blank=True, help_text=_("This is the public description displayed via the website."), verbose_name=_("public desc"))

    class Meta:
        verbose_name_plural = _('Position')
        verbose_name = _('Position')
        ordering = ('-importance',)

    def save(self):
        """
        When saving a position, considering changing the evluation status of all its related
        job opportunity's evaluations to status="Candidacy closed"
        """
        super(Position, self).save()

    def __unicode__(self):
        return "%s" %(self.name)


class Job(models.Model):
    POSITION_STATUS = (
        (1, _("Open")),
        (2, _("Filled")),
        (3, _("Closed")),
    )

    OPPORTUNITY_STATUS_CHOICES = (
        (1, _('Unpublished')),
        (2, _('Published')),
    )

    """
    CONTRACT_TYPES = (
        (0, "Employee - Full-Time"),
        (1, "Independent Contractor - Full-Time"),
        (2, "Employee - Part-Time"),
        (3, "Independent Contractor - Part-Time"),
        (4, "Internship - Full-Time"),
        (5, "Internship - Part-Time"),
    )
    """

    status = models.PositiveSmallIntegerField(choices=POSITION_STATUS, default=1, verbose_name=_("status"))
    published_status = models.PositiveSmallIntegerField(choices=OPPORTUNITY_STATUS_CHOICES, default=1, verbose_name=_("published status"))
    pay = models.IntegerField(blank=True, default=0, verbose_name=_("pay"))
    benefits = models.ManyToManyField(BenefitType, blank=True, null=True, verbose_name=_("benefits"))
    department = models.ForeignKey(Department,blank=False, verbose_name=_("department"))
    position = models.ForeignKey(Position, blank=False, related_name="job_opportunities", verbose_name=_("position"))
    location = models.CharField(max_length=150,blank=True, verbose_name=_("location"))
    slug = AutoSlugField(max_length=150, populate_from=('department', 'position'), overwrite=True, verbose_name=_("slug"))
    #contract_types = models.ManyToManyField("ContractType",blank=True, verbose_name=_("contract types"))
    num_of_planed_employees =  models.IntegerField(default=0, verbose_name=_("NPEes")) #0 means no limitation
    num_of_vacancies = models.IntegerField(default=0, verbose_name=_("num of vacancies")) #0 means no vacancy
    note = models.CharField(max_length=500, blank=True, verbose_name=_("note"))

    def get_absolute_url(self):
        return ('/jobs/%s/' %(self.slug))
        #return reverse('job_page', kwargs={"position_slug": self.position.slug, "location_slug": self.location_slug, "job_id": self.pk})

    def __unicode__(self):
        return "%s - %s" %(self.department.name, self.position.name)

    class Meta:
        verbose_name = _('jobs')
        verbose_name_plural = _('jobs')
        ordering = ('department',)


class Person(models.Model):
    user = models.ForeignKey(User, unique=True, blank=True, null=True, verbose_name=_("user"))
    name = models.CharField(max_length=125,unique=True, verbose_name=_("person name"))
    description = models.CharField(max_length=250, blank=True, verbose_name=_("person description"))
    gender = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("gender"))


    class Meta:
        abstract = True
        ordering = ('-name',)

    def __unicode__(self):
        return "%s" %(self.name)
    
class Employee(Person):
    internal_id = models.CharField(max_length=30, unique=True, verbose_name=_("internal_id"))
    department = models.ForeignKey(Department, blank=True, null=True, related_name="employee", verbose_name=_("department"))
    job = models.ForeignKey(Job, blank=True, null=True, verbose_name=_("Job"))
    join_date = models.DateField(blank=True, null=True, verbose_name=_("join_date"))
    note = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("note"))    

    class Meta:
        verbose_name_plural = _('Employees')
        verbose_name = _('Employee')
        ordering = ('internal_id',)

from django.contrib.auth.hashers import make_password
class UserPlainPassword(models.Model):

    username = models.CharField(_('username'), max_length=30, unique=True)
    password = models.CharField(_('password'), max_length=128)

    class Meta:
        verbose_name_plural = _('UserPlainPasswords')
        verbose_name = _('UserPlainPassword')
        ordering = ('username',)

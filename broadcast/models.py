from datetime import date
from dateutil.relativedelta import relativedelta
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

communication_mode = (
    ('sms', 'SMS'),
    ('whatsapp', 'WhatsApp'),
    ('email', 'Email'),
)


class Announcement(models.Model):

    receipients = models.TextField()

    subject = models.CharField(
        max_length=100)

    message = models.TextField()

    mode = models.CharField(
        max_length=8,
        default='sms')

    group = models.CharField(
        max_length=50,
        default='all')

    broadcast_dt = models.DateTimeField()

    user_created = models.ForeignKey(
        User,
        on_delete=models.PROTECT)

    class Meta:
        app_label = 'broadcast'


def valid_employee_dob(value):
    min_age = 18
    min_date = date.today() + relativedelta(years=min_age)
    if value < min_date:
        raise ValidationError(
            _(f'{value} is before {min_date}. Employee age '
              'cannot be less than 18 years.'))


class Employee(models.Model):

    user = models.ForeignKey(
        User, on_delete=models.CASCADE)

    employee_id = models.CharField(
        max_length=10,
        primary_key=True)

    first_name = models.CharField(
        max_length=20)

    last_name = models.CharField(
        max_length=20)

    dob = models.DateField(
        validators=[valid_employee_dob])

    ministry = models.CharField(
        verbose_name=('Ministry employed under '
                      'e.g. Ministry of Education'), # ministries
        max_length=100)

    job_position = models.CharField(
        verbose_name='Job position e.g. Senior Teacher/Accountant',
        max_length=100)

    salary_scale = models.CharField(
        verbose_name='Salary scale e.g. B2/C1',
        max_length=2)

    contact_details = models.CharField(
        verbose_name='Contact number',
        max_length=8)

    class Meta:
        app_label = 'broadcast'


class Documents(models.Model):
    title = models.CharField(max_length=100)
    type = models.CharField(max_length=100)

    def __str__(self):
        return self.title

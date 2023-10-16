from datetime import date, timedelta
from django.contrib.auth.models import User
from dateutil.relativedelta import relativedelta
import itertools
from model_bakery import baker
from model_bakery.utils import seq


salary_scales = ('C1', 'C2', 'C3', 'B2', 'D2', 'D3', 'E2')
positions = ('senior_teacher_1', 'senior_accountant', 'junior_developer')
departments = ('ministry_of_edu', 'ministry_of_fin', 'dit')

min_date = date.today() - relativedelta(years=18)

def load_employees():
    baker.make(
        'broadcast.employee',
        user=itertools.cycle(User.objects.exclude(username='amediphoko')),
        job_position=itertools.cycle(positions),
        ministry=itertools.cycle(departments),
        salary_scale=itertools.cycle(salary_scales),
        dob=seq(min_date, timedelta(days=30)),
        _quantity=2)

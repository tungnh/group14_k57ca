# pylint: disable=no-member, unexpected-keyword-arg, too-many-public-methods,
# pylint: too-few-public-methods, import-error, relative-import
"""Views implement here"""
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from timetables.models import Timetable
# Create your views here.

from models import Period
from forms import EditPeriodForm


def index(request):
    """Index page view, log in required"""
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/users/auth_login')

    periods_array = Period.objects.all()
    context = {'periods_array': periods_array}
    return render(request, 'periods/index.html', context)


def detail(request, pid="0"):
    """Course detail page view"""
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/users/auth_login')

    objs = []
    periods = Period.objects.filter(id=pid)
    if not periods.exists():
        return HttpResponse("Period not found!")

    for period in periods:
        objs.append(period)
    content = {
        'period_id': pid,
        'periods': objs,
    }
    return render(request, 'periods/detail/index.html', content)


def enroll(request, pid='0'):
    """Course enroll page view"""
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/users/auth_login')
    if request.method == 'GET':
        tb_array = Timetable.objects.filter(owner=request.user.id)
        if tb_array.exists():
            tid = tb_array[0].owner
        else:
            tid = 0
        periods = Period.objects.get(id=pid)
        periods_array = Period.objects.filter(timetable_id=tid)
        pos = periods.position
        leg = periods.length
        free = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
                17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44,
                45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58,
                59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73]
        for f in free:
            f = True
        for p in periods_array:
            free[p.position] = False
            j = p.position
            while j <= p.position + p.length-1:
                if (j > 0) and (j < 71):
                    free[j] = False
                j += 1
        j = pos
        while j <= pos+leg-1:
            if j > 70:
                return HttpResponseRedirect('/users/gateway/do=5')
            if not free[j]:
                return HttpResponseRedirect('/users/gateway/do=5')
            else:
                free[j] = False
            j += 1
        new_period = Period(code=periods.code,
                            name=periods.name,
                            period_type=periods.period_type,
                            lecturer=periods.lecturer,
                            position=periods.position,
                            length=periods.length,
                            timetable_id=tid)
        new_period.save()
        return HttpResponseRedirect('/')


def remove(request, pid="0"):
    """Course remove page view"""
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/users/auth_login')
    # Check permission
    period_object = Period.objects.get(id=pid)
    if not period_object.timetable.owner == request.user.id:
        return HttpResponseRedirect('/users/gateway/do=8')
    # Delete
    Period.objects.filter(id=pid).delete()
    return HttpResponseRedirect('/')


def edit(request, pid="0"):
    """Course edit page view"""
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/users/auth_login')

    period_object = Period.objects.get(id=pid)
    if not period_object.timetable.owner == request.user.id:
        return HttpResponseRedirect('/users/gateway/do=7')

    if request.method == 'POST':  # if the form has been submitted...
        form = EditPeriodForm(request.POST)  # A form bound to the POST data
        if form.is_valid() and form.check_conflict(pid):  # check validation
            Period.objects.filter(id=pid).update(code=form.cleaned_data['code'],
                                                 name=form.cleaned_data['name'],
                                                 period_type=form.cleaned_data['period_type'],
                                                 lecturer=form.cleaned_data['lecturer'],
                                                 position=(int(form.cleaned_data['day'])-1)*10+int(form.cleaned_data['start']),
                                                 length=form.cleaned_data['length'])
            return HttpResponseRedirect('/periods/id='+pid)  # Redirect
        else:
            return HttpResponseRedirect('/users/gateway/do=6')
    else:
        form = EditPeriodForm()
    period_obj = Period.objects.filter(id=pid)[0]
    return render(request, 'periods/edit/index.html', {
        'form': form,
        'period_obj': period_obj
        })


def add(request, pid="0"):
    """Course add page view"""
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/users/auth_login')

    if request.method == 'POST':  # if the form has been submitted...
        form = EditPeriodForm(request.POST)   # A form bound to the POST data
        if form.is_valid() and form.check_conflict(pid):  # Check validation
            new_period = Period(
                code=form.cleaned_data['code'],
                name=form.cleaned_data['name'],
                lecturer=form.cleaned_data['lecturer'],
                position=(int(form.cleaned_data['day'])-1)*10+int(form.cleaned_data['start']),
                length=form.cleaned_data['length'],
                timetable_id=pid)
            new_period.save()
            return HttpResponseRedirect('/')           # Redirect after POST
        else:
            return HttpResponseRedirect('/users/gateway/do=6')
    else:
        form = EditPeriodForm()

    return render(
        request,
        'periods/edit/index.html', {
            'form': form
        }
    )

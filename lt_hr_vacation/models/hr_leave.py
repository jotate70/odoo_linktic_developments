from odoo import fields, _, models, api
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from odoo.exceptions import ValidationError
from odoo.tools import float_compare
from datetime import datetime
from collections import namedtuple
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
from pytz import timezone, UTC
import pytz


DummyAttendance = namedtuple('DummyAttendance', 'hour_from, hour_to, dayofweek, day_period, week_type')


class HrLeave(models.Model):
    _inherit = "hr.leave"

    is_vacation = fields.Boolean(related='holiday_status_id.is_vacation', string="Is Vacation")

    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_number_of_days(self):
        for holiday in self:
            if holiday.request_date_from and holiday.request_date_to:
                holiday.number_of_days = relativedelta(holiday.request_date_to, holiday.request_date_from).days + 1
                if holiday.holiday_status_id.is_vacation:

                    holiday.number_of_days = 0
                    total_days = relativedelta(holiday.request_date_to, holiday.request_date_from).days + 1
                    for day in range(total_days):
                        date_init = holiday.request_date_from + timedelta(days=day)

                        all_days = ['0', '1', '2', '3', '4', '5', '6']
                        calendar_days = list(
                            set(holiday.employee_id.resource_calendar_id.attendance_ids.mapped('dayofweek')))
                        dominican_days = [int(day) for day in all_days if day not in calendar_days]

                        if date_init.weekday() not in dominican_days:
                            holiday.number_of_days += 1

                    global_leaves = len(holiday.env['resource.calendar.leaves'].search(
                        [('calendar_id', '=', False), ('date_from', '<=', holiday.date_to),
                         ('date_to', '>=', holiday.date_from)]))

                    holiday.number_of_days -= global_leaves

            else:
                holiday.number_of_days = 0

    @api.constrains('state', 'number_of_days', 'holiday_status_id')
    def _check_holidays(self):
        mapped_days = self.holiday_status_id.get_employees_days((self.employee_id | self.sudo().employee_ids).ids)
        for holiday in self:
            if holiday.holiday_type != 'employee' \
                    or not holiday.employee_id and not holiday.employee_ids \
                    or holiday.holiday_status_id.requires_allocation == 'no':
                continue
            if holiday.employee_id:
                leave_days = mapped_days[holiday.employee_id.id][holiday.holiday_status_id.id]
                if not holiday.env.context.get('re_compute') and (float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == -1 \
                                                                  or float_compare(
                            leave_days['virtual_remaining_leaves'], 0,
                            precision_digits=2) == -1):
                    raise ValidationError(
                        _('The number of remaining time off is not sufficient for this time off type.\n'
                          'Please also check the time off waiting for validation.'))
            else:
                unallocated_employees = []
                for employee in holiday.employee_ids:
                    leave_days = mapped_days[employee.id][holiday.holiday_status_id.id]
                    if float_compare(leave_days['remaining_leaves'],
                                     holiday.number_of_days, precision_digits=2) == -1 \
                            or float_compare(leave_days['virtual_remaining_leaves'],
                                             holiday.number_of_days,
                                             precision_digits=2) == -1:
                        unallocated_employees.append(employee.name)
                if unallocated_employees and not holiday.env.context.get('re_compute'):
                    raise ValidationError(
                        _('The number of remaining time off is not sufficient for this time off type.\n'
                          'Please also check the time off waiting for validation.')
                        + _('\nThe employees that lack allocation days are:\n%s',
                            (', '.join(unallocated_employees))))

    @api.depends('request_date_from_period', 'request_hour_from', 'request_hour_to', 'request_date_from', 'request_date_to',
                'request_unit_half', 'request_unit_hours', 'request_unit_custom', 'employee_id')
    def _compute_date_from_to(self):
        for holiday in self:
            if holiday.request_date_from and holiday.request_date_to and holiday.request_date_from > holiday.request_date_to:
                holiday.request_date_to = holiday.request_date_from
            if not holiday.request_date_from:
                holiday.date_from = False
            elif not holiday.request_unit_half and not holiday.request_unit_hours and not holiday.request_date_to:
                holiday.date_to = False
            else:
                if holiday.request_unit_half or holiday.request_unit_hours:
                    holiday.request_date_to = holiday.request_date_from
                resource_calendar_id = holiday.employee_id.resource_calendar_id or self.env.company.resource_calendar_id
                domain = [('calendar_id', '=', resource_calendar_id.id), ('display_type', '=', False)]
                attendances = self.env['resource.calendar.attendance'].read_group(domain, ['ids:array_agg(id)', 'hour_from:min(hour_from)', 'hour_to:max(hour_to)', 'week_type', 'dayofweek', 'day_period'], ['week_type', 'dayofweek', 'day_period'], lazy=False)

                # Must be sorted by dayofweek ASC and day_period DESC
                attendances = sorted([DummyAttendance(group['hour_from'], group['hour_to'], group['dayofweek'], group['day_period'], group['week_type']) for group in attendances], key=lambda att: (att.dayofweek, att.day_period != 'morning'))

                default_value = DummyAttendance(0, 0, 0, 'morning', False)

                if resource_calendar_id.two_weeks_calendar:
                    # find week type of start_date
                    start_week_type = self.env['resource.calendar.attendance'].get_week_type(holiday.request_date_from)
                    attendance_actual_week = [att for att in attendances if att.week_type is False or int(att.week_type) == start_week_type]
                    attendance_actual_next_week = [att for att in attendances if att.week_type is False or int(att.week_type) != start_week_type]
                    # First, add days of actual week coming after date_from
                    attendance_filtred = [att for att in attendance_actual_week if int(att.dayofweek) >= holiday.request_date_from.weekday()]
                    # Second, add days of the other type of week
                    attendance_filtred += list(attendance_actual_next_week)
                    # Third, add days of actual week (to consider days that we have remove first because they coming before date_from)
                    attendance_filtred += list(attendance_actual_week)
                    end_week_type = self.env['resource.calendar.attendance'].get_week_type(holiday.request_date_to)
                    attendance_actual_week = [att for att in attendances if att.week_type is False or int(att.week_type) == end_week_type]
                    attendance_actual_next_week = [att for att in attendances if att.week_type is False or int(att.week_type) != end_week_type]
                    attendance_filtred_reversed = list(reversed([att for att in attendance_actual_week if int(att.dayofweek) <= holiday.request_date_to.weekday()]))
                    attendance_filtred_reversed += list(reversed(attendance_actual_next_week))
                    attendance_filtred_reversed += list(reversed(attendance_actual_week))

                    # find first attendance coming after first_day
                    attendance_from = attendance_filtred[0]
                    # find last attendance coming before last_day
                    attendance_to = attendance_filtred_reversed[0]
                else:
                    # find first attendance coming after first_day
                    attendance_from = next((att for att in attendances if int(att.dayofweek) >= holiday.request_date_from.weekday()), attendances[0] if attendances else default_value)
                    # find last attendance coming before last_day
                    attendance_to = next((att for att in reversed(attendances) if int(att.dayofweek) <= holiday.request_date_to.weekday()), attendances[-1] if attendances else default_value)

                compensated_request_date_from = holiday.request_date_from
                compensated_request_date_to = holiday.request_date_to

                if holiday.request_unit_half:
                    if holiday.request_date_from_period == 'am':
                        hour_from = float_to_time(attendance_from.hour_from)
                        hour_to = float_to_time(attendance_from.hour_to)
                    else:
                        hour_from = float_to_time(attendance_to.hour_from)
                        hour_to = float_to_time(attendance_to.hour_to)
                elif holiday.request_unit_hours:
                    hour_from = float_to_time(float(holiday.request_hour_from))
                    hour_to = float_to_time(float(holiday.request_hour_to))
                elif holiday.request_unit_custom:
                    hour_from = holiday.date_from.time()
                    hour_to = holiday.date_to.time()
                    compensated_request_date_from = holiday._adjust_date_based_on_tz(holiday.request_date_from, hour_from)
                    compensated_request_date_to = holiday._adjust_date_based_on_tz(holiday.request_date_to, hour_to)
                else:
                    hour_from = float_to_time(attendance_from.hour_from)
                    hour_to = float_to_time(attendance_to.hour_to)

                holiday.date_from = timezone('UTC').localize(datetime.combine(compensated_request_date_from, hour_from)).astimezone(UTC).replace(tzinfo=None)
                holiday.date_to = timezone('UTC').localize(datetime.combine(compensated_request_date_to, hour_to)).astimezone(UTC).replace(tzinfo=None)

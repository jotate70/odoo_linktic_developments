from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _


def is_last_day_of_february(date_end: date) -> bool:
    last_february_day_in_given_year = date_end + relativedelta(month=3, day=1) + timedelta(days=-1)
    return date == last_february_day_in_given_year


def days360(
        date_a: date, date_b: date, preserve_excel_compatibility: bool = True
) -> int:
    """
    This method uses the the US/NASD Method (30US/360) to calculate the days between two
    dates.

    NOTE: to use the reference calculation method 'preserve_excel_compatibility' must be
    set to false.
    The default is to preserve compatibility. This means results are comparable to those
    obtained with Excel or Calc.
    This is a bug in Microsoft Office which is preserved for reasons of backward
    compatibility. Open Office Calc also choose to "implement" this bug to be MS-Excel
    compatible [1].

    [1] http://wiki.openoffice.org/wiki/Documentation/How_Tos/Calc:_Date_%26_Time_functions#Financial_date_systems
    """
    day_a = date_a.day
    day_b = date_b.day

    # Step 1 must be skipped to preserve Excel compatibility
    # (1) If both date A and B fall on the last day of February, then date B will be
    # changed to the 30th.
    if (
            not preserve_excel_compatibility
            and is_last_day_of_february(date_a)
            and is_last_day_of_february(date_b)
    ):
        day_b = 30

    # (2) If date A falls on the 31st of a month or last day of February, then date A
    # will be changed to the 30th.
    if day_a == 31 or is_last_day_of_february(date_a):
        day_a = 30

    # (3) If date A falls on the 30th of a month after applying (2) above and date B
    # falls on the 31st of a month, then date B will be changed to the 30th.
    if day_a == (30) and day_b == (31):
        day_b = 30

    days = (
            (date_b.year - date_a.year) * 360
            + (date_b.month - date_a.month) * 30
            + (day_b - day_a)
    )
    return days


def group_dates_by_week(dates):
    week_groups = {}
    for day in dates:
        week_number = day.isocalendar()[1]  # Get ISO week number
        if week_number not in week_groups:
            week_groups[week_number] = []
        week_groups[week_number].append(day)
    return len(week_groups)


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def get_vacation(self):
        vacation = self.env['hr.vacation'].search(
            [('employee_id', '=', self.employee_id.id), ('contract_id', '=', self.contract_id.id)])
        return vacation

    def get_days(self, date_a, date_b, not_sum_1=False):
        res = days360(date_a, date_b) + 1
        if not_sum_1:
            res -= 1
        return res

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        """
        @param contract: Browse record of contracts
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        res = []
        # fill only if the contract as a working schedule linked
        for contract in contracts.filtered(lambda contract: contract.resource_calendar_id):

            day_from = self.payroll_period_id.novelty_date_start
            day_to = self.payroll_period_id.novelty_date_end
            calendar = contract.resource_calendar_id

            leaves = {}
            other_leaves_employee = self.env['hr.leave'].search([
                ('employee_id', '=', contract.employee_id.id),
                ('state', '=', 'validate'),
                ('request_date_from', '<=', day_to),
                ('request_date_to', '>=', day_from),
                ('is_vacation', '=', False)
            ])
            vacation_employee = self.env['hr.leave'].search([
                ('employee_id', '=', contract.employee_id.id),
                ('state', '=', 'validate'),
                ('request_date_from', '<=', self.payroll_period_id.date_end),
                ('request_date_to', '>=', self.payroll_period_id.date_start),
                ('is_vacation', '=', True)
            ])
            leaves_employee = other_leaves_employee + vacation_employee

            list_dates = []
            for leave in leaves_employee:
                if leave.is_vacation:
                    date_start = self.payroll_period_id.date_start if self.payroll_period_id.date_start > leave.request_date_from < self.payroll_period_id.date_end else leave.request_date_from
                    date_end = self.payroll_period_id.date_end if leave.request_date_to > self.payroll_period_id.date_end else leave.request_date_to
                else:
                    date_start = day_from if day_from > leave.request_date_from < day_to else leave.request_date_from
                    date_end = day_to if leave.request_date_to > day_to else leave.request_date_to

                number_of_days = self._get_number_of_days(date_start, date_end, calendar,
                                                          leave.holiday_status_id.is_vacation)

                current_leave_struct = leaves.setdefault(leave.holiday_status_id, {
                    'name': leave.holiday_status_id.name or _('Global Leaves'),
                    'sequence': 5,
                    'code': leave.holiday_status_id.code or 'GLOBAL',
                    'number_of_days': 0.0,
                    'number_of_hours': 0.0,
                    'contract_id': contract.id,
                    'leave_id': leave.id,
                })
                current_leave_struct['number_of_days'] += number_of_days
                current_leave_struct['number_of_hours'] += number_of_days * calendar.hours_per_day

                # Total days to dominical
                if leave.holiday_status_id.dominican_discount:
                    leave_dates = [date_start + timedelta(days=day) for day in range((date_end - date_start).days + 1)]
                    list_dates += [day for day in leave_dates if day not in list_dates]

            # Rest days of all leaves
            leave_days = sum(item['number_of_days'] for item in leaves.values() if 'number_of_days' in item)
            leave_hours = sum(item['number_of_hours'] for item in leaves.values() if 'number_of_days' in item)

            if list_dates:
                days = group_dates_by_week(list_dates)
                leave_days += days
                dominical = {
                    'name': _("Discount Dominical Days"),
                    'sequence': 2,
                    'code': 'DIA_DESC_DOMINICAL',
                    'number_of_days': days,
                    'number_of_hours': days * contract.resource_calendar_id.hours_per_day,
                    'contract_id': contract.id,
                }
                res.append(dominical)

            worked_days = days360(date_from, date_to + relativedelta(days=1))
            worked_hours = contract.resource_calendar_id.hours_per_day * worked_days

            if contract.date_start > date_from:
                days = contract.date_start.day - 1
                leave_days += days
                income = {
                    'name': _("Days of income"),
                    'sequence': 2,
                    'code': 'DIA_DE_INGRESO',
                    'number_of_days': days,
                    'number_of_hours': days * contract.resource_calendar_id.hours_per_day,
                    'contract_id': contract.id,
                }
                res.append(income)

            if contract.date_end and contract.date_end != date_to and days360(contract.date_end, date_to) - 1 > 0:
                days = days360(contract.date_end, date_to) - 1
                leave_days += days
                retirement = {
                    'name': _("Days of retirement"),
                    'sequence': 3,
                    'code': 'DIA_DE_RETIRO',
                    'number_of_days': days,
                    'number_of_hours': days * contract.resource_calendar_id.hours_per_day,
                    'contract_id': contract.id,
                }
                res.append(retirement)

            attendances = {
                'name': _("Worked Days"),
                'sequence': 1,
                'code': 'WORK100',
                'number_of_days': worked_days - leave_days,
                'number_of_hours': worked_hours - leave_hours,
                'contract_id': contract.id,
            }

            res.append(attendances)
            res.extend(leaves.values())
        return res

    def _get_number_of_days(self, date_from, date_to, calendar, is_vacation=False):
        result = relativedelta(date_to, date_from).days + 1
        if is_vacation:

            result = 0
            total_days = relativedelta(date_to, date_from).days + 1
            for day in range(total_days):
                date_init = date_from + timedelta(days=day)

                all_days = ['0', '1', '2', '3', '4', '5', '6']
                calendar_days = list(set(calendar.attendance_ids.mapped('dayofweek')))
                dominican_days = [int(day) for day in all_days if day not in calendar_days]

                if date_init.weekday() not in dominican_days:
                    result += 1

            global_leaves = len(self.env['resource.calendar.leaves'].search(
                [('calendar_id', '=', False), ('date_from', '<=', date_to),
                 ('date_to', '>=', date_from)]))

            result -= global_leaves
        return result


class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    leave_id = fields.Many2one('hr.leave', string='Leave')

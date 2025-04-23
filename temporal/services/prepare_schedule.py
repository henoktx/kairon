from temporalio.client import ScheduleCalendarSpec, ScheduleRange

from executions.models import Execution
from workflows.models import Schedule


def prepare_schedule_input(execution: Execution) -> ScheduleCalendarSpec:
    schedule = Schedule.objects.get(workflow=execution.workflow)
    calendar_kwargs: dict[str, list[ScheduleRange]] = {}

    if schedule.minute is not None:
        calendar_kwargs["minute"] = [ScheduleRange(schedule.minute)]

    if schedule.hour is not None:
        calendar_kwargs["hour"] = [ScheduleRange(schedule.hour)]

    if schedule.day_of_month is not None:
        calendar_kwargs["day_of_month"] = [
            ScheduleRange(schedule.day_of_month, end=schedule.day_of_month)
        ]

    if schedule.day_of_week is not None:
        calendar_kwargs["day_of_week"] = [
            ScheduleRange(schedule.day_of_week, end=schedule.day_of_week)
        ]

    return ScheduleCalendarSpec(**calendar_kwargs)

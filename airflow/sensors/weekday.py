#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
import warnings
from typing import Iterable, Union

from airflow.exceptions import RemovedInAirflow3Warning
from airflow.sensors.base import BaseSensorOperator
from airflow.utils import timezone
from airflow.utils.context import Context
from airflow.utils.weekday import WeekDay


class DayOfWeekSensor(BaseSensorOperator):
    """
    Waits until the first specified day of the week. For example, if the execution
    day of the task is '2018-12-22' (Saturday) and you pass 'FRIDAY', the task will wait
    until next Friday.

    **Example** (with single day): ::

        weekend_check = DayOfWeekSensor(
            task_id='weekend_check',
            week_day='Saturday',
            use_task_logical_date=True,
            dag=dag)

    **Example** (with multiple day using set): ::

        weekend_check = DayOfWeekSensor(
            task_id='weekend_check',
            week_day={'Saturday', 'Sunday'},
            use_task_logical_date=True,
            dag=dag)

    **Example** (with :class:`~airflow.utils.weekday.WeekDay` enum): ::

        # import WeekDay Enum
        from airflow.utils.weekday import WeekDay

        weekend_check = DayOfWeekSensor(
            task_id='weekend_check',
            week_day={WeekDay.SATURDAY, WeekDay.SUNDAY},
            use_task_logical_date=True,
            dag=dag)

    :param week_day: Day of the week to check (full name). Optionally, a set
        of days can also be provided using a set.
        Example values:

            * ``"MONDAY"``,
            * ``{"Saturday", "Sunday"}``
            * ``{WeekDay.TUESDAY}``
            * ``{WeekDay.SATURDAY, WeekDay.SUNDAY}``

        To use ``WeekDay`` enum, import it from ``airflow.utils.weekday``

    :param use_task_logical_date: If ``True``, uses task's logical date to compare
        with week_day. Execution Date is Useful for backfilling.
        If ``False``, uses system's day of the week. Useful when you
        don't want to run anything on weekdays on the system.
    :param use_task_execution_day: deprecated parameter, same effect as `use_task_logical_date`
    """

    def __init__(
        self,
        *,
        week_day: Union[str, Iterable[str], WeekDay, Iterable[WeekDay]],
        use_task_logical_date: bool = False,
        use_task_execution_day: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.week_day = week_day
        self.use_task_logical_date = use_task_logical_date
        if use_task_execution_day:
            self.use_task_logical_date = use_task_execution_day
            warnings.warn(
                "Parameter ``use_task_execution_day`` is deprecated. Use ``use_task_logical_date``.",
                RemovedInAirflow3Warning,
                stacklevel=2,
            )
        self._week_day_num = WeekDay.validate_week_day(week_day)

    def poke(self, context: Context) -> bool:
        self.log.info(
            'Poking until weekday is in %s, Today is %s',
            self.week_day,
            WeekDay(timezone.utcnow().isoweekday()).name,
        )
        if self.use_task_logical_date:
            return context['logical_date'].isoweekday() in self._week_day_num
        else:
            return timezone.utcnow().isoweekday() in self._week_day_num

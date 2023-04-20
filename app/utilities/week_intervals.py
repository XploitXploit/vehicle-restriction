from datetime import date, datetime, time, timedelta
from enum import IntEnum
from functools import total_ordering, cache
import logging
import re
from typing import Iterable, NamedTuple, Optional, Union

# requires python 3.9!
from zoneinfo import ZoneInfo

from app.settings import settings


logger = logging.getLogger(__name__)


Weekday = IntEnum("Weekday", "L M W J V S D")
default_tz = ZoneInfo("America/Santiago")
utc_tz = ZoneInfo("UTC")


def _localize_dt(
    dt: Optional[datetime] = None,
    origin_tz: Union[str, ZoneInfo] = default_tz,
    target_tz: Union[str, ZoneInfo] = utc_tz,
) -> datetime:
    """Cast a datetime from one tz to another. If naive localizes first.
    dt can be naive or aware, if naive is localized first, else only casted to the
    target tz. if None is passed, None is returned.
    """
    if dt is None:
        return None
    if not isinstance(dt, datetime):
        raise TypeError("dt must be datetime")

    otz = ZoneInfo(origin_tz) if isinstance(origin_tz, str) else origin_tz
    ttz = ZoneInfo(target_tz) if isinstance(target_tz, str) else target_tz

    # if naive, localize using the origin_tz (otz object)
    localized_dt = dt.replace(tzinfo=otz) if dt.tzinfo is None else dt

    return localized_dt.astimezone(ttz)


class Limits(NamedTuple):
    """Represents the result of a query_limits call for DatetimeIntervalCollection. left
    and right represent the closest limits at either side of the datetime queried."""

    is_contained: bool
    left: Optional[datetime]
    right: Optional[datetime]


@total_ordering
class DatetimeInterval:
    """TODO"""

    def __init__(self, start, end):
        if not isinstance(start, datetime) or not isinstance(end, datetime):
            raise ValueError("start and end must be datetimes")
        if start > end:
            raise ValueError("start <= end must be true")
        self.start = start
        self.end = end

    def to_weektime_range(self):
        """TODO: refactor
        PENDING LOCALIZATION AND TEST
        now assumes that the datetimes are either in local time without
        timezone or in utc with time zone.
        """
        weekday = self.start.isocalendar()[2]
        t = self.start.time()
        td = self.end - self.start
        return WeektimeRange(weekday, t, td)

    def localize_(self, tz: Union[str, ZoneInfo]) -> None:
        """
        This is an inplace operation, if the datetimes are not naive then the
        operation is equivalent to awtimezone_
        """
        self.start = _localize_dt(self.start, tz, tz)
        self.end = _localize_dt(self.end, tz, tz)

    def astimezone_(self, tz: Union[str, ZoneInfo]) -> None:
        """
        if the datetimes are naive then UTC is assumed.
        :param tz: tzinfo object
        """
        self.start = _localize_dt(self.start, utc_tz, tz)
        self.end = _localize_dt(self.end, utc_tz, tz)

    # TODO: refactor
    def split(self, length):
        """
        Returns a list of Interval objects of at most 'length' length.
        The last Interval may be smaller.
        :param length: float, the length of the split parts.
        """
        if self.length() <= length:
            return [self]
        else:
            sep = timedelta(minutes=length)

            num_splits = int(self.length() // length) + 1
            p = [self.start + i * sep for i in range(num_splits)]
            p += [self.end]

            parts = [DatetimeInterval(p[i], p[i + 1]) for i in range(len(p) - 1)]
            return parts

    def length(self):
        """
        if type is datetime the length is in minutes.
        """
        return (self.end - self.start) / timedelta(minutes=1)

    def adjacent(self, interval):
        """
        Test whether two intervals are adjacent to each other. Overlapping
        implies not adjacent.
        :param interval: Interval, the other one
        """
        if isinstance(interval, type(self)):
            return self.start == interval.end or self.end == interval.start
        else:
            raise TypeError(
                "This operation is only supported between Interval" " objects."
            )

    # supposes that 'element' is of type self.interval_type
    def __contains__(self, x):
        if isinstance(x, type(self)):
            return self == self + x
        elif isinstance(x, datetime):
            return self.start <= x < self.end
        else:
            raise TypeError("This operation is only supported for this object type")

    def __repr__(self):
        return f"DatetimeInterval(start={repr(self.start)}, end={repr(self.end)})"

    def __str__(self):
        return f"DatetimeInterval('{self.start}', '{self.end}')"

    def __hash__(self):
        return hash(self.start, self.end)

    # overlaps
    def __and__(self, o):  # overrides &
        if isinstance(o, type(self)):
            return (
                o.start <= self.start < o.end
                or o.start < self.end < o.end
                or self.start <= o.start < self.end
                or self.start < o.end < self.end
            )
        elif isinstance(o, datetime):
            return o in self
        # TODO: refactor
        elif isinstance(o, DatetimeIntervalCollection):
            return o.__and__(self)
        else:
            # TODO: refactor
            raise TypeError(
                "& operation not supported between Interval " "and {}".format(type(o))
            )

    # union
    def __add__(self, o):  # overrides +
        """union"""
        if isinstance(o, type(self)):
            if self & o or self.adjacent(o):
                s = min(self.start, o.start)
                e = max(self.end, o.end)
                return type(self)(s, e)
            else:
                return None
        # TODO: refactor
        elif isinstance(o, DatetimeIntervalCollection):
            return o.__add__(self)
        else:
            raise TypeError("TODO: message")

    # intersection
    def __mul__(self, o):
        """
        Returns None if intervals dont overlap
        """
        if isinstance(o, type(self)):
            if self & o:
                s = max(self.start, o.start)
                e = min(self.end, o.end)
                dr = type(self)(s, e)
                return dr
            else:
                return None
        elif isinstance(o, DatetimeIntervalCollection):
            # TODO
            return o.__mul__(self)
        else:
            raise TypeError(
                "* operation not supported between Interval " "and {}".format(type(o))
            )

    def __lt__(self, o):
        if isinstance(o, type(self)):
            if self.start < o.start:
                return True
            elif self.start == o.start:
                if self.end < o.end:
                    return True
                else:
                    return False
            else:
                return False
        elif isinstance(o, datetime):
            raise TypeError("Use the method 'lt'")
        else:
            raise TypeError(
                f"This comparison is not implemented for type '{type(o).__name__}'."
            )

    def __eq__(self, o):
        if not isinstance(o, type(self)):
            return False
        return (self.start, self.end) == (o.start, o.end)

    def lt(self, o: datetime) -> bool:
        if not isinstance(o, datetime):
            raise TypeError(f"o must be a datetime, not '{type(o).__name__}'.")
        return self.end < o

    def gt(self, o: datetime) -> bool:
        if not isinstance(o, datetime):
            raise TypeError(f"o must be a datetime, not '{type(o).__name__}'.")
        return o < self.start

    def contains(self, o: datetime) -> bool:
        if not isinstance(o, datetime):
            raise TypeError(f"o must be a datetime, not '{type(o).__name__}'.")
        return self.start <= o <= self.end


class DatetimeIntervalCollection:
    """A datetime interval collection that implements useful comparisions with other
    intervals collections, intervals and single datetime objects."""

    def __init__(self, interval_list: Iterable[DatetimeInterval]):
        if not isinstance(interval_list, Iterable):
            raise TypeError("todo: message")

        for i in interval_list:
            if not isinstance(i, DatetimeInterval):
                raise TypeError("todo: message must be DatetimeInterval instance")

        self.interval_list = list(interval_list)

    def consolidate_(self):
        """Adds together intervals that are overlapping"""
        if len(self.interval_list) == 0:
            return
        self.interval_list.sort()

        curr = self.interval_list.pop(0)
        final_list = []

        for i in self.interval_list:
            if curr & i or curr.adjacent(i):
                curr += i
            else:
                final_list.append(curr)
                curr = i
        final_list.append(curr)

        self.interval_list = final_list

    def localize_(self, tz: str) -> None:
        """this is an inplace operation"""
        for i in self:
            i.localize_(tz)

    def astimezone_(self, tz):
        """
        Transforms timezone inplace. If no timezone then UTC is assumed.
        :param tz: tzinfo object
        """
        for i in self:
            i.astimezone_(tz)

    def query_limits(self, dt: datetime) -> Limits:
        """Returns if the datetime is contained and the closest interval borders at
        either 'side' of the datetime."""
        if dt in self:
            for i in self:
                if dt in i:
                    return Limits(is_contained=True, left=i.start, right=i.end)
            raise ValueError(
                "'dt in self' evaluates True but there is no interval that contains dt!"
            )
        else:
            lowers = [i.end for i in self if i.lt(dt)]
            uppers = [i.start for i in self if i.gt(dt)]
            return Limits(
                is_contained=False,
                left=max(lowers) if len(lowers) > 0 else None,
                right=min(uppers) if len(uppers) > 0 else None,
            )

    def __len__(self):
        return len(self.interval_list)

    def __iter__(self):
        return iter(self.interval_list)

    def __contains__(self, element):
        return any([element in r for r in iter(self)])

    def __repr__(self):
        return "DatetimeIntervalCollection({})".format(
            ", ".join([repr(i) for i in self.interval_list])
        )

    def __str__(self):
        return "DatetimeIntervalCollection({})".format(
            ", ".join([str(i) for i in self.interval_list])
        )

    def __getitem__(self, key):
        return self.interval_list[key]

    def __hash__(self):
        return hash(self.interval_list)

    def __and__(self, other) -> bool:
        """intersects"""
        if isinstance(other, type(self)):
            # remember type is iterable
            return any([x & y for x in self for y in other])
        else:
            # delegates to the elements method
            return any([x & other for x in iter(self)])

    def __add__(self, o):
        """union"""
        if isinstance(o, type(self)):
            return type(self)(self.interval_list + o.interval_list)
        elif isinstance(o, DatetimeInterval):
            return type(self)(self.interval_list + [o])
        else:
            raise TypeError(
                "Union (+ operator) is not supported between types"
                f"'{type(self).__name__}' and '{type(o).__name__}'"
            )

    def __mul__(self, other):
        """intersection"""
        return type(self)([x * y for x in self for y in other if x & y])


class WeektimeRange:
    """
    A convinient class that represents a day of the week and time for a general
    week. It allows the tranformation to a datetime given a year and isoweek
    number.
    """

    @classmethod
    def from_str(cls, range_definition):
        """
        format: 'Xhh:mm-Yu' meaning 'start X day at hh:mm for Y units of
        time separated by commas, spaces ignored
        X, days of the week [L,M,W,J,V,S,D], can insert multiple letters to
        expand
        A -> week days, expands to [L, M, W, J, V]
        B -> week ends, expands to [S,D]
        Y -> integer number
        u -> unit [d, h, m] -> day, hour, minute
        examples:
        'L07:00-2h' mondays from 7:00 to 9:00
        'L00:00-7d' whole week
        'B21:00-8h' expands to 'S21:00-8h,D21:00-8h'
        'AB21:00-h10' = 'LMWJVSD21:00-10h'
        """
        str_range = range_definition.replace(" ", "").upper()

        ranges = str_range.split(",")
        normalized = []
        for r in ranges:
            r = r.replace("A", "LMWJV")
            r = r.replace("B", "SD")
            # find the first digit, if no digit returns None
            m = re.search(r"\d", r)
            if m is None:
                continue

            days = r[: m.start()]
            time_range = r[m.start() :]

            tr_split = time_range.split("-")
            if len(tr_split) != 2:
                continue
            t, ran = tr_split
            t = time(*[int(x) for x in t.split(":")])
            if ran[-1] == "D":
                td = timedelta(days=int(ran[:-1]))
            elif ran[-1] == "H":
                td = timedelta(hours=int(ran[:-1]))
            elif ran[-1] == "M":
                td = timedelta(minutes=int(ran[:-1]))
            else:
                continue
            for d in days:
                normalized.append(cls(Weekday[d], t, td))
        return normalized

    @staticmethod
    def iso_to_gregorian(iso_year: int, iso_week: int, iso_day: int) -> date:
        """
        Gregorian calendar date for the given ISO year, week and day
        """

        def iso_year_start(iso_year: int) -> date:
            """
            The gregorian calendar date of the first day of the given ISO year
            """
            fourth_jan = date(iso_year, 1, 4)
            delta = timedelta(fourth_jan.isoweekday() - 1)
            return fourth_jan - delta

        year_start = iso_year_start(iso_year)
        return year_start + timedelta(days=iso_day - 1, weeks=iso_week - 1)

    def __init__(self, weekday: int, time: time, offset: timedelta):
        """
        :param weekday: int, [1,...,7] from Monday to Sunday
        :param time: datetime.time
        :offset: datetime.timedelta
        """
        self.weekday = weekday
        self.time = time
        self.offset = offset

    def __repr__(self):
        return type(self).__name__ + "(weekday={}, time={}, offset={})".format(
            self.weekday, self.time, self.offset
        )

    def __and__(self, o):
        # TODO: refactor this!
        s = self.specify(2020, 1)
        e = o.specify(2020, 1)
        return s & e

    def __sum__(self, o):
        if self & o:
            s = self.specify(2020, 1)
            e = o.specify(2020, 1)
            return (s + e).to_weektime_range()
        else:
            return None

    def __hash__(self):
        return hash((self.weekday, self.time, self.offset))

    def __eq__(self, o):
        return (self.weekday, self.time, self.offset) == (o.weekday, o.time, o.offset)

    def specify(self, isoyear: int, isoweek: int) -> DatetimeInterval:
        """
        Transforms the WeektimeRange into a naive datetime Interval based on
        year and week number.
        :param isoyear: int,
        :param isoweek: int
        """
        start = datetime.combine(
            WeektimeRange.iso_to_gregorian(isoyear, isoweek, int(self.weekday)),
            self.time,
        )

        end = start + self.offset
        return DatetimeInterval(start, end)


def parse_weektime_range(
    str_range: str,
    utc_start: Optional[datetime] = None,
    utc_end: Optional[datetime] = None,
    local_timezone: str = settings.TIME_ZONE,
) -> DatetimeIntervalCollection:
    """
    this methods return ranges of localized datetimes built from str_range
    considering utc_start and utc_end

    the format is:
    'Xhh:mm-Yu'

    :param str_range: str
    :param utc_start: datetime
    :param utc_end: datetime
    :param local_timezone: str
    """

    logger.debug(
        f"calling parse_weektime_range({str_range=}, {utc_start=}, {utc_end=}, "
        f"{local_timezone=})"
    )

    local_tz = ZoneInfo(local_timezone)

    local_start = _localize_dt(
        utc_start or datetime.utcnow() - timedelta(days=7), utc_tz, local_tz
    )
    local_end = _localize_dt(
        utc_end or datetime.utcnow() + timedelta(days=7), utc_tz, local_tz
    )

    ranges = WeektimeRange.from_str(str_range)

    # generate iso calendar dates from the start date until the end date,
    # inclusive plus one day margin
    day = timedelta(days=1)
    s_date, e_date = local_start.date() - day, local_end.date() + day
    isocalendar_weeks = [s_date.isocalendar()[0:2]]
    offset = 1
    while True:
        actual = s_date + timedelta(days=offset)
        if actual <= e_date:
            isocalendar_weeks.append(actual.isocalendar()[0:2])
            offset += 1
        else:
            break

    # keep only unique weeks
    isocalendar_weeks = list(set(isocalendar_weeks))
    ranges = list(set(ranges))

    datetime_ranges = [
        x.specify(*y) for x in ranges for y in isocalendar_weeks  # a list of Interval
    ]
    collection = DatetimeIntervalCollection(datetime_ranges)
    collection.consolidate_()
    collection.localize_(local_tz)
    collection.astimezone_(utc_tz)

    logger.debug("parse_weektime_range ended, response: %s", collection)

    return collection


@cache
def quick_match(
    str_range: str, dt: Optional[datetime] = None, tz: str = "America/Sao_Paulo"
) -> Limits:
    """Returns a Limits object, with the form (bool, dt, dt) indicating if the datetime
    is inside the range definition, and where are the closest borders."""
    dt = _localize_dt(dt or datetime.utcnow(), utc_tz, tz)
    margin = timedelta(days=7)
    intervals = parse_weektime_range(str_range, dt - margin, dt + margin, tz)
    return intervals.query_limits(dt)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import os
import json
import logging

import requests

import numpy as np
import pandas as pd


class HolidayAPI(object):
    """
    An api helper to obtain holiday date data.
    """

    URL = 'https://holidayapi.com/v1/holidays'

    def __init__(self, api_key=os.environ.get('API_KEY')):
        """
        Initializes the holiday api object.
        """
        if api_key is None:
            raise Exception('You must supply a holiday API key (https://holidayapi.com/)')

        self.api_key = api_key

    def _get_holidays(self, year, country):
        """
        Calls the https://holidayapi.com/ api to get holidays.

        Country must be in ISO 3166-2 format (e.g. US) and year must be
        in YYYY format (e.g. 2017).
        """
        payload = {
            'key': self.api_key,
            'country': country,
            'year': year,
        }

        response = requests.get(url=self.URL, params=payload)
        data = json.loads(response.text)
        if 'error' in data.keys():
            raise Exception('{error}: {message}'.format(
                error=data['status'],
                message=data['error']
            ))

        elif response.status_code != requests.codes.ok:
            response.raise_for_status()

        return data['holidays']

    def get_holidays(self, year, country):
        """
        Obtain holiday data.
        """
        return self._get_holidays(year, country)


class Calendar(object):

    WEEKDAY_MAP = {
        1: 'Monday',
        2: 'Tuesday',
        3: 'Wednesday',
        4: 'Thursday',
        5: 'Friday',
        6: 'Saturday',
        7: 'Sunday',
    }

    CALENDAR_KEYS = [
        'date',
        'year',
        'month',
        'day',
        'weekday',
        'weekday_name',
        'weeknumber',
        'is_weekend',
        'is_business_day',
        'is_holiday',
        'holiday_name',
    ]

    def __init__(self, start_date_string, end_date_string,
        include_holidays=False, holiday_api_key=os.environ.get('API_KEY'),
        country='US', format='%Y-%m-%d'):
        """
        Initialize with a start and end date string with a default format
        of %Y-%m-%d (YYYY-MM-DD). This can be changed with the
        format argument.

        include_holidays is a boolean if you want to include holidays in the calendar.
        If you do you need a https://holidayapi.com/ API key. If you are using the
        free service you cannot obtain future holidays.

        country is the country for which you want to generate a calendar (defaults
        to US)
        """
        self.start_date = datetime.datetime.strptime(start_date_string, format)
        self.end_date = datetime.datetime.strptime(end_date_string, format)
        self.num_days = (self.end_date - self.start_date).days
        self.include_holidays = include_holidays
        self.CALENDAR_DATA = self._gen_calendar_data_template()

        if include_holidays is True:
            self.holiday_api_key = holiday_api_key
            self.country = country

    def _gen_calendar_data_template(self):
        """
        Generates a calendar data template with empty lists assigned to each
        key in `self.CALENDAR_KEYS`
        """
        return { k:[] for k in self.CALENDAR_KEYS }

    def _gen_dates(self):
        for day_num in range(self.num_days):
            yield self.start_date + datetime.timedelta(days=day_num)

    def _get_holidays_from_api(self):
        # Get years needed
        years = [year for year in range(self.start_date.year, self.end_date.year + 1)]
        holidays = []

        # Call the api for each year
        for year in years:
            if year >= datetime.datetime.today().year:
                logging.warning('NOTE: You must have a paid account with https://holidayapi.com/' \
                    ' to get future holiday data. If you are using a free ' \
                    'api key, you will receive an error or may encounter missing data.')
            holidays.append(HolidayAPI(self.holiday_api_key).get_holidays(year, self.country))

        self.holidays = {}
        for holiday_data_dict in holidays: # loop through each dict (holidays for each year)
            for holiday_date, holiday_data in holiday_data_dict.items():
                if len(holiday_data) > 1: # More than 1 holiday on the same day
                    # Only include first listed public holiday
                    public_holidays = []
                    for day in holiday_data:
                        if day['public'] is True: # Public holiday
                            public_holidays.append(day)

                    if len(public_holidays) > 0: # if there are any public holidays
                        first_public_holiday = public_holidays[0]
                        # List the holiday under its observed date
                        observed_date = first_public_holiday['observed']
                        self.holidays[observed_date] = first_public_holiday['name']

                # Handle records with 1 holiday per day
                holiday_data = holiday_data[0]
                if holiday_data['public'] is True: # Only include public_holidays
                    observed_date = holiday_data['observed']
                    self.holidays[observed_date] = holiday_data['name']

    def _is_weekend(self, weekday_index):
        """
        If it's a weekend, return True.
        """
        return True if weekday_index in (6, 7) else False

    def _is_holiday(self, datetime_object):
        """
        takes a datetime date object and returns True if it is a public
        holiday on the date.
        """
        date_key = datetime.datetime.strftime(datetime_object, '%Y-%m-%d')
        holiday = self.holidays.get(date_key)
        if holiday is None:
            return (False, np.nan)
        return (True, holiday)

    def _is_business_day(self, weekday_index, datetime_object):
        """
        Returns True for M-F providing they're not holidays.
        """
        if self.include_holidays is True:
            return not self._is_weekend(weekday_index) and not self._is_holiday(datetime_object)[0]
        return not self._is_weekend(weekday_index)

    def generate(self, dest=None, sep=',', reset=False):
        """
        Generates the calendar. If reset is True it will reset the cal.

        If destination is provided it will save the calendar. You can use
        the sep argument to define the delimiter.
        """
        if reset:
            self.CALENDAR_DATA = self._gen_calendar_data_template()

        if self.include_holidays:
            self._get_holidays_from_api()

        for date in self._gen_dates():
            year, weeknumber, weekday = date.isocalendar()
            self.CALENDAR_DATA['date'].append('%s' % date.date())
            self.CALENDAR_DATA['year'].append(year)
            self.CALENDAR_DATA['month'].append(date.month)
            self.CALENDAR_DATA['day'].append(date.day)
            self.CALENDAR_DATA['weekday'].append(weekday)
            self.CALENDAR_DATA['weekday_name'].append(self.WEEKDAY_MAP[weekday])
            self.CALENDAR_DATA['weeknumber'].append(weeknumber)
            self.CALENDAR_DATA['is_weekend'].append(self._is_weekend(weekday))

            # Handle holidays
            if self.include_holidays:
                is_holiday, holiday_name = self._is_holiday(date)
            else:
                is_holiday = np.nan
                holiday_name = np.nan
            self.CALENDAR_DATA['is_holiday'].append(is_holiday)
            self.CALENDAR_DATA['holiday_name'].append(holiday_name)
            self.CALENDAR_DATA['is_business_day'].append(self._is_business_day(weekday, date))

        calendar = pd.DataFrame(self.CALENDAR_DATA)[self.CALENDAR_KEYS]

        if dest is None:
            return calendar

        return calendar.to_csv(dest, sep=sep, index=False)

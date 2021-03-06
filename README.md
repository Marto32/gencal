# Gen Cal
Generates a calendar for a customized period of time.

It also has the option to include holidays for multiple countries once you
create a [Holiday API](https://holidayapi.com/) api key. You can create a
free key for historical generation or, with a paid key, you can obtain holiday
data for future dates (I do not have any affiliation with Holiday API).

Your API key can be set as an environment variable assigned to `API_KEY` or
as an argument when initializing the `Calendar` object.

The calendar can be used within python as a pandas DataFrame or you can specify a destination path to download the dataset.

Contributions welcome!

## Directions

I haven't had the chance to upload this to pypi yet, so for now, just clone the repo and follow the directions in the **Example Usage** section below.

GenCal requires the following libraries:

 * [Requests](http://docs.python-requests.org/en/master/)
 * [Pandas](https://pandas.pydata.org/)
 * [NumPy](http://www.numpy.org/)

It is recommended to create a new virtual environment to house all of these dependencies. If you need help creating a virtual environment, you can follow [this guide](http://docs.python-guide.org/en/latest/dev/virtualenvs/). To install the above packages, run the following in terminal:

```
pip install -r requirements.txt
```

To make things easier, you can also use [Pipenv](https://pipenv.readthedocs.io/en/latest/). Once installed, navigate to the repo and run the following:

```
pipenv install
```

To get started, run the following in your terminal (if you don't have pipenv just use `python` on the last line):

```
git clone https://github.com/Marto32/gencal.git
export PATH=$PATH:$(pwd)/gencal
cd gencal
pipenv run python
```

Once in the python shell you can use the library as shown below.

## Example Usage

```python
from generate_calendar import Calendar

start_date = '2013-01-01'
end_date = '2016-01-01'
api_key = 'YOUR_HOLIDAY_API_KEY_HERE'

calendar = Calendar(start_date, end_date, include_holidays=True, holiday_api_key=api_key, country='US')

data_frame = calendar.generate()
data_frame.head()
```

Output:

date|year|month|day|weekday|weekday_name|weeknumber|is_weekend|is\_business\_day|is_holiday|holiday_name
|---|---|---|---|---|---|---|---|---|---|---|
2013-01-01|2013|1|1|2|Tuesday|1|False|False|True|New Year's Day
2013-01-02|2013|1|2|3|Wednesday|1|False|True|False|NaN
2013-01-03|2013|1|3|4|Thursday|1|False|True|False|NaN
2013-01-04|2013|1|4|5|Friday|1|True|False|False|NaN
2013-01-05|2013|1|5|6|Saturday|1|True|False|False|NaN

Another option would have been to write directly to disk:

```python
calendar = Calendar(start_date, end_date, include_holidays=True, holiday_api_key=api_key, country='US')

calendar.generate(dest='~/calendar_data.csv', sep=',')
```

## Field Descriptions

**Field**|**Description**
|---|---|
date|The date in YYYY-MM-DD format
year|The year part of the date in YYYY format
month|The month part of the date in M format
day|The day part of the date in D format
weekday|The iso weekday index of the date (1 - 7)
weekday_name|The name of the weekday
weeknumber|The number of the week in the year
is_weekend|Boolean, whether or not the date falls on Sat or Sun.
is_business_day|Boolean, if the date is not on a weekend or public holiday, it's True
is_holiday|Boolean, denoting whether or not the date falls on a public holiday (if api keys are provided)
holiday_name|Holiday name (if api keys are provided)

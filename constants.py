import re
import datetime
import telebot
from my_calendar import CallbackData

# token = '1088624168:AAHUE2hz9l5NaPwOSIbctrLmxs1HcgTgSB4'
token = ''
GMT = '+03:00'
# time_intervals = ['10:00-10:30', '10:00-11:00', '10:30-11:00', '10:30-11:30', '11:00-11:30', '11:00-12:00',
#                   '11:30-12:00', '11:30-12:30', '12:00-12:30', '12:00-13:00', '12:30-13:00', '12:30-13:30',
#                   '13:00-13:30', '13:00-14:00', '13:30-14:00', '13:30-14:30', '14:00-14:30', '14:00-15:00',
#                   '14:30-15:00', '14:30-15:30', '15:00-15:30', '15:00-16:00', '15:30-16:00', '15:30-16:30',
#                   '16:00-16:30', '16:00-17:00', '16:30-17:00', '16:30-17:30', '17:00-17:30', '17:00-18:00',
#                   '17:30-18:00', '17:30-18:30', '18:00-18:30', '18:00-19:00', '18:30-19:00', '18:30-19:30',
#                   '19:00-19:30', '19:00-20:00', '19:30-20:00']

calendar_show = CallbackData("calendar_show", "action", "year", "month", "day")
calendar_delete = CallbackData("calendar_delete", "action", "year", "month", "day")
calendar_add = CallbackData("calendar_add", "action", "year", "month", "day")

addPattern = re.compile('(/)(((\d{1,2})/(\d{1,2})) )?(\d{1,2})(:(\d{2}))?(-(\d{1,2})(:(\d{2}))?)? (['
                        '-/_,.@()\w\u0400-\u04FF\s]+)')
outputPattern = re.compile('\d{4}-\d{2}-\d{2}T(\d{2}:\d{2}):\d{2}\+\d{2}:\d{2}\d{4}-\d{2}-\d{2}T(\d{2}:\d{2}):\d{'
                           '2}\+\d{2}:\d{2}([-/_,.@()\w\u0400-\u04FF\s]+)')
datePattern = re.compile('(\d{4})-(\d{2})-(\d{2})T(\d{2}:\d{2}):\d{2}\+03:00')
inline_time_pattern = re.compile('(\d{2}:\d{2})-(\d{2}:\d{2})')
event_name_pattern = re.compile('(/)([-_,.@\w\u0400-\u04FF\s]+)')
getEventPatternTime = re.compile('(\d{4})-(\d{2})-(\d{2})T(\d{2}:\d{2}):\d{2}\+\d{2}:\d{2}')
addEventTimePattern = re.compile('(\d{4})-(\d{2})-(\d{2})T(\d{2}:\d{2}):\d{2}')

now = datetime.datetime.now()
todayStartTime = datetime.datetime.combine(datetime.datetime.today(), datetime.datetime.min.time()).isoformat() + GMT
todayEndTime = datetime.datetime.combine(datetime.datetime.today() + datetime.timedelta(days=1),
                                         datetime.datetime.min.time()).isoformat() + GMT
tomorrowStartTime = datetime.datetime.combine(datetime.datetime.today() + datetime.timedelta(days=1),
                                              datetime.datetime.min.time()).isoformat() + GMT
tomorrowEndTime = datetime.datetime.combine(datetime.datetime.today() + datetime.timedelta(days=2),
                                            datetime.datetime.min.time()).isoformat() + GMT

default_markup = telebot.types.ReplyKeyboardMarkup(True, False)
default_markup.row('Today', 'Tomorrow', 'Date')
default_markup.row('Delete', 'Help')

inline_default_markup = telebot.types.InlineKeyboardMarkup(row_width=3)
today_button = telebot.types.InlineKeyboardButton("Today", callback_data='today')
tomorrow_button = telebot.types.InlineKeyboardButton("Tomorrow", callback_data='tomorrow')
help_button = telebot.types.InlineKeyboardButton("Help", callback_data='help')
date_button = telebot.types.InlineKeyboardButton("Date", callback_data='date')
delete_button = telebot.types.InlineKeyboardButton("Delete", callback_data='delete')
inline_default_markup.add(today_button, tomorrow_button, date_button, delete_button, help_button)

cancel_button = telebot.types.InlineKeyboardButton("Cancel", callback_data='cancel')


# time_markup = telebot.types.InlineKeyboardMarkup(row_width=3)
# time_markup.add(*[telebot.types.InlineKeyboardButton(time_span, callback_data=time_span)
#                   for time_span in time_intervals])
# time_markup.add(cancel_button)


def time_constructor(value):
    is_today = False
    value = addPattern.search(value)
    if value:
        if value.group(3):
            date = str(now.year) + "-" + str(value.group(5)) + "-" + str(value.group(4))
        else:
            date = str(now.date())
            is_today = True
        hour_start = str(value.group(6))
        if value.group(8):
            min_start = str(value.group(8))
        else:
            min_start = "00"
        if value.group(10):
            hour_end = str(value.group(10))
        else:
            hour_end = str(int(value.group(6)) + 1)
        if value.group(12):
            min_end = str(value.group(12))
        else:
            min_end = min_start
        time_start = hour_start + '::' + min_start + '::00'
        time_end = hour_end + '::' + min_end + '::00'
        name = str(value.group(13))

        date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        time_start = datetime.datetime.strptime(time_start, '%H::%M::%S').time()
        time_start = datetime.datetime.combine(date, time_start).isoformat()
        time_end = datetime.datetime.strptime(time_end, '%H::%M::%S').time()
        time_end = datetime.datetime.combine(date, time_end).isoformat()

        return time_start, time_end, name, is_today
    else:
        return False, False, False, is_today


def inline_time_constructor(value, date):
    value = inline_time_pattern.search(value)
    if value:
        time_start = value.group(1)
        time_end = value.group(2)
        time_start = datetime.datetime.strptime(time_start, '%H:%M').time()
        time_end = datetime.datetime.strptime(time_end, '%H:%M').time()
        time_start = datetime.datetime.combine(date, time_start).isoformat()
        time_end = datetime.datetime.combine(date, time_end).isoformat()
        return time_start, time_end
    else:
        return False, False, False


if __name__ == '__main__':
    print("It's just supporting module, run main.py")

import telebot
import constants
import answers
import getEvents
import my_calendar
from telebot.types import CallbackQuery
import datetime
import re
import time

bot = telebot.TeleBot(constants.token)

print(bot.get_me())


def log(message, answer):
    print("\n---------------------------")
    from datetime import datetime
    print(datetime.now())
    print("Message from {0} {1} (id = {2})\nText - {3}".format(message.from_user.first_name,
                                                               message.from_user.last_name,
                                                               str(message.from_user.id), message.text))
    print(answer)


def show_events(date):
    start_time = datetime.datetime.combine(date, datetime.datetime.min.time()).isoformat() + constants.GMT
    end_time = datetime.datetime.combine(date + datetime.timedelta(days=1),
                                         datetime.datetime.min.time()).isoformat() + constants.GMT
    answer, event_id = getEvents.show_events(start_time, end_time)
    return answer, event_id


def add_event(message, username, first_name, last_name):
    time_start, time_end, name, is_today = constants.time_constructor(str(message))
    if time_start:
        checker, event_id = getEvents.show_events(time_start + constants.GMT, time_end + constants.GMT)
        if checker[1] == "No events found":
            answer = getEvents.add_events(time_start + '%s', time_end + '%s', name)
            event_start_time = re.search(constants.addEventTimePattern, time_start)
            event_end_time = re.search(constants.addEventTimePattern, time_end)
            bot.send_message(chat_id=message.chat.id,
                             text="<b>{4}-{5}-{6}</b>\n{0} {7}-{8} by @{1} ({2} {3})".format(
                                 answer, username, first_name, last_name, event_start_time.group(3),
                                 event_start_time.group(2), event_start_time.group(1), event_start_time.group(4),
                                 event_end_time.group(4)),
                             reply_markup=constants.default_markup, parse_mode='html')
            if is_today:
                answer, event_id = getEvents.show_events(constants.todayStartTime, constants.todayEndTime)
                pin = bot.send_message(message.chat.id, "\n".join(answer), parse_mode='html',
                                 reply_markup=constants.default_markup)
                if message.chat.type == "group" or message.chat.type == "supergroup":
                    bot.pin_chat_message(message.chat.id, pin.message_id)
        else:
            bot.send_message(chat_id=message.chat.id, text=answers.occupied,
                             reply_markup=constants.inline_default_markup)
    else:
        bot.send_message(chat_id=message.chat.id, text=answers.invalid, reply_markup=constants.inline_default_markup)


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, answers.welcome, reply_markup=constants.default_markup)
    log(message, "Started bot")


@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, answers.add, reply_markup=constants.default_markup)


@bot.message_handler(commands=['today'])
def handle_today(message):
    answer, event_id = getEvents.show_events(constants.todayStartTime, constants.todayEndTime)
    bot.send_message(message.chat.id, "\n".join(answer), parse_mode='html',
                     reply_markup=constants.inline_default_markup)


@bot.message_handler(commands=['tomorrow'])
def handle_help(message):
    answer, event_id = getEvents.show_events(constants.tomorrowStartTime, constants.tomorrowEndTime)
    bot.send_message(chat_id=message.chat.id, text="\n".join(answer), parse_mode='html',
                     reply_markup=constants.inline_default_markup)


@bot.message_handler(commands=['date'])
def handle_help(message):
    bot.send_message(chat_id=message.chat.id, text="Select date:", reply_markup=my_calendar.create_calendar(
        name=constants.calendar_show.prefix, year=constants.now.year, month=constants.now.month))


@bot.message_handler(commands=['delete'])
def handle_delete(message):
    bot.send_message(chat_id=message.chat.id, text="Select date of the event to be deleted:",
                     reply_markup=my_calendar.create_calendar(
                         name=constants.calendar_delete.prefix, year=constants.now.year,
                         month=constants.now.month))


@bot.message_handler(content_types=['text'])
def handle_text(message):
    if re.match(constants.addPattern, message.text):
        add_event(message, message.from_user.username, message.from_user.first_name, message.from_user.last_name)
    elif message.text == "Today":
        answer, event_id = getEvents.show_events(constants.todayStartTime, constants.todayEndTime)
        bot.send_message(message.chat.id, "\n".join(answer), parse_mode='html',
                         reply_markup=constants.inline_default_markup)
    elif message.text == "Tomorrow":
        answer, event_id = getEvents.show_events(constants.tomorrowStartTime, constants.tomorrowEndTime)
        bot.send_message(message.chat.id, "\n".join(answer), parse_mode='html',
                         reply_markup=constants.inline_default_markup)
    elif message.text == "Date":
        bot.send_message(message.chat.id, "Select date:",
                         reply_markup=my_calendar.create_calendar(
                             name=constants.calendar_show.prefix, year=constants.now.year, month=constants.now.month))
    elif message.text == "Help":
        bot.send_message(chat_id=message.chat.id, text=answers.add, reply_markup=constants.inline_default_markup)
    elif message.text == "Delete":
        bot.send_message(chat_id=message.chat.id, text="Select date of the event to be deleted:",
                         reply_markup=my_calendar.create_calendar(
                             name=constants.calendar_delete.prefix, year=constants.now.year,
                             month=constants.now.month))
    # else:
    #     bot.send_message(message.chat.id, answers.invalid, reply_markup=constants.inline_default_markup)


@bot.callback_query_handler(func=lambda call: call.data == 'today')
def callback_inline(call: CallbackQuery):
    answer, event_id = getEvents.show_events(constants.todayStartTime, constants.todayEndTime)
    bot.edit_message_text(chat_id=call.message.chat.id, text="\n".join(answer), message_id=call.message.message_id,
                          parse_mode='html', reply_markup=constants.inline_default_markup)


@bot.callback_query_handler(func=lambda call: call.data == 'tomorrow')
def callback_inline(call: CallbackQuery):
    answer, event_id = getEvents.show_events(constants.tomorrowStartTime, constants.tomorrowEndTime)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="\n".join(answer),
                          parse_mode='html', reply_markup=constants.inline_default_markup)


@bot.callback_query_handler(func=lambda call: call.data == 'date')
def callback_inline(call: CallbackQuery):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Select date:",
                          reply_markup=my_calendar.create_calendar(
                              name=constants.calendar_show.prefix, year=constants.now.year, month=constants.now.month))


@bot.callback_query_handler(func=lambda call: call.data == 'help')
def callback_inline(call: CallbackQuery):
    bot.edit_message_text(chat_id=call.message.chat.id, text=answers.add, reply_markup=constants.inline_default_markup,
                          message_id=call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data == 'delete')
def callback_inline(call: CallbackQuery):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="Select date of the event to be deleted:",
                          reply_markup=my_calendar.create_calendar(
                              name=constants.calendar_delete.prefix, year=constants.now.year,
                              month=constants.now.month))


@bot.callback_query_handler(func=lambda call_calendar: call_calendar.data.startswith(constants.calendar_show.prefix))
def callback_inline(call_calendar: CallbackQuery):
    name, action, year, month, day = call_calendar.data.split(constants.calendar_show.sep)
    date = my_calendar.calendar_query_handler(bot=bot, call=call_calendar, name=name, action=action,
                                              year=year, month=month, day=day)

    if action == "DAY":
        answer, event_id = show_events(date)
        bot.edit_message_text(chat_id=call_calendar.message.chat.id, text="\n".join(answer), parse_mode='html',
                              message_id=call_calendar.message.message_id, reply_markup=constants.inline_default_markup)
    elif action == "CANCEL":
        bot.edit_message_text(chat_id=call_calendar.message.chat.id, text="Select option:",
                              message_id=call_calendar.message.message_id,
                              reply_markup=constants.inline_default_markup)


@bot.callback_query_handler(func=lambda call_delete_calendar: call_delete_calendar.data.startswith(
    constants.calendar_delete.prefix))
def callback_inline(call_delete_calendar: CallbackQuery):
    name, action, year, month, day = call_delete_calendar.data.split(constants.calendar_delete.sep)
    date = my_calendar.calendar_query_handler(bot=bot, call=call_delete_calendar, name=name, action=action,
                                              year=year, month=month, day=day)

    if action == "DAY":
        answer, event_id = show_events(date)
        if answer[1] == "No events found":
            bot.edit_message_text(chat_id=call_delete_calendar.message.chat.id, text="\n".join(answer),
                                  message_id=call_delete_calendar.message.message_id,
                                  reply_markup=constants.inline_default_markup,
                                  parse_mode='html')
        else:
            delete_markup = telebot.types.InlineKeyboardMarkup(row_width=2)
            for event, button_id in zip(answer, event_id):
                if event == answer[0]:
                    continue
                button = telebot.types.InlineKeyboardButton(event, callback_data="d - {0}".format(button_id))
                delete_markup.add(button)
            delete_markup.add(constants.cancel_button)
            bot.edit_message_text(chat_id=call_delete_calendar.message.chat.id, text="Select event to delete:",
                                  message_id=call_delete_calendar.message.message_id, reply_markup=delete_markup)

            @bot.callback_query_handler(func=lambda call_delete_event: call_delete_event.data.startswith("d - "))
            def callback_inline2(call_delete_event: CallbackQuery):
                response = call_delete_event.data
                response = response.replace("d - ", "")
                delete_event_name = '!Error!'
                # for get_event, get_button_id in zip(answer, event_id):
                #     if response == get_button_id:
                #         delete_event_name = get_event
                #         break
                event_start, event_end, event_name = getEvents.get_event(response)
                event_start = re.search(constants.getEventPatternTime, event_start)
                event_end = re.search(constants.getEventPatternTime, event_end)
                getEvents.delete_events(response)
                is_today = "{2}-{1}-{0}".format(event_start.group(3), event_start.group(2), event_start.group(1))
                is_today = is_today == str(constants.now.date())
                bot.edit_message_text(chat_id=call_delete_event.message.chat.id,
                                      message_id=call_delete_event.message.message_id,
                                      text="<b>{0}-{1}-{2}</b>\nEvent {3} {4}-{5} was successfully deleted by "
                                           "@{6} ({7} {8})"
                                      .format(event_start.group(3), event_start.group(2), event_start.group(1),
                                              event_name, event_start.group(4), event_end.group(4),
                                              call_delete_event.from_user.username,
                                              call_delete_event.from_user.first_name,
                                              call_delete_event.from_user.last_name),
                                      reply_markup=None, parse_mode='html')
                if is_today:
                    new_answer, new_event_id = getEvents.show_events(constants.todayStartTime, constants.todayEndTime)
                    pin = bot.send_message(call_delete_event.message.chat.id, "\n".join(new_answer), parse_mode='html',
                                     reply_markup=constants.default_markup)
                    if call_delete_event.message.chat.type == "group" or call_delete_event.message.chat.type == "supergroup":
                        bot.pin_chat_message(call_delete_event.message.chat.id, pin.message_id)

            @bot.callback_query_handler(func=lambda call_cancel: call_cancel.data == 'cancel')
            def callback_inline2(call_cancel: CallbackQuery):
                bot.edit_message_text(chat_id=call_cancel.message.chat.id, message_id=call_cancel.message.message_id,
                                      text="Select option:", reply_markup=constants.inline_default_markup)
    elif action == "CANCEL":
        bot.edit_message_text(chat_id=call_delete_calendar.message.chat.id, text="Select option:",
                              message_id=call_delete_calendar.message.message_id,
                              reply_markup=constants.inline_default_markup)


# @bot.callback_query_handler(func=lambda call: call.data == 'add')
# def callback_inline(call: CallbackQuery):
#     bot.send_message(chat_id=call.message.chat.id, text="Select date of the event:",
#                      reply_markup=my_calendar.create_calendar(
#                               name=constants.calendar_add.prefix, year=constants.now.year, month=constants.now.month))


# @bot.callback_query_handler(func=lambda call: call.data.startswith(constants.calendar_add.prefix))
# def callback_inline(call: CallbackQuery):
#     name, action, year, month, day = call.data.split(constants.calendar_delete.sep)
#     date = my_calendar.calendar_query_handler(bot=bot, call=call, name=name, action=action,
#                                                    year=year, month=month, day=day)
#     if action == "DAY":
#         bot.send_message(chat_id=call.message.chat.id, text="Select time:", reply_markup=constants.time_markup)
#
#         @bot.callback_query_handler(func=lambda time: re.match(constants.inline_time_pattern, time.data))
#         def callback_time(time: CallbackQuery):
#             bot.edit_message_text(chat_id=time.message.chat.id, message_id=time.message.message_id,
#                                   text="Send me name of the event", reply_markup=None)
#
#             # @bot.message_handler(content_types=['text'])
#             # def handle_add(message):
#             #     if re.match(constants.event_name_pattern, message.text):
#             #         answer = inline_add_event(date, time.data, message.text)
#             #         bot.send_message(chat_id=message.chat.id,
#             #                          text=answer, reply_markup=constants.inline_default_markup)
#             #     else:
#             #         bot.send_message(chat_id=time.message.chat.id,
#             #                          text="It's too difficult", reply_markup=constants.inline_default_markup)
#
#         @bot.callback_query_handler(func=lambda call2: call2.data == 'cancel')
#         def callback_inline2(call2: CallbackQuery):
#             bot.edit_message_text(chat_id=call2.message.chat.id, message_id=call2.message.message_id,
#                                   text="Select option:", reply_markup=constants.inline_default_markup)
#
#     elif action == "CANCEL":
#         bot.send_message(chat_id=call.message.chat.id, text="Select option:",
#                          reply_markup=constants.inline_default_markup)


# def inline_add_event(date, time_interval, name):
#     time_start, time_end = constants.inline_time_constructor(time_interval, date)
#     if time_start:
#         checker, event_id = getEvents.show_events(time_start + constants.GMT, time_end + constants.GMT)
#         if checker[1] == "No events found":
#             answer = getEvents.add_events(time_start + '%s', time_end + '%s', name)
#             return answer
#         else:
#             return answers.occupied
#     else:
#         return answers.invalid
#

while True:
    try:
        bot.polling(none_stop=True, interval=0, timeout=15)
        bot.infinity_polling(True)
    except Exception:
        time.sleep(15)
        pass

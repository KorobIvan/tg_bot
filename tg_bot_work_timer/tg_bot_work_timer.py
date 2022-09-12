from asyncio.windows_events import NULL
from time import time
import telebot
import bot_key
import datetime
from telebot import types
import sqlite3

conn = sqlite3.connect('C:\\Users\\vanv2\\Desktop\\PROG\\tg_bot\\tg_bot_work_timer\\bd\\study_time_manager.db', check_same_thread=False)
cursor = conn.cursor()
def db_table_val(user_id: int, start_study: datetime, pause_study: datetime, continue_study: datetime, finish_study: datetime):
	cursor.execute('INSERT INTO stydy_time (user_id, start_study, pause_study, continue_study, finish_study) VALUES (?,?,?,?,?)', (user_id, start_study, pause_study, continue_study, finish_study))
	conn.commit()
def db_table_update_fin(finish_study: datetime, study_time: str, study_id = int):
	cursor.execute('UPDATE stydy_time SET finish_study = ?, study_time = ? WHERE study_id = ?;', (finish_study, study_time, study_id))
	conn.commit()
	return
def db_table_update_pause(pause_study: datetime, study_id = int):
	cursor.execute('UPDATE stydy_time SET pause_study = ? WHERE study_id = ?;', (pause_study, study_id))
	conn.commit()
	return
def db_table_update_cont(continue_study: datetime,sum_pause: int, study_id = int):
	cursor.execute('UPDATE stydy_time SET continue_study = ?, sum_pause = ? WHERE study_id = ?;', (continue_study,sum_pause, study_id))
	conn.commit()
	return
def db_table_query(us_id):
    cursor.execute(f'SELECT * from stydy_time WHERE user_id = {us_id};')
    result = cursor.fetchall()
    return result

bot = telebot.TeleBot(bot_key.work_timer)
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "/start":
        keyboard = types.InlineKeyboardMarkup()
        key_start = types.InlineKeyboardButton(text='start', callback_data='study')
        keyboard.add(key_start)
        bot.send_message(message.from_user.id, text='Начните заниматься', reply_markup=keyboard)
    elif message.text == "/help":
        bot.send_message(message.chat.id, f'Команда /start начнет отсчет времни, которое ты занимался.\nКоманда /finish выведет сколько времни ты посвятил занятиям!\n/my_stydy_time')     
    elif message.text == "/my_stydy_time":
        bot.send_message(message.chat.id, f'Ты занимался часов.')
    else:
        bot.send_message(message.chat.id, "Привет, данный бот поможети тебе подсчитать, то время, которое ты посвятишь занятиям, для отображения команд жми /help")

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "study":
        us_id = call.message.from_user.id
        st_time = datetime.datetime.now()
        db_table_val(user_id=us_id, start_study=st_time, pause_study=NULL, continue_study=NULL, finish_study=NULL)

        keyboard = types.InlineKeyboardMarkup()
        key_pause = types.InlineKeyboardButton(text='pause', callback_data='pause')
        keyboard.add(key_pause)
        key_finish = types.InlineKeyboardButton(text='finish', callback_data='finish')
        keyboard.add(key_finish)
        bot.send_message(call.message.chat.id, f'Отлично, ты нача заниматьс в {st_time.strftime("%H:%M:%S")}\nВремя пошло!', reply_markup=keyboard)
    elif call.data == "pause": 
        us_id = call.message.from_user.id
        pa_time = datetime.datetime.now()
        db_table_update_pause(pause_study=pa_time, study_id=db_table_query(us_id)[-1][0])

        keyboard = types.InlineKeyboardMarkup()
        key_continue = types.InlineKeyboardButton(text='continue', callback_data='continue')
        keyboard.add(key_continue)
        key_finish = types.InlineKeyboardButton(text='finish', callback_data='finish')
        keyboard.add(key_finish) 
        bot.send_message(call.message.chat.id, f'Отлично, время приостановленно, как решишь вернуться нажми продолжить', reply_markup=keyboard)
    elif call.data == "continue": 
        us_id = call.message.from_user.id
        cont_time = datetime.datetime.now()
        pa_time = datetime.datetime(year=int(db_table_query(us_id)[-1][3][0:4]),month=int(db_table_query(us_id)[-1][3][5:7]),day=int(db_table_query(us_id)[-1][3][8:10]),hour=int(db_table_query(us_id)[-1][2][11:13]),minute=int(db_table_query(us_id)[-1][3][14:16]),second=int(db_table_query(us_id)[-1][3][17:19]),microsecond=int(db_table_query(us_id)[-1][3][20:]))
        delta = str(cont_time - pa_time)
        db_table_update_cont(continue_study=cont_time,sum_pause=delta[0:7], study_id=db_table_query(us_id)[-1][0])
        
        keyboard = types.InlineKeyboardMarkup()
        key_pause = types.InlineKeyboardButton(text='pause', callback_data='pause')
        keyboard.add(key_pause)
        key_finish = types.InlineKeyboardButton(text='finish', callback_data='finish')
        keyboard.add(key_finish) 
        bot.send_message(call.message.chat.id, f'Отлично, ты решил вернуться к занятию!', reply_markup=keyboard)
    elif call.data == "finish":
        us_id = call.message.from_user.id
        fin_time = datetime.datetime.now()
        st_time_res = datetime.datetime(year=int(db_table_query(us_id)[-1][2][0:4]),month=int(db_table_query(us_id)[-1][2][5:7]),day=int(db_table_query(us_id)[-1][2][8:10]),hour=int(db_table_query(us_id)[-1][2][11:13]),minute=int(db_table_query(us_id)[-1][2][14:16]),second=int(db_table_query(us_id)[-1][2][17:19]),microsecond=int(db_table_query(us_id)[-1][2][20:]))
        delta = str(fin_time - st_time_res)
        if db_table_query(us_id)[-1][3] != 0 and db_table_query(us_id)[-1][5] != 0:
            #dt.datetime.strptime(start, '%H:%M:%S')
            sum_pause_time = datetime.datetime.strptime(db_table_query(us_id)[-1][5], '%H:%M:%S')
            delta = datetime.datetime.strptime(delta[0:7],'%H:%M:%S')
            db_table_update_fin(finish_study=fin_time, study_time=str(delta-sum_pause_time), study_id=db_table_query(us_id)[-1][0])

            bot.send_message(call.message.chat.id, f'Ты закончил заниматьс в {fin_time.strftime("%H:%M:%S")}\nПродолжительность занятия {str(delta-sum_pause_time)}') 
        elif db_table_query(us_id)[-1][3] != 0:
            pass
        else:
            db_table_update_fin(finish_study=fin_time, study_time=delta[0:7], study_id=db_table_query(us_id)[-1][0])   

            bot.send_message(call.message.chat.id, f'Ты закончил заниматьс в {fin_time.strftime("%H:%M:%S")}\nПродолжительность занятия {delta[0:7]}')

bot.polling(none_stop=True, interval=0)
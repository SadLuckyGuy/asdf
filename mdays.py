import vk_api
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
import random
import json
import sqlite3

global db
global sql

db = sqlite3.connect('mdays.db')
sql = db.cursor()

sql.execute("""CREATE TABLE IF NOT EXISTS users(
	id INT,
	message INT
)""")

vk_session = vk_api.VkApi(token = tok)
longpoll = VkBotLongPoll(vk_session, 201700447)

def sender(id, text):
	vk_session.method('messages.send', {'user_id' : id, 'message' : text, 'random_id' : random.randint(-1234567, +1234567)})

def get_but(text, color):
	return {
							"action": {
									"type": "text",
									"payload": "{\"button\": \"" + "1" + "\"}",
									"label": f"{text}"
							},
							"color": f"{color}"
					}

def key_sender(id, text, key):
	vk_session.method('messages.send', {'user_id' : id, 'message' : text, 'keyboard' : key, 'random_id' : random.randint(-1234567, +1234567)})

menu_key = {
	"one_time" : True,
	"inline" : False,
	"buttons" : [
			[get_but('Меню', 'positive')],
			[get_but('FAQ', 'positive')],
	]
}

menu_key = json.dumps(menu_key, ensure_ascii = False).encode('utf-8')
menu_key = str(menu_key.decode('utf-8'))

for event in longpoll.listen():
	if event.type == VkBotEventType.MESSAGE_NEW:

		msg = event.object.message['text'].lower()

		if event.from_chat:
			id = event.object.message['from_id']
			chat_id = event.chat_id

			sql.execute(f"SELECT id FROM users WHERE id = '{id}'")
			if sql.fetchone() is None:
				sql.execute(f"INSERT INTO users VALUES(?, ?)", (id, 0))
				db.commit()
#ls
		else:
			id = event.object.message['from_id']

			sql.execute(f"SELECT id FROM users WHERE id = '{id}'")
			if sql.fetchone() is None:
				sql.execute(f"INSERT INTO users VALUES(?, ?)", (id, 0))
				db.commit()

			mess = sql.execute("SELECT message FROM users WHERE id = ?", (id, )).fetchone()

			if mess[0] == 0:
				key_sender(id, 'Доступные команды: ' + '\n📕Меню' +'\n❓FAQ', menu_key)
				sql.execute(f"UPDATE users SET message = {1} WHERE id = '{id}'")
				db.commit()

			if msg == 'обнулить':
				sql.execute(f"UPDATE users SET message = {0} WHERE id = '{id}'")
				db.commit()

			if msg == 'меню':
				if mess[0] == 0:
					pass
				else:
					key_sender(id, 'Доступные команды: ' + '\n📕Меню' +'\n❓FAQ', menu_key)

			if 'ник' in msg:
				nick = msg.split('ник')[1]
				sender(id, nick)

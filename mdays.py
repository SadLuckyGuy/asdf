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
	vopros TEXT,
	admin INT,
	message INT,
	stata INT,
	otvet INT,
	ans INT,
	black INT
)""")
db.commit()

vk_session = vk_api.VkApi(token = '3990cb63ed91a2d612e6f61d6d28d1635dd8ec2a58623ba005d721e0394d688658bb8e9b9d3a1b1331d48')
longpoll = VkBotLongPoll(vk_session, 205306551)

def sender(id, text):
	vk_session.method('messages.send', {'user_id' : id, 'message' : text, 'random_id' : random.randint(-1234567, +1234567)})

def chat_sender(id, text):
	vk_session.method('messages.send', {'chat_id' : id, 'message' : text, 'random_id' : random.randint(-1234567, +1234567)})

def forward(id, text, fo):
	vk_session.method('messages.send', {'chat_id' : id, 'message' : text, 'forward' : fo, 'random_id' : random.randint(-1234567, +1234567)})

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

def prof(user_id):
	data = vk_session.method('users.get', {'user_id' : user_id, 'name_case' : 'Nom', 'fields' : ["domain", "online"]})[0]
	otvet = sql.execute("SELECT otvet FROM users WHERE id = ?", (user_id, )).fetchone()
	admin = sql.execute("SELECT admin FROM users WHERE id = ?", (user_id, )).fetchone()
	if admin[0] == 0:
		dolg = 'игрок'
		chat_sender(chat_id, '👤Имя: ' + data['first_name'] + '\n👥Фамилия: ' + data['last_name'] + '\n💬Ответы: ' + str(otvet[0]) + '\n🌐ID: ' + str(user_id) + '\n💼Должность: ' + dolg)
	if admin[0] == 1:
		dolg = 'модератор'
		chat_sender(chat_id, '👤Имя: ' + data['first_name'] + '\n👥Фамилия: ' + data['last_name'] + '\n💬Ответы: ' + str(otvet[0]) + '\n🌐ID: ' + str(user_id) + '\n💼Должность: ' + dolg)
	if admin[0] == 2:
		dolg = 'тестер'
		chat_sender(chat_id, '👤Имя: ' + data['first_name'] + '\n👥Фамилия: ' + data['last_name'] + '\n💬Ответы: ' + str(otvet[0]) + '\n🌐ID: ' + str(user_id) + '\n💼Должность: ' + dolg)
	if admin[0] == 3:
		dolg = 'администратор'
		chat_sender(chat_id, '👤Имя: ' + data['first_name'] + '\n👥Фамилия: ' + data['last_name'] + '\n💬Ответы: ' + str(otvet[0]) + '\n🌐ID: ' + str(user_id) + '\n💼Должность: ' + dolg)

def conver(chat_id, peer_id):
	data = vk_session.method('messages.getConversationMembers', {'peer_id' : peer_id, 'profiles' : ['first_name', 'last_name']})
	print(data['profiles'][1])

def reply(peer, cmi):
	ward = {"peer_id" : peer, "conversation_message_ids" : cmi}
	return ward

menu_key = {
	"one_time" : True,
	"inline" : False,
	"buttons" : [
			[get_but('Меню', 'positive')],
	]
}

menu_key = json.dumps(menu_key, ensure_ascii = False).encode('utf-8')
menu_key = str(menu_key.decode('utf-8'))

for event in longpoll.listen():
	if event.type == VkBotEventType.MESSAGE_NEW:

		msg = event.object.message['text'].lower()
		text = event.object.message['text']
		peer_id = event.object.message['peer_id']
#beseda
		if event.from_chat:
			id = event.object.message['from_id']
			chat_id = event.chat_id
			msg_id = event.message["conversation_message_id"]
			peer_id = event.object.message['peer_id']
			#reg
			sql.execute(f"SELECT id FROM users WHERE id = '{id}'")
			if sql.fetchone() is None:
				sql.execute(f"INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (id, 0, 0, 0, 0, 0, 0, 0))
				db.commit()

			if '!выключить' in msg:
				data = sql.execute("SELECT admin FROM users WHERE id = ?", (id, )).fetchone()
				if data[0] == 3 or data[0] == 2:
					chat_sender(chat_id, '✅Бот выключен')
					break
				else:
					chat_sender(chat_id, '🚫У Вас недостаточно прав')

			if msg == '!бот':
				chat_sender(chat_id, '✅БИП БУП')

			if '+чс' in msg:
				text_trr = msg.split(' ')
				text_arr = msg.split('+чс')[1]
				data = sql.execute("SELECT admin FROM users WHERE id = ?", (id, )).fetchone()
				if '+чс' == text_trr[0].lower():
					if text_arr == '':
						chat_sender(chat_id, '🚫Вы не указали ID нарушителя')
					elif data[0] == 0:
						chat_sender(chat_id, '🚫У Вас недостаточно прав')
					else:
						ask = msg.split()[1]
						sql.execute(f"SELECT id FROM users WHERE id = '{ask}'")
						if sql.fetchone() is None:
							sql.execute(f"INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (ask, 0, 0, 0, 0, 0, 0, 0))
							db.commit()
						else:
							sql.execute("UPDATE users SET black = ? WHERE id = ?", (1, ask))
							db.commit()
							chat_sender(chat_id, '✅Игрок был добавлен в черный список')
							sender(ask, '😞Вы были добавлены в черный список')

			if '-чс' in msg:
				text_trr = msg.split(' ')
				text_arr = msg.split('-чс')[1]
				data = sql.execute("SELECT admin FROM users WHERE id = ?", (id, )).fetchone()
				if '-чс' == text_trr[0].lower():
					if text_arr == '':
						chat_sender(chat_id, '🚫Вы не указали ID нарушителя')
					elif data[0] == 0:
						chat_sender(chat_id, '🚫У Вас недостаточно прав')
					else:
						ask = msg.split()[1]
						sql.execute(f"SELECT id FROM users WHERE id = '{ask}'")
						if sql.fetchone() is None:
							sql.execute(f"INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (ask, 0, 0, 0, 0, 0, 0, 0))
							db.commit()
						else:
							sql.execute("UPDATE users SET black = ? WHERE id = ?", (0, ask))
							db.commit()
							chat_sender(chat_id, '✅Игрок был убран из черного списка')
							sender(ask, '⭐Вы были убраны из черного списка')


			if '!профиль' in msg:
				text_trr = msg.split(' ')
				text_arr = msg.split('!профиль')[1]
				if '!профиль' == text_trr[0].lower():
					if text_arr == '':
						prof(id)
					else:
						user_id_text = text_trr[1]
						user_id = user_id_text[user_id_text.find('d')+1:user_id_text.find('|')]
						print(user_id)
						sql.execute(f"SELECT id FROM users WHERE id = '{user_id}'")
						if sql.fetchone() is None:
							sql.execute(f"INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (user_id, 0, 0, 0, 0, 0, 0, 0))
							db.commit()
							prof(user_id)
						else:
							prof(user_id)

			if '/ask' in msg:
				data = sql.execute("SELECT admin FROM users WHERE id = ?", (id, )).fetchone()
				if data[0] == 0:
					chat_sender(chat_id, '🚫У Вас нет прав на использование данной команды')
				if data[0] == 1:
					ask = msg.split()[1] #id польз
					bag = sql.execute("SELECT vopros FROM users WHERE id = ?", (ask, )).fetchone()
					allowed = vk_session.method('messages.isMessagesFromGroupAllowed', {'group_id' : 205306551, 'user_id' : ask})
					if allowed['is_allowed'] == 0:
						chat_sender(chat_id, '🚫Игрок запретил сообщения')
					elif bag[0] == str(0):
						chat_sender(chat_id, '🚫Игрок не задавал вопрос')
					else:
						ret = text.split('/ask')[1]
						mes = ret.split(ask)[1]
						msg_id = event.message['conversation_message_id']
						peer_id = event.object.message['peer_id']
						reply_ward = json.dumps(reply(peer_id, msg_id))
						sender(ask, '💬Вам ответил модератор: ' + ' ' + mes)
						forward(chat_id, '✅Ответ дошел до игрока', reply_ward)
						otv = sql.execute("SELECT otvet FROM users WHERE id = ?", (id, )).fetchone()
						sql.execute("UPDATE users SET otvet = ? WHERE id = ?", (1 + int(otv[0]), id))
				if data[0] == 2:
					ask = msg.split()[1] #id
					bag = sql.execute("SELECT vopros FROM users WHERE id = ?", (ask, )).fetchone()
					allowed = vk_session.method('messages.isMessagesFromGroupAllowed', {'group_id' : 205306551, 'user_id' : ask})
					if allowed['is_allowed'] == 0:
						chat_sender(chat_id, '🚫Игрок запретил сообщения')
					elif bag[0] == str(0):
						chat_sender(chat_id, '🚫Игрок не задавал вопрос')
					else:
						ret = text.split('/ask')[1]
						mes = ret.split(ask)[1]
						msg_id = event.message['conversation_message_id']
						peer_id = event.object.message['peer_id']
						reply_ward = json.dumps(reply(peer_id, msg_id))
						sender(ask, '💬Вам ответил тестер: ' + ' ' + mes)
						forward(chat_id, '✅Ответ дошел до игрока', reply_ward)
						otv = sql.execute("SELECT otvet FROM users WHERE id = ?", (id, )).fetchone()
						sql.execute("UPDATE users SET otvet = ? WHERE id = ?", (1 + int(otv[0]), id))
						db.commit()
				if data[0] == 3:
					ask = msg.split()[1] #id
					bag = sql.execute("SELECT vopros FROM users WHERE id = ?", (ask, )).fetchone()
					allowed = vk_session.method('messages.isMessagesFromGroupAllowed', {'group_id' : 205306551, 'user_id' : ask})
					if allowed['is_allowed'] == 0:
						chat_sender(chat_id, '🚫Игрок запретил сообщения')
					elif bag[0] == str(0):
						chat_sender(chat_id, '🚫Игрок не задавал вопрос')
					else:
						ret = text.split('/ask')[1]
						mes = ret.split(ask)[1]
						msg_id = event.message['conversation_message_id']
						peer_id = event.object.message['peer_id']
						reply_ward = json.dumps(reply(peer_id, msg_id))
						sender(ask, '💬Вам ответил администратор: ' + ' ' + mes)
						forward(chat_id, '✅Ответ дошел до игрока', reply_ward)
						otv = sql.execute("SELECT otvet FROM users WHERE id = ?", (id, )).fetchone()
						sql.execute("UPDATE users SET otvet = ? WHERE id = ?", (1 + int(otv[0]), id))
						db.commit()

			if '!модер' in msg:
				admin = sql.execute("SELECT admin FROM users WHERE id = ?", (id, )).fetchone()
				if admin[0] == 3 or admin[0] == 2:
					text_trr = msg.split(' ')
					text_arr = msg.split('!модер')[1]
					if ('reply_message' in event.object.message):
						user_id = event.object.message['reply_message']['from_id']
						sql.execute("UPDATE users SET admin = ? WHERE id = ?", (1, user_id))
						db.commit()
						chat_sender(chat_id, '✅Вы успешно выдали должность')
					elif text_arr == '':
						chat_sender(chat_id, '🚫Вы не передали id пользователя')
					else:
						user_id_text = text_trr[1]
						user_id = user_id_text[user_id_text.find('d')+1:user_id_text.find('|')]
						sql.execute("UPDATE users SET admin = ? WHERE id = ?", (1, user_id))
						db.commit()
						chat_sender(chat_id, '✅Вы успешно выдали должность')
				else:
					chat_sender(chat_id, '🚫У Вас недостаточно прав')

			if '!тестер' in msg:
				admin = sql.execute("SELECT admin FROM users WHERE id = ?", (id, )).fetchone()
				if admin[0] == 3 or admin[0] == 2:
					text_trr = msg.split(' ')
					text_arr = msg.split('!тестер')[1]
					if ('reply_message' in event.object.message):
						user_id = event.object.message['reply_message']['from_id']
						sql.execute("UPDATE users SET admin = ? WHERE id = ?", (1, user_id))
						db.commit()
						chat_sender(chat_id, '✅Вы успешно выдали должность')
					elif text_arr == '':
						chat_sender(chat_id, '🚫Вы не передали id пользователя')
					else:
						user_id_text = text_trr[1]
						user_id = user_id_text[user_id_text.find('d')+1:user_id_text.find('|')]
						sql.execute("UPDATE users SET admin = ? WHERE id = ?", (2, user_id))
						db.commit()
						chat_sender(chat_id, '✅Вы успешно выдали должность')
				else:
					chat_sender(chat_id, '🚫У Вас недостаточно прав')

			if '!админ' in msg:
				admin = sql.execute("SELECT admin FROM users WHERE id = ?", (id, )).fetchone()
				if admin[0] == 3 or admin[0] == 2:
					text_trr = msg.split(' ')
					text_arr = msg.split('!админ')[1]
					if ('reply_message' in event.object.message):
						user_id = event.object.message['reply_message']['from_id']
						sql.execute("UPDATE users SET admin = ? WHERE id = ?", (1, user_id))
						db.commit()
						chat_sender(chat_id, '✅Вы успешно выдали должность')
					elif text_arr == '':
						chat_sender(chat_id, '🚫Вы не передали id пользователя')
					else:
						user_id_text = text_trr[1]
						user_id = user_id_text[user_id_text.find('d')+1:user_id_text.find('|')]
						sql.execute("UPDATE users SET admin = ? WHERE id = ?", (3, user_id))
						db.commit()
						chat_sender(chat_id, '✅Вы успешно выдали должность')
				else:
					chat_sender(chat_id, '🚫У Вас недостаточно прав')

			if '!игрок' in msg:
				admin = sql.execute("SELECT admin FROM users WHERE id = ?", (id, )).fetchone()
				if admin[0] == 3 or admin[0] == 2:
					text_trr = msg.split(' ')
					text_arr = msg.split('!игрок')[1]
					if ('reply_message' in event.object.message):
						user_id = event.object.message['reply_message']['from_id']
						sql.execute("UPDATE users SET admin = ? WHERE id = ?", (1, user_id))
						db.commit()
						chat_sender(chat_id, '✅Вы успешно выдали должность')
					elif text_arr == '':
						chat_sender(chat_id, '🚫Вы не передали id пользователя')
					else:
						user_id_text = text_trr[1]
						user_id = user_id_text[user_id_text.find('d')+1:user_id_text.find('|')]
						sql.execute("UPDATE users SET admin = ? WHERE id = ?", (0, user_id))
						db.commit()
						chat_sender(chat_id, '✅Вы успешно выдали должность')
				else:
					chat_sender(chat_id, '🚫У Вас недостаточно прав')

			if '!должность' in msg:
				text_trr = msg.split(' ')
				text_arr = msg.split('!должность')[1]
				if text_arr == '':
					data = sql.execute("SELECT admin FROM users WHERE id = ?", (id, )).fetchone()
					if data[0] == 1:
						chat_sender(chat_id, '⚠Ваша должность: модератор')
					if data[0] == 0:
						chat_sender(chat_id, '👶Ваша должность: игрок')
					if data[0] == 2:
						chat_sender(chat_id, '🔧Ваша должность: тестер')
					if data[0] == 3:
						chat_sender(chat_id, '⭐Ваша должность: администратор')
				else:
					user_id_text = text_trr[1]
					user_id = user_id_text[user_id_text.find('d')+1:user_id_text.find('|')]
					obs = sql.execute("SELECT admin FROM users WHERE id = ?", (user_id, )).fetchone()
					sql.execute(f"SELECT id FROM users WHERE id = '{user_id}'")
					if sql.fetchone() is None:
						sql.execute(f"INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (user_id, 0, 0, 0, 0, 0, 0, 0))
						db.commit()
					if obs[0] == 1:
						chat_sender(chat_id, '⚠Должность участника: модератор')
					if obs[0] == 0:
						chat_sender(chat_id, '👶Должность участника: игрок')
					if obs[0] == 2:
						chat_sender(chat_id, '🔧Должность участника: тестер')
					if obs[0] == 3:
						chat_sender(chat_id, '⭐Должность участника: администратор')
#ls
		else:
			id = event.object.message['from_id']
			#reg
			sql.execute(f"SELECT id FROM users WHERE id = '{id}'")
			if sql.fetchone() is None:
				sql.execute(f"INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (id, 0, 0, 0, 0, 0, 0, 0))
				db.commit()

			mess = sql.execute("SELECT message FROM users WHERE id = ?", (id, )).fetchone()

			if mess[0] == 0:
				key_sender(id, 'Доступные команды: ' + '\n📕Меню' +'\n❓Задать вопрос (пример использования: задать вопрос *вопрос*)', menu_key)
				sql.execute(f"UPDATE users SET message = {1} WHERE id = '{id}'")
				db.commit()

			if msg == 'меню':
				black = sql.execute("SELECT black FROM users WHERE id = ?", (id, )).fetchone()
				if black[0] == 1:
					sender(id, '😞Вы находитесь в черном списке и не можете использовать команды')
				else:
					if mess[0] == 0:
						pass
					else:
						key_sender(id, 'Доступные команды: ' + '\n📕Меню' +'\n❓Задать вопрос (пример использования: задать вопрос *вопрос*)', menu_key)

			if 'задать вопрос' in msg:
				black = sql.execute("SELECT black FROM users WHERE id = ?", (id, )).fetchone()
				if black[0] == 1:
					sender(id, '😞Вы находитесь в черном списке и не можете использовать команды')
				else:
					vop = msg.split('задать вопрос')[1]
					if vop == '':
						sender(id, '❗Вы не указали вопрос')
					else:
						sql.execute("UPDATE users SET vopros = ? WHERE id = ?", (vop, id))
						db.commit()
						sql.execute("UPDATE users SET ans = ? WHERE id = ?", (1, id))
						db.commit()
						data = vk_session.method('users.get', {"user_id" : id, "name_case" : "Nom", "fields" : ["sex, bdate, city, country, status, followers_count, online"]})[0]
						ask = sql.execute("SELECT vopros FROM users WHERE id = ?", (id, )).fetchone()
						msg_id = event.message['conversation_message_id']
						reply_ward = json.dumps(reply(peer_id, msg_id))
						forward(2, '❓' + data['first_name'] + ' ' + data['last_name'] + ' задал вопрос' + '\n❗Используйте команду /ask [id] (ответ), чтобы ответить пользователю' + '\n' + '\n🧠Вопрос: ' + '"' + ask[0] + '"' + '\n🌐ID: ' + str(id), reply_ward)
						sender(id, '✅Вы задали вопрос, ожидайте, когда администрация ответит на него')
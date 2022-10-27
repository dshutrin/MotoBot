import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from config import token, g_id, CHAT_ID
from base import Base
from random import choice, randint as rd


class MyLongPoll(VkBotLongPoll):  # Класс, который фиксит оригинальный класс LongPoll
	def listen(self):
		while True:
			try:
				for event in self.check():
					yield event
			except Exception as error:
				print(error)


class Bot:
	def __init__(self):
		self.vk_session = vk_api.VkApi(token=token)
		self.longpoll = MyLongPoll(self.vk_session, g_id)
		self.base = Base('data.db')
		self.percent = 5

	def sender(self, chat_id, msg):  # Отправка сообщений
		try:
			self.vk_session.method('messages.send', {'chat_id': chat_id, 'message': msg, 'random_id': 0})
		except Exception as e:
			print(f'Error send message: {e}')

	def get_user_name(self, vk_id):  # Получение имени и фамилии пользователя
		data = self.vk_session.method('users.get', {'user_id': vk_id})[0]
		return f'{data["first_name"]} {data["last_name"]}'

	def run(self):  # Основная функция бота
		for event in self.longpoll.listen():
			if event.type == VkBotEventType.MESSAGE_NEW:
				print(event.chat_id, event.object.message['from_id'], event.object.message['text'])
				if event.chat_id == CHAT_ID:

					user_id = event.object.message['from_id']
					user = self.base.get_user(user_id)
					msg = event.object.message['text'].lower()
					chat_id = event.chat_id

					if msg == '/пробег':
						self.sender(chat_id, f'Ваш пробег: {self.base.get_dist(user_id)} км.')

					elif msg == '/поехали':
						if self.base.get_last_try(user_id):
							if not (rd(0, 1000) in range(self.percent * 10)):
								dist = self.base.run(user_id)
								if dist:
									self.sender(chat_id, f'{self.get_user_name(user_id)}, cегодня вы проехали {dist} километров!\nТеперь ваш пробег составляет {self.base.get_dist(user_id)} км.')
								else:
									self.sender(chat_id, choice(
										[
											'Увы, ваш мотоцикл сломан, вы не проехали ни одного километра!',
											'Вам не повезло(\nВаш транспорт заглох'
										]
									))
								self.base.set_last(user_id)
							else:
								self.sender(chat_id, 'Ваш транспорт сломан!\nВы не можете ехать сегодня!')
								self.base.set_last(user_id)
						else:
							self.sender(chat_id, f'Вы уже использовали свою попытку сегодня!')

					elif msg == '/топ':
						ans = 'Топ пробега:'
						top = self.base.get_top()
						num = 1
						for usr in top:
							ans = f'{ans}\n{num}) {self.get_user_name(usr[0])}: {usr[1]} км.'
							num += 1
						self.sender(chat_id, ans)


if __name__ == '__main__':
	Bot().run()

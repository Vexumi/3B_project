import vk_api
import random


def auth_handler():
    """ При двухфакторной аутентификации вызывается эта функция. """

    # Код двухфакторной аутентификации,
    # который присылается по смс или уведомлением в мобильное приложение
    key = input("Enter authentication code: ")
    # Если: True - сохранить, False - не сохранять.
    remember_device = True

    return key, remember_device


login, password = '89137939434', 'isq_bt7274'
vk_session = vk_api.VkApi(
    login, password,
    # функция для обработки двухфакторной аутентификации
    auth_handler=auth_handler
)

try:
    vk_session.auth()
except vk_api.AuthError as error_msg:
    print(error_msg)
vk = vk_session.get_api()
response = vk.photos.get(owner_id=-161642411, album_id='wall', offset=random.randint(0, 3055),
                         count=1)
print(response['items'][0]['sizes'][-1]['url'])
# Используем метод wall.get
# response = vk.wall.get(owner_id=-161642411, count=1, offset=2)
# for i in response['items']:
#     for photo in i['attachments']:
#         print(photo['photo']['sizes'][0]['url'])

# 3B_project
# Начало работы
1) Для работы бота требуется вставить дискорд-токен, логин и пароль от аккаунта ВК в файл "dialogs.json", в соответствующие поля. 
    * Логин и пароль от аккаунта Вконтакте используется для получения картинок из групп.
    * Для получения дискорд-токена требуется перейти по ссылке (https://discord.com/developers/applications), создать приложение, нажав на кнопку "New Application" сверху справа. После чего перейти во вкладку "AOuth2" и поставить галочку возле "bot", после чего спуститься ниже и поставить возле "Administrator", теперь ссылка для приглашения бота появится выше. Для получения токена нужно перейти во вкладку "Bot" и нажать на кнопку "Copy".
2) Пригласить бота используя ссылку из предыдущего пункта.
3) Создать на сервере роли "Bot Master" (участникам с этой ролью будут доступны все команды в том числе банить и кикать участников) и "Bot Commander" (участникам с этой ролью будут доступны только основные команды).
4) Запустить "main.py"

# Дополнительные настройки 
* Для выдачи специальных превелегий, неиспользуя роли, вы можете вставить id пользователей в файл "dialogs.json" в строки "who_can_ban" и/или "who_can_kick".
* Вы можете изменить названия ролей (вместо "Bot Master" и "Bot Commander") в файле "dialogs.json" в строке "permission_roles".
* Так же вы можете изменить группы из которых бот будет брать мемы, меняется это в файле "dialogs.json" в строке "id_groups_for_mems".
* Для изменения надписи игры в которую играет бот в дискорде нужно изменить строку "bot_play_game" в файле "dialogs.json".
* Для изменения префикса (по умолчанию "#") в коммандах (пример: "#help") нужно изменить строку "prefix" в файле "dialogs.json".
* Для изменения картинок отправляемых при встречах нужно сохранить картинку в папке source/img и в файле "dialogs.json" в строке "img_meetings" добавить название картинок.

# Управление и работа
1) Для получения списка всех команд необходимо написать в чат "#help"
2) Для получения дополнительных данных нужно написать "#help /command_name/"
3) Команды подаются в формате "#/command_name\ |first_arg| |second_arg| |third_arg|..."
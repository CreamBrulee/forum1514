# FORUM1514 
https://better-valuable-node.glitch.me

> Форум создан для комфортного общения учеников школы 1514

## Структура
+ **Server.py** - основной файл
+ **Templates** - html файлы
+ **Static/img** - хранение базовой аватарки
+ **forms** - flask-wtf формы
    - **newsform.py** - форма фобавления поста
    - **login.py** - для логинизации
    - **user.py** - для регистрации пользователя
    - **editacc.py** - для редактирования профиля
+ **data** - ORM-models
    - **comments.py** - таблица коментариев к постам
    - **news.py** - таблица постов
    - **users.py** - таблица пользователей
    - **images.py** - таблица аватарок

## Реализованные возможности
+ Регистрация и логинизация
+ Добавление постов
+ Редактирование и удаление постов
+ Комментирование постов, вложенность комментариев
+ Редактирование профиля, добавление аватарки
+ Просмотр профилей авторов постов и комментаторов
+ Создание личных постов, видимых только в вашей ленте и профиле
+ Поиск по постам

## Дальнейшие идеи
- Возможность лайкать и дизлайкать посты
- Возможность загрузки файлов в посты
 

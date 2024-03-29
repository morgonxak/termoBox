# termoBox 09.09.2020
Данный проект предназначен для измерения температуры с тепловизора и с помощью пирометра. Также в данном проекте реализованна функция идентификации пользователя.
## Оборудование:
0. Камера для Raspberry Pi «Модель IR-CUT B»
0. Инфракрасный тепловизор AMG8833
0. Инфракрасный датчик MLX90614
0. Микрокомпьютер Raspberry Pi 4 4гб
0. Цветной сенсорный HDMI-дисплей для Raspberry Pi 480×320 / 3,5”
0. Двухцветный светодиод (красно-зелёный)
0. Пьезо-датчик (для звукового сигнала)
0. Инфракрасный дальномер Sharp (4-30 см)

## Основные зависимости
0. PostgreSQL
0. OpenCV
0. pyhton 3.7
0. cmake
    
## Установка:
0. mkdir thermoBox && cd thermoBox
0. python3 -m venv .env
0. source .env/bin/activate
0. pip install -r requirements.txt
0. Второй вариант, если какие либо пакеты не могут поставится: cat requirements.txt | xargs -n 1 pip install
0. Запуск: pyhton run.py

## Настройки распологаются: app_thermometer/__init__.py:
0. база данных находится app_thermometr/rs/thermobox_database.dump
0. Установить базу: psql thermobox < thermobox_database.dump
0. Сделать dump: pg_dump thermobox > thermobox_database.dump

## Описания сохраниения данных 
## Данные хранящиеся в базе (PostgreSQL)
1. Таблица users - Хранит информацию о пользователе (ФИО, Дата создания, Дата удаления поьзователя)
2. Таблица Log - Хранит информацио о прохождении через коробку (uuid пользователя, дата время, температуры датчиков, непересчитанные температуры с датчиков, имя изображения пользователя)
## Формат хрнанения фотографий: uuid_data_flag1_t1_t2_flag2.jpg
1. **uuid** - Уникальный идентификатор фотографии
2. **data** - Дата время сьемки
3. **flag1** - 0/1 - Повышеная температура или нет
4. **flag2** - 0/1 - Распознанный пользователь или нет
5. **t1** - Температура тепловизора, если значения -1 значет были проблемы с температурой
6. **t2** - Температура пирометра, если значения -1 значет пользователь не поднес руку.

## Схема подключения оборудования
![alt text](https://github.com/morgonxak/termoBox/blob/9_9_20/app_thermometer/rc/connection_diagram.png)

## Распиновка
![alt text](https://github.com/morgonxak/termoBox/blob/9_9_20/app_thermometer/rc/pins.png)

## Полузные ссылки:
0. https://github.com/adafruit/Adafruit_CircuitPython_AMG88xx.git
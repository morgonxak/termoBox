# import psycopg2
import cv2
import datetime
import uuid
import os
import sqlite3
import numpy 

class BD:
    '''
    Класс для работы с основной базой данных пользователя
    '''
    def __init__(self, path_bd_file:str, path_save_image:str = "/home/pi/project/log"):
        
        #print(path_save_image)
        #Соеденения с базой данных
        self.path_save_image = path_save_image
        try:
            os.makedirs(self.path_save_image)
        except OSError:
            pass
        else:
            print("Успешно создана директория log")

        self.dict_connect_settings = os.path.abspath(os.path.join(os.getcwd(), path_bd_file))

        try:
            self.con = self.connect_sqlite3(self.dict_connect_settings)
            self.cur = self.con.cursor()
            
        except BaseException as e:
            raise ValueError("Error create cursor {} path {}".format(e, self.dict_connect_settings))

    def connect_sqlite3(self, pathDataBase:str):
        '''
        Соеденяемся с базой данных
        :param pathDataBase:
        :return:
        '''
        try:
            con = sqlite3.connect(pathDataBase)
        except BaseException as e:
                raise ValueError("Error sqlite3 connect BD: {}".format(e, self.dict_connect_settings))
        return con

    def get_people_name_by_person_id(self, person_id: str):
        '''
        Получает имя пользователя по уникальному ключу
        :param person_id: str
        :return first_name: str - хороший результат -1 Ошибка или нет такого пользователя
        '''
        try:
            self.cur.execute("SELECT first_name from users WHERE personId = '{}'".format(person_id))

            row = self.cur.fetchone()[0]

        except BaseException as e:
            print(ValueError("Error get_people_name_by_person_id: {}".format(e)))
            return -1
        else:
            return row

    def is_person_id(self, person_id: str):
        '''
        Есть ли пользователь в базе
        :param person_id:
        :return bool:
        '''
        try:
            self.cur.execute("SELECT personId from users WHERE personId = '{}'".format(person_id))

            row = self.cur.fetchall()
            if len(row) != 0:
                return True
            else:
                return False

        except BaseException as e:
            print(ValueError("Error get Users info: " + str(e)))
            return -1

    def pull_log(self, frame, flag_disease, person_id=None):
        '''
        Отправляет данные логирования
        Формат сохранения изображения:
        Уникальный идентификатор_дата время_болен_распознан нет_
        :param frame: Кадр для сохранения
        :param flag_disease: больной пользователь или нет bool
        :param person_id: ели none то пользователь не известный
        :return: 0 все хорошо, -1 что то не так
        '''
        try:

            data_time = str(datetime.datetime.now())
            recognition = int(not person_id is None)
            if person_id is None: person_id = '00000000-0000-0000-0000-000000000000'


            name_image = '{}_{}_{}_{}'.format(str(uuid.uuid4()), data_time.replace('-', '_').replace(' ', '_'), int(flag_disease), recognition)
            #print(self.path_save_image)
            str_ =  os.path.join(self.path_save_image, name_image + '.jpg')
            try:
                #print(" save image {} ".format(type(frame)))
                cv2.imwrite(str_, frame)
            except BaseException as e:
                print("error save image {} {}".format(str_, e))
            except:
                print("error save image {}".format(str_))
            self.cur.execute(
                "INSERT INTO log (person_id, data_time, name_image) VALUES ('{}', '{}', '{}')".format(person_id, data_time, name_image)
            )

            self.con.commit()

        except ZeroDivisionError as e:
            print("Error pull log {}".format(e))
            return -1

        return 0

    def pull_temperature(self, data_teplovizor: list, data_pirometr: list, is_hand, is_fase):
        '''
        Заполняет базу с температурами
        :param data_teplovizor: Масив с температурами с тепловизора
        :param data_pirometr: Масив с температурами с пирометра
        :param is_hand: Данный о руке /0 - есть рука / 1 - нет руки
        :param is_fase: Данные о лице /1 - есть лицо / 2 - нет лицо
        :return: 0 все хорошо, -1 что то не так
        '''

        try:
            data_time = str(datetime.datetime.now())
            self.cur.execute(
                "INSERT INTO log_temperature (data_time, temperature_teplovizor, temperature_pirometr, is_hand, is_face) VALUES ('{}', '{}', '{}', '{}', '{}')".format(
                    data_time, str(data_teplovizor), str(data_pirometr), int(is_hand), int(is_fase))
            )
            self.con.commit()
        except BaseException as e:
            print("Error pull_temperature {}".format(e))
            return -1
        return 0

    def pull_log_background(self, data_teplovizor: list, data_pirometr: list):
        '''
        Заполняем данные окружающий среды
        :param data_teplovizor: данные тепловизора
        :param data_pirometr: данные пирометра
        :return:  0 все хорошо, -1 что то не так
        '''
        try:
            data_time = str(datetime.datetime.now())
            self.cur.execute(
                "INSERT INTO log_background (data_time, temperature_teplovizor, temperature_pirometr) VALUES ('{}', '{}', '{}')".format(
                    data_time, str(data_teplovizor), str(data_pirometr))
            )
            self.con.commit()
        except BaseException as e:
            print("Error pull_log_background {}".format(e))
            return -1
        return 0

    def pull_calibration_threshold(self, threshold_teplovizor: float, threshold_pir: float):
        '''
        Заполняем данные калибровки хранит коэфициент
        :param threshold_teplovizor:
        :param threshold_pir:
        :return:
        '''
        try:
            data_time = str(datetime.datetime.now())
            self.cur.execute(
                "INSERT INTO calibration_threshold (data_time, threshold_teplovizor, threshold_pir) VALUES ('{}', '{}', '{}')".format(
                    data_time, threshold_teplovizor, threshold_pir)
            )
            self.con.commit()
            return 0
        except BaseException as e:
            print("Error pull_calibration_threshold {}".format(e))
            return -1

    def get_calibration_threshold(self):
        '''
        Получает данные о последней колибровки
        :return: (ДатаВремя, Температура пирометра, температура тепловизора)
        '''
        try:
            self.cur.execute("SELECT max(id)  from calibration_threshold")
            row = self.cur.fetchone()[0]

            self.cur.execute("SELECT data_time, threshold_pir, threshold_teplovizor  from calibration_threshold WHERE id = '{}'".format(row))

            rows = self.cur.fetchall()
            data_time, threshold_pir, threshold_teplovizor = rows[0]
            return data_time, threshold_pir, threshold_teplovizor

        except BaseException as e:
            print(ValueError("Error get_calibration_threshold: {}".format(e)))
            
    def get_agv_10_calibration_threshold(self):
        '''
        Получает данные о колибровки
        :return: (ДатаВремя, Температура пирометра, температура тепловизора)
        '''
        data_str = str(datetime.datetime.today().strftime("%Y-%m-%d"))
        #print(data_str)
        try:
            sql_str = "SELECT count(data_time) FROM( SELECT (data_time) FROM log_temperature WHERE data_time LIKE '{}'||'%'  and temperature_teplovizor <> 'None' and is_hand = 0 ORDER BY data_time DESC  LIMIT 10)".format(data_str) # DESC
            
            #print(sql_str)
            self.cur.execute(sql_str)
            #row = self.cur.fetchone()[0]

            row = self.cur.fetchall()
            #print(row)
            #print(row[0][0])
            if row[0][0] < 10:
                return False, 0, 0
            sql_str = "SELECT temperature_teplovizor, temperature_pirometr FROM log_temperature WHERE data_time LIKE '{}'||'%' and temperature_teplovizor <> 'None' and is_hand = 0 ORDER BY data_time DESC LIMIT 10".format(data_str)  # DESC 
            self.cur.execute(sql_str)

            rows = self.cur.fetchall()
            
            #print(rows[0])
            max_teplovizor = []
            max_pirometr = []
            for number in range(0, 10):
                threshold_teplovizor, threshold_pirometr = rows[number]
                #print(threshold_pirometr)
                threshold_teplovizor = threshold_teplovizor.replace("[", "").replace("]", "").replace("\n", " ").replace(" ", "\n").replace("\n\n", "\n")
                threshold_teplovizor = threshold_teplovizor.replace("\n\n", "\n").split('\n')

                threshold_pirometr = threshold_pirometr.replace("[", "").replace("]", "").replace("\n", " ").replace(" ", "\n").replace("\n\n", "\n")
                threshold_pirometr = threshold_pirometr.replace("\n\n", "\n")

                #print(threshold_pirometr)
                max_teplovizor.append(float(max(threshold_teplovizor)))
                max_pirometr.append(float((threshold_pirometr)))
                
                #print(max_teplovizor[-1],max_pirometr[-1])
            avg_teplovizor = sum(max_teplovizor) / len(max_teplovizor)
            avg_pirometr = sum(max_pirometr) / len(max_pirometr)
            #print(avg_teplovizor,avg_pirometr , "!!!!")
            
            
            return True, round(avg_teplovizor, 1), round(avg_pirometr, 1)

        except BaseException as e:
            print(ValueError("Error get_agv_10_calibration_threshold: {}".format(e)))
            
            
            
class PASS_OFFICE(BD):
    def __init__(self, path_bd_file: str, path_save_image: str):
        super(PASS_OFFICE, self).__init__(path_bd_file, path_save_image)

    def pull_users(self, person_id, last_name, first_name, middle_name):
        '''
        Отправляем данные в базу
        :param person_id:
        :param last_name:
        :param first_name:
        :param middle_name:
        middle_name
        :return:
        '''

        self.cur.execute(
            "INSERT INTO users (personId, last_name, first_name, middle_name, mode_skip) VALUES ('{}', '{}', '{}', '{}', '{}')".format(
                person_id, last_name, first_name, middle_name, 0)
        )
        self.con.commit()

class DATA_BASE_TELEGRAM_BOT(BD):

    def __init__(self, dataBase_file: str, path_save_image: str):

        super(DATA_BASE_TELEGRAM_BOT, self).__init__(dataBase_file, path_save_image)

        self.con = self.connect_sqlite3(dataBase_file)
        self.cur = self.con.cursor()
        self.last_sick = None

    def get_subscriptions(self, status=True):
        """Получаем всех активных подписчиков бота"""
        with self.con:
            return self.cur.execute("SELECT * FROM `telegram_bot` WHERE `status` = ?", (status,)).fetchall()

    def subscriber_exists(self, user_id):
        """Проверяем, есть ли уже юзер в базе"""
        with self.con:
            result = self.cur.execute('SELECT * FROM `telegram_bot` WHERE `user_id` = ?', (user_id,)).fetchall()
            return bool(len(result))

    def add_subscriber(self, user_id, status=True):
        """Добавляем нового подписчика"""
        with self.con:
            return self.cur.execute("INSERT INTO `telegram_bot` (`user_id`, `status`) VALUES(?,?)",
                                       (user_id, status))

    def update_subscription(self, user_id, status):
        """Обновляем статус подписки пользователя"""
        with self.con:
            return self.cur.execute("UPDATE `telegram_bot` SET `status` = ? WHERE `user_id` = ?", (status, user_id))

    def get_full_name_by_person_id(self, person_id):
        '''
        Получает пользователя по уникальному ключу
        :param person_id:
        :return:
        '''
        try:
            self.cur.execute("SELECT last_name, first_name, middle_name from users WHERE personId = '{}'".format(person_id))

            row = self.cur.fetchone()
            return '{} {} {}'.format(row[0], row[1], row[2])
        except BaseException as e:
            print(ValueError("Error get Users info: " + str(e)))
            return -1

    #todo Надо доделать
    def get_data_for_report_1(self, period_dey=7, period_min=5):
        '''
        Формирует отчет о заболевших за последнее время
        Действия:
        1) ищем в таблице Log за временной поромежуток все запеси
        2) Проходим по каждой из записей получаем:
            1.ФИО если пользователь был распознан
            2.Его фотографию
            3.дату время прохода
            3.1 Зная время прохода берем промежуток по времени +- 1сек
            3.2 В таблице с температурами находим температуры данного пользователя
            3.3 todo необходимо дописать отчет так как поменялась логика
        :param period_dey:
        :param period_min:
        :return:
        '''

        current_time = datetime.datetime.now()
        period_search = current_time - datetime.timedelta(days=period_dey, minutes=period_min)
        print("временной промежуток: ", current_time, period_search)

        self.cur.execute("SELECT person_id, data_time, name_image from log WHERE data_time BETWEEN '{}' and '{}'".format(period_search, current_time))

        rows = self.cur.fetchall()

        # ['01-12-2020', 'Shumelev Dmitry Igorevith', '36.6', '37.8', 'Проходит', '/home/dima/Изображения/Nnec5EGL3oo.jpg']
        data_report = []
        for log_data in rows:
            person_id = log_data[0]
            name_photo = os.path.join(self.path_save_image, log_data[2]+'.jpg')
            if person_id != '00000000-0000-0000-0000-000000000000':
                fullName = self.get_full_name_by_person_id(person_id)
            else:
                fullName = "Пользователь не распознан"

            time_temp = log_data[1]  #2020-10-29 12:00:50.660110
            time_temp = datetime.datetime.strptime(time_temp, '%Y-%m-%d %H:%M:%S.%f')

            time_1 = time_temp - datetime.timedelta(seconds=1)
            time_2 = time_temp + datetime.timedelta(seconds=1)

            self.cur.execute("SELECT * from log_temperature WHERE data_time BETWEEN '{}' and '{}'".format(time_1, time_2))

            rows = self.cur.fetchall()
            for measurements in rows:

                data_pir = max(measurements[1].strip('][').split(', '))
                data_tepl = max(measurements[2].strip('][').split(', '))

                if float(data_pir) >= 37.6:
                    solutions = 'Подозрительный поьзователь'
                else:
                    solutions = 'Все нормально'
                update_date_time = str(time_temp)[:str(time_temp).rfind('.')]
                data_report.append([update_date_time, fullName, data_pir, data_tepl, solutions, name_photo])

        print(data_report)

        return (str(str(current_time)[:str(current_time).rfind('.')]), str( str(period_search)[:str(period_search).rfind('.')])), data_report


if __name__ == '__main__':
    import numpy
    path_save_image = '/home/pi/project/log'
    dict_connect_settings = '/home/dima/PycharmProjects/termoBox/rc/database.bd'

    test = DATA_BASE_TELEGRAM_BOT(dict_connect_settings, path_save_image)
    #frame, flag_disease, person_id=None
    # print(test.get_people_name_by_person_id('b9e1d2bc-ac4f-4b5b-bec3-fd586c8c3e4'))
    # print(test.is_person_id('b9e1d2bc-ac4f-4b5b-bec3-fd586c8c3e4'))
    # test.pull_log(numpy.zeros([100, 100, 3], dtype=numpy.uint8), True, None) #+
    # test.pull_temperature([1,2,3,4,5],[1.2,1,3,4,2], True, False)
    # test.pull_log_background([1,2,3,4,5],[1.2,1,3,4,2])
    # print(test.get_full_name_by_person_id('b9e1d2bc-ac4f-4b5b-bec3-fd586c8c3e49'))
    # print(test.get_calibration_threshold())
    print(test.pull_calibration_threshold(6, 5))

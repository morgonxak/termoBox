import psycopg2
import cv2
import datetime
import uuid
import os
import sqlite3


if 1==2:
    dict_connect_settings = {"database": "thermobox",
                             "user": "pi",
                             "password": "asm123",
                             "host": "10.10.22.214",
                              "port": "5432"}
else:
    dict_connect_settings = '/home/dima/Загрузки/termoBox-9_9_20/database.bd'

path_save_image = '/home/pi/project/log'

class BD:
    def __init__(self, dict_connect_settings, type_BD=1, path_save_image=path_save_image):
        #0 - psycopg2
        #1 - sqlite3

        #Соеденения с базой данных
        #if type(dict_connect_settings) != 'str':
        self.path_save_image = path_save_image
        try:
            os.makedirs(self.path_save_image)
        except:
            None
        else:
            print ("Успешно создана директория log")                              

        self.dict_connect_settings = os.path.abspath(os.path.join(os.getcwd(), dict_connect_settings))
        if type_BD == 0:
            self.con = self.connect_psycopg2(self.dict_connect_settings)
        elif type_BD == 1:
            self.con = self.connect_sqlite3(self.dict_connect_settings)
        else:
           raise ValueError("Error type_BD {}".format(type_BD)) 
        try:
            self.cur = self.con.cursor()
            
        except BaseException as e:
            raise ValueError("Error create cursor " + str(e) + " ("+ self.dict_connect_settings+ ")")
    def connect_psycopg2(self, dict_connect_settings):
        try:
            con = psycopg2.connect(
                database=dict_connect_settings['database'],
                user=dict_connect_settings['user'],
                password=dict_connect_settings['password'],
                host=dict_connect_settings['host'],
                port=dict_connect_settings['port'])
            return con
        except BaseException as e:
            raise ValueError("Error psycopg2 connect BD: " + str(e))
    
    def connect_sqlite3(self, pathDataBase:str):
        '''
        Соеденяемся с базой данных
        :param pathDataBase:
        :return:
        '''
        try:
            con = sqlite3.connect(pathDataBase)
            return con
        except BaseException as e:
                raise ValueError("Error sqlite3 connect BD: " + str(e) + " ("+ self.dict_connect_settings+ ")")
        
        #except Error:
         #   print(Error)

    #+++++++++++
    def get_people_name_by_person_id(self, person_id):
        '''
        Получает пользователя по уникальному ключу
        :param person_id:
        :return first_name:
        '''
        try:
            self.cur.execute("SELECT first_name from users WHERE person_id = '{}'".format(person_id))

            rows = self.cur.fetchall()
        except BaseException as e:
            raise ValueError("Error get Users info: " + str(e))
        else:
            return rows[0][0]

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
            "INSERT INTO users (person_id, last_name, first_name, middle_name, mode_skip) VALUES ('{}', '{}', '{}', '{}', '{}')".format(
                person_id, last_name, first_name, middle_name, 0)
        )
        self.con.commit()

    def is_person_id(self, person_id):
        '''
        Присутствует ли пользователь в базе
        :param person_id:
        :return bool:
        '''
        try:
            self.cur.execute("SELECT person_id  from users WHERE person_id = '{}'".format(person_id))

            rows = self.cur.fetchall()
        except BaseException as e:
            raise ValueError("Error get Users info: " + str(e))
        else:
            if len(rows) != 0:
                return True
            else:
                return False

    def pull_log(self, frame, flag_disease, person_id=None):
        '''
        Отправляет данные логирования
        :param frame: Кадр для сохранения
        :param flag_disease: больной пользователь или нет bool
        :param person_id: ели none то пользователь не известный
        :return: 0 все хорошо, -1 что то не так
        '''
        try:
            data_time = str(datetime.datetime.now())
            if person_id is None: person_id = '00000000-0000-0000-0000-000000000000'
            
            if person_id is None:
                recognition = 0
            else:
                recognition = 0

            if flag_disease:
                flag_disease = 1
            else:
                flag_disease = 0


            name_image = '{}_{}_{}_{}'.format(str(uuid.uuid4()), data_time.replace('-', '_').replace(' ', '_'), flag_disease, recognition)
            cv2.imwrite(os.path.join(path_save_image, name_image + '.jpg'), frame)

            self.cur.execute(
                "INSERT INTO log (person_id, data_time, name_image) VALUES ('{}', '{}', '{}')".format(person_id, data_time, name_image)
            )
            self.con.commit()
        except ZeroDivisionError as e:
            print("Error pull log {}".format(e))
            return -1
        return 0

    def pull_temperature(self, data_teplovizor, data_pirometr, is_hand, is_fase): #list
        '''
        Заполняет базу с температурами
        :param data_teplovizor: Масив с температурами с тепловизора
        :param data_pirometr: Масив с температурами с пирометра
        :param is_hand: Данный о руке
        :param is_fase: Данные о лице
        :return: 0 все хорошо, -1 что то не так
        '''
        if is_hand:
            is_hand = 1
        else:
            is_hand = 0

        if is_fase:
            is_fase = 1
        else:
            is_fase = 0

        try:
            data_time = str(datetime.datetime.now())
            self.cur.execute(
                "INSERT INTO log_temperature (data_time, temperature_teplovizor, temperature_pirometr, is_hand, is_face) VALUES ('{}', '{}', '{}', '{}', '{}')".format(
                    data_time, str(data_teplovizor), str(data_pirometr), is_hand, is_fase)
            )
            self.con.commit()
        except BaseException as e:
            print("Error pull_temperature {}".format(e))
            return -1
        return 0

    def pull_log_background(self, data_teplovizor, data_pirometr): #:list
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

    def test(self):
        '''
        Для заполнения базы пользователей
        :return:
        '''
        url = "http://82.179.15.125:10101/IntegrationService/IntegrationService.asmx"
        # domain = '\xd0\x9a\xd0\xb5\xd0\xbc\xd0\x93\xd0\xa3'
        domain = 'КемГУ'
        userName = 'test'
        password = '123456'
        path_dataset = r'/media/dima/Новый том/ptotoRGBD_2/faceid_train'

        import datetime
        from expiriments.pull_info_iser.Parsec_API import prosecApi
        obj_BD = BD(dict_connect_settings)
        test = prosecApi(url, userName, password, domain)

        for count, person_id in enumerate(os.listdir(path_dataset)):
            infoUser = test.get_photo_by_person_id(person_id)
            try:
                last_name = infoUser[person_id]['LAST_NAME']
                first_name = infoUser[person_id]['FIRST_NAME']
                middle_name = infoUser[person_id]['MIDDLE_NAME']
                print(count, person_id, last_name, first_name, middle_name)
                try:
                    obj_BD.pull_users(person_id, last_name, first_name, middle_name)
                except sqlite3.IntegrityError:
                    print("Пользователь уже в базе")
            except BaseException as e:
                print("error: {}".format(e))

if __name__ == '__main__':

    test = BD(dict_connect_settings)
    #frame, flag_disease, person_id=None
    test.pull_log(np.zeros([100, 100, 3], dtype=np.uint8), True, None) #+
    test.pull_temperature([1,2,3,4,5],[1.2,1,3,4,2], True, False)
    test.pull_log_background([1,2,3,4,5],[1.2,1,3,4,2])

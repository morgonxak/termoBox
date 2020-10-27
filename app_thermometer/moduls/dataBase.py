import psycopg2
import base64
import numpy as np
import cv2
import datetime
import uuid
import os

import sqlite3
from sqlite3 import Error

if 1==2:
    dict_connect_settings = {"database": "thermobox",
                             "user": "pi",
                             "password": "asm123",
                             "host": "10.10.22.214",
                              "port": "5432"}
else:
    dict_connect_settings = '/home/pi/project/recognition_service_client_simplified/rc/database'

path_save_image = '/home/pi/project/log'

class BD:
    def __init__(self, dict_connect_settings, type_BD=1):
        #0 - psycopg2
        #1 - sqlite3

        #Соеденения с базой данных
        #if type(dict_connect_settings) != 'str':
        self.dict_connect_settings = os.path.abspath(os.path.join(os.getcwd(),dict_connect_settings))
        if type_BD == 0:
            self.con = self.connect_psycopg2(self.dict_connect_settings)
        elif type_BD == 1:
            self.con =  self.connect_sqlite3(self.dict_connect_settings)
        else:
           raise ValueError("Error type_BD {}".format(type_BD)) 
        try:
            self.cur = self.con.cursor()
            
        except BaseException as e:
            raise ValueError("Error create cursor " + str(e))

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
                raise ValueError("Error sqlite3 connect BD: " + str(e))
        
        #except Error:
         #   print(Error)

    def push_data_log(self, flag_disease, frame:np.ndarray, temp_pirom=None, temp_teplovizor=None, raw_pirom=None, raw_teplovizor=None, person_id=None):
        '''
        ОТправляет логи в базу данных
        :param person_id:
        :param data_time:
        :param temp_pirom:
        :param temp_teplovizor:
        :param raw_pirom:
        :param raw_teplovizor:
        :return:
        '''
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

        if temp_pirom is None: temp_pirom = -1
        if temp_teplovizor is None: temp_teplovizor = -1
        if raw_pirom is None: raw_pirom = -1
        if raw_teplovizor is None: raw_teplovizor = -1
        
        name_image = '{}_{}_{}_{}_{}_{}'.format(str(uuid.uuid4()), data_time.replace('-', '_').replace(' ', '_'), flag_disease, temp_teplovizor, temp_pirom, recognition)

        #self.cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='log')
        
        try: #DATETIME
            self.cur.execute('''CREATE TABLE log(person_id INTEGER, data_time DATETIME, temp_pirometr INTEGER, temp_teplovizor INTEGER, raw_pirometr INTEGER, raw_teplovizor INTEGER, name_image TEXT)''')
            self.con.commit()
        except:
            None
        
        cv2.imwrite(os.path.join(path_save_image, name_image+'.jpg'), frame)

         
        str_ = "INSERT INTO log (person_id, data_time, temp_pirometr, temp_teplovizor, raw_pirometr, raw_teplovizor, name_image) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
                person_id, data_time, temp_pirom, temp_teplovizor, raw_pirom, raw_teplovizor, name_image) 
        #print(str_)
        
        self.cur.execute(str_)
        self.con.commit()
        

    def get_people_name_by_person_id(self, person_id):
        '''

        :param person_id:
        :return:
        '''
        try:
            self.cur.execute("SELECT first_name from users WHERE person_id = '{}'".format(person_id))

            rows = self.cur.fetchall()
        except BaseException as e:
            raise ValueError("Error get Users info: " + str(e))
        else:
            return rows[0][0]

    def pull_users(self, person_id, surname, first_name, middle_name):
        '''
        Отправляем данные в базу
        :param person_id:
        :param surname:
        :param first_name:
        :param middle_name:
        :return:
        '''

        self.cur.execute(
            "INSERT INTO users (person_id, surname, first_name, middle_name, create_time) VALUES ('{}', '{}', '{}', '{}', '{}')".format(
                person_id, surname, first_name, middle_name, str(datetime.datetime.now()))
        )
        self.con.commit()


# def add_people():
#     '''
#     path_photo:
#
#     :param path_photo:
#     :return:
#     '''
#
#     print("dasd")
#     for people in known_face_names:
#         person_id = people
#         surname = known_face_names[people]['lastname']
#         first_name, middle_name = known_face_names[people]['initials'].split(' ')
#         print(person_id, surname, first_name, middle_name)
#         obj_BD.pull_users(person_id, surname, first_name, middle_name)

if __name__ == '__main__':
    import datetime
    obj_BD = BD(dict_connect_settings)
    #obj_BD.push_data_log(temp_pirom=36.1)
    #add_people()
    user = obj_BD.get_people_name_by_person_id('b9e1d2bc-ac4f-4b5b-bec3-fd586c8c3e49')
    print(user)
    #obj_BD.pull_users("00000000-0000-0000-0000-000000000000", 'Не распознан', 'Тест', "test")

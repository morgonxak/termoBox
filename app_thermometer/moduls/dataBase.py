import psycopg2
import base64
import numpy as np
import cv2
import datetime
import uuid
import os

dict_connect_settings = {"database": "thermobox",
                         "user": "pi",
                         "password": "asm123",
                         "host": "10.10.22.214",
                          "port": "5432"}

path_save_image = '/home/pi/project/log'

class BD:
    def __init__(self, dict_connect_settings):
        #Соеденения с базой данных
        try:
            self.con = psycopg2.connect(
                database=dict_connect_settings['database'],
                user=dict_connect_settings['user'],
                password=dict_connect_settings['password'],
                host=dict_connect_settings['host'],
                port=dict_connect_settings['port'])
        except BaseException as e:
            raise ValueError("Error connect BD: " + str(e))

        try:
            self.cur = self.con.cursor()
        except BaseException as e:
            raise ValueError("Error create cursor " + str(e))

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

        cv2.imwrite(os.path.join(path_save_image, name_image+'.jpg'), frame)
        self.cur.execute(
            "INSERT INTO log (person_id, data_time, temp_pirometr, temp_teplovizor, raw_pirometr, raw_teplovizor, name_image) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
                person_id, data_time, temp_pirom, temp_teplovizor, raw_pirom, raw_teplovizor, name_image)
        )
        self.con.commit()


if __name__ == '__main__':
    import datetime
    obj_BD = BD(dict_connect_settings)
    obj_BD.push_data_log(temp_pirom=36.1)

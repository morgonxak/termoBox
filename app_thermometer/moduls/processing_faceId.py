'''
Модуль для проверки распознования миц и для дообучения CVM, Knn нейронных сетей
'''
import threading
import face_recognition

from app_thermometer.moduls.dict_user import known_face_names

class processing_faceid(threading.Thread):

    def __init__(self, queue, model_cvm, model_knn):
        '''

        :param queue: Задания
        :param model_cvm: открытые модели
        :param model_knn: открытые модели
        :param face_detector: Открытая модель лица
        :param path_madel:
        :param door:
        '''
        super().__init__()
        self.queue, self.model_cvm, self.model_knn = queue, model_cvm, model_knn
        self.dict_res = {}



    def get_descriptor_RGB(self, fase_RGB_200_200):
        '''
        создаем дискриптор для RGBизображения
        :param fase_RGB_200_200:
        :return:
        '''
        face_encoding = face_recognition.face_encodings(fase_RGB_200_200)
        return face_encoding

    def __predict_cvm(self, face_encoding):
        '''
        Проверяет пользователя по модели CVM
        :param face_encoding: Получаем дескриптор
        :return: person_id -- Уникальный идентификатор пользователя
        '''
        # Прогнозирование всех граней на тестовом изображении с использованием обученного классификатора
        try:
            person_id = self.model_cvm.predict(face_encoding)
        except ValueError:
            person_id = None

        return person_id

    def __predict_knn(self, face_encoding, tolerance=0.4):
        '''
        Проверяет пользователя по модели knn
        :param face_encoding:
        :param tolerance: Коэфициент похожести
        :return: person_id, dist == уникальный идентификатор и дистанция до него
        '''
        try:
            closest_distances = self.model_knn.kneighbors(face_encoding, n_neighbors=1)

            are_matches = [closest_distances[0][i][0] <= tolerance for i in range(1)]

            if are_matches[0]:
                person_id = self.model_knn.predict(face_encoding)[0]
            else:
                person_id = "Unknown"
        except ValueError:
            person_id = None

        return person_id

    def predict_freme(self, fase_RGB):
        # dict_res = {}

        descriptor_fase_RGB = self.get_descriptor_RGB(fase_RGB)

        res_predict_cvm = self.__predict_cvm(descriptor_fase_RGB)
        res_predict_knn = self.__predict_knn(descriptor_fase_RGB)
        print(res_predict_cvm, res_predict_knn, res_predict_cvm == res_predict_knn)

        if res_predict_cvm == res_predict_knn:
            if not res_predict_cvm is None:

                people = known_face_names.get(res_predict_cvm[0], None)
                #print("Найден пользователь:", people)
                if not people is None:
                    return people
                    # if not res_predict_cvm[0] in dict_res:
                    #     dict_res[res_predict_cvm[0]] = {}
                    #     dict_res[res_predict_cvm[0]]['name'] = people
                    # else:
                    #     dict_res[res_predict_cvm[0]]['name'] = people

        # self.dict_res = dict_res
        return None

    def run(self):
        '''
        Фходные данные Изображения в формате RGB
        :return:
        '''

        while True:
            fase_RGB = self.queue.get()

            dict_res = {}

            descriptor_fase_RGB = self.get_descriptor_RGB(fase_RGB)

            res_predict_cvm = self.__predict_cvm(descriptor_fase_RGB)
            res_predict_knn = self.__predict_knn(descriptor_fase_RGB)

            if res_predict_cvm == res_predict_knn:
                if res_predict_cvm is None:
                    pass
                else:
                    people = known_face_names.get(res_predict_cvm[0], None)
                    print("Найден пользователь:", people)
                    if not people is None:

                        if not res_predict_cvm[0] in dict_res:
                            dict_res[res_predict_cvm[0]] = {}
                            dict_res[res_predict_cvm[0]]['name'] = people
                        else:
                            dict_res[res_predict_cvm[0]]['name'] = people

            self.dict_res = dict_res

            # cv2.imshow("rgb", frame)
            # cv2.waitKey(1)







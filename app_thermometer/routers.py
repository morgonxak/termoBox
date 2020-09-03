from flask import Flask, render_template, Response, jsonify
from app_thermometer import app

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

#Трансляция данных с тепловизора

def gen_video_ir():
    while True:
        frame = app.config['camera_RGB'].get_IR_web()
        if not frame is None:
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_ir_feed')
def video_ir_feed():
    return Response(gen_video_ir(), mimetype='multipart/x-mixed-replace; boundary=frame')


######################################################################################################################

#Трансляция изображения с RGB камеры

def gen_video(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame_web()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_video(app.config['camera_RGB']), mimetype='multipart/x-mixed-replace; boundary=frame')

######################################################################################################################
#Отправка температуры


import json
import random
@app.route('/get_temp', methods=['GET', 'POST'])
def pull_IR_temp():
    '''
    Отправляет на веб страничку температуру с лица человека
    :return:
    '''
    t1, t2, mode = app.config['camera_RGB'].get_temp_web()
    if mode:
        mode = 1
    else:
        mode = 0

    d = {
        "T1": t1,
         "T2": t2,
        "mode_seekThermal": mode
         }

    print("json:", json)
    return str(json.dumps(d))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
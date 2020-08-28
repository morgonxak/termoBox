from flask import Flask, render_template, Response
from app_thermometer import app



def gen_video_ir():
    while True:
        frame = app.config['camera_IR'].getFrame_web()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_ir_feed')
def video_ir_feed():
    return Response(gen_video_ir(), mimetype='multipart/x-mixed-replace; boundary=frame')


######################################################################################################################

def gen_video(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame_web()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_video(app.config['camera_RGB']), mimetype='multipart/x-mixed-replace; boundary=frame')



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
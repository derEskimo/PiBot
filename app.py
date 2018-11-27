from flask import Flask, render_template, Response, request, send_file
import threading
import StepperLib
import RadarLib
import OpenCv
import RoboAssistant
from time import sleep
import pickle
import os

app = Flask(__name__)

motors = StepperLib.StepperMotor()
radar = RadarLib.Radar(motors)
threadAssistant = threading.Thread(target=RoboAssistant.main)
threadAssistant.start()

programStorage = []
speed = 0.002
programs = []

frame=None

def thread_move(direction):
    global programStorage, speed
    t = threading.currentThread()

    while getattr(t, "do_run", True):

        print("Moving " + direction)
        if direction == "forward":
            motors.step(1, 1)
            programStorage.extend([1, 1])
            sleep(speed)
        elif direction == "backward":
            motors.step(-1, -1)
            programStorage.extend([-1, -1])
            sleep(speed)
        elif direction == "turnLeft":
            motors.step(1, -1)
            programStorage.extend([1, -1])
            sleep(speed+0.01)
        elif direction == "turnRight":
            motors.step(-1, 1)
            programStorage.extend([-1, 1])
            sleep(speed+0.01)
    print("Stop")
    motors.off()


@app.route("/")
def getPage():
    load_dropdown()
    return render_template('index.html', programs=programs)


threadMove = threading.Thread(target=thread_move, args=("forward",))
@app.route("/move/<direction>", methods=['GET', 'POST'])
def move(direction):
    global threadMove
    if not threadMove.isAlive():
        threadMove = threading.Thread(target=thread_move, args=(direction,))
        threadMove.start()
    else:
        threadMove.do_run = False
        threadMove.join()
    return ('', 204)


@app.route("/delete", methods=['GET', 'POST'])
def not_Aus():
    global programStorage
    programStorage = []
    print("ProgramStorage geleert")
    return ('', 204)



@app.route('/video_feed')
def video_feed():
    return Response(OpenCv.gen(),
                mimetype='multipart/x-mixed-replace; boundary=frame')




@app.route("/speed_slider/<speed_value>", methods=['GET', 'POST'])
def set_speed(speed_value):
    global speed
    speed = float(speed_value)
    print("Speed set to " + str(speed))
    return ('', 204)


@app.route("/save_program/<programName>", methods=['GET', 'POST'])
def save_program(programName):
    global programStorage
    print(programStorage)
    with open("programs/+" + programName, "wb") as f:
        pickle.dump(programStorage, f)
    print("Saved as: " + programName)
    programStorage = []
    getPage()
    return ('', 204)


def load_dropdown():
    global programs
    programs = os.listdir("programs")
    programs = [program[1:] for program in programs]
    print(programs)
    print("Dropdown loaded")


@app.route("/run_program/<programName>", methods=['GET', 'POST'])
def run_program(programName):
    with open("programs/+" + programName, "rb") as f:
        programStorage = pickle.load(f)
    print(programStorage)
    for i in range(0, len(programStorage), 2):
        motors.step(programStorage[i], programStorage[i + 1])
        sleep(speed)
    motors.off()
    return ('', 204)


@app.route('/radar_img/', methods=['GET', 'POST'])
def radar_img():
    pic, data = radar.scan()
    # return send_file(pic, as_attachment=True, attachment_filename='radar_img', mimetype='image/png')
    return send_file(pic, mimetype='image/png')


if __name__ == "__main__":
    app.run(host='0.0.0.0', threaded=True)

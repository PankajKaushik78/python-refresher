import socketio
import time
import os

LOGFILE = '/home/pankaj/Desktop/Dev/python-refresher/IO/socketio/logfile'
BACKGROUND_TASK_STARTED = False

sio = socketio.Server()
app = socketio.WSGIApp(sio, static_files={
    '/': './public/'
})

@sio.event
def connect(sid, environ):
    global BACKGROUND_TASK_STARTED
    print(sid, "connected")
    send_intial_lines(sid)
    if not BACKGROUND_TASK_STARTED:
        sio.start_background_task(send_updated_lines)
        BACKGROUND_TASK_STARTED = True

@sio.event
def disconnect(sid):
    print(sid, "disconnected")

def send_updated_lines():
    print("[Watching Log file...]")
    last_modified = os.path.getmtime(LOGFILE)
    with open('logfile', 'r') as file:
        file.seek(0, 2)
        while True:
            modify_time = os.path.getmtime(LOGFILE)
            if(last_modified < modify_time):
                last_modified = modify_time
                updated_lines = file.readlines()
                for line in updated_lines:
                    sio.emit('last_n_lines', { 'result': line })
            time.sleep(3)



def send_intial_lines(sid):
    with open('logfile', 'rb') as file:
        # last_n_lines = get_last_n_lines(file, 10)
        # for line in last_n_lines:
        #     sio.emit('last_n_lines', { 'result': line }, to=sid)
        last_n_lines = tail(file, 10)
        print(last_n_lines)
        sio.emit('last_n_lines', {'result': last_n_lines})


def get_last_n_lines(file, lines = 10):
    file.seek(0, 2)
    fsize = file.tell()
    file.seek(max(fsize-1024, 0), 0)
    lines = file.readlines()
    return lines


def tail(f, lines=10):
    total_lines_wanted = lines

    BLOCK_SIZE = 1024
    f.seek(0, 2)
    block_end_byte = f.tell()
    lines_to_go = total_lines_wanted
    block_number = -1
    blocks = []
    while lines_to_go > 0 and block_end_byte > 0:
        if (block_end_byte - BLOCK_SIZE > 0):
            f.seek(block_number*BLOCK_SIZE, 2)
            blocks.append(f.read(BLOCK_SIZE))
        else:
            f.seek(0,0)
            blocks.append(f.read(block_end_byte))
        lines_found = blocks[-1].count(b'\n')
        lines_to_go -= lines_found
        block_end_byte -= BLOCK_SIZE
        block_number -= 1
    all_read_text = b''.join(reversed(blocks))
    return b'\n'.join(all_read_text.splitlines()[-total_lines_wanted:])




# gunicorn -k eventlet -w 1 --reload app:app
# Stop process at port -> fuser 8000/tcp after this -> fuser -k 8000/tcp
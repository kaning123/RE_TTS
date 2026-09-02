from .Main.Server.boot import boot,boot_webui
from .Main.Server.Thread_Killer import kill_thread, kill_threads
import threading
import rpyc
import time
import edge_tts
from edge_tts import VoicesManager
import os 
import uuid
MERGE_DIR_TXT = os.path.join
MY_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = MERGE_DIR_TXT(MY_DIR, "Temp")
def Base_TTS(txt,):
    comm = edge_tts.Communicate(txt,)
    comm.save_sync(MERGE_DIR_TXT(TEMP_DIR, f"{str(uuid.uuid4())}.wav"))
    return MERGE_DIR_TXT(TEMP_DIR, f"{str(uuid.uuid4())}.wav")

def main(*args, **kwargs):
    print("Starting RE_TTS Server...")
    print(f"args:{args}")
    print(f"kwargs:{kwargs}")

ThreadPool = []
def conn_await():
    err_times = 0
    try:
        time.sleep(1)
        return rpyc.connect("localhost", 5418)
    except Exception as e:
        print(f"Time {err_times} failed to connect to server: {e}")
        err_times += 1
        return conn_await()

connection = None
def connect():
    global connection
    connection = conn_await()

def boot_():
    t = threading.Thread(target=boot)
    t.start()
    ThreadPool.append(t)
    return t,len(ThreadPool)-1

def stop(tid):
    kill_thread(ThreadPool[tid])

def stop_all():
    kill_threads(ThreadPool)

def SetVoice(VoicePth):
    if connection is None:
        connect()
        return SetVoice(VoicePth)

    return connection.root.get_vc(VoicePth)

def VoiceChangeSingle(AudioWav,
                      IndexPath,
                      retry=3,
                      depth=0):
    if connection is None:
        connect()
        return VoiceChangeSingle(AudioWav,IndexPath)
    
    try:
        ret = connection.root.vc_single__(AudioWav, IndexPath)
    except KeyboardInterrupt as e:
        raise e
    except Exception as e:
        depth += 1
        return VoiceChangeSingle(AudioWav,IndexPath,retry,depth)

def TTS(txts:list[str],IndexPath:str,Retry=3,Depth=0):
    ''''''
    bases = []
    for txt in txts:
        Base = Base_TTS(txt)
        bases.append(Base)
    Outputs = []
    for base in bases:
        Outputs.append(VoiceChangeSingle(base,IndexPath,Retry,Depth))
    return Outputs
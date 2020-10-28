import wave
import threading
from os import remove,mkdir,listdir
from os.path import exists,splitext,basename,join
from datetime import datetime
from time import sleep
from shutil import rmtree
import pyaudio
from PIL import ImageGrab
from numpy import array

import cv2
from moviepy.editor import *

CHUNK_SIZE = 1024
CHANNELS = 2
FORMAT = pyaudio.paInt16
RATE = 48000
allowRecording = True

def record_audio():
    p = pyaudio.PyAudio()
    # 等待摄像头启动好 然后大家一起等3秒开始录制
    event.wait()
    sleep(3)
    #创建输入流
    stream = p.open(format = FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE
    )
    wf = wave.open(audio_filename,'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.serframerate(RATE)
    while allowRecording:
        # 从录音设备读取数据，直接写入wav文件
        data = stream.read(CHUNK_SIZE)
        wf.writeframes(data)
    wf.close()
    stream.stop_stream()
    stream.close()
    p.terminate()


def record_screen():
    #录制屏幕
    #等待摄像头启动好，然后大家一起等3秒开始录制
    event.wait()
    sleep(3)
    im = ImageGrab.grab()
    video = cv2.videoWrite(screen_video_filename,cv2.VideoWrite_fourcc(*'XVID'),25,im.size)
    while allowRecording:
        im = ImageGrab.grab()
        im = cv2.cvtColor(array(im),cv2.COLOR_RGB2BGR)
        video.write(im)
    video.release()

def record_webcam():
    # 参数0表示笔记本自带摄像头
    cap = cv2.VideoCapture(0)
    # 启动好摄像头，发出通知，大家一起等三秒开始录
    event.set()
    sleep(3)
    aviFile = cv2.VideoWrite(webcam_video_filename,cv2.VideoWriter_fourcc(*'MJPG'),25,(640,480))
    while allowRecording and cap.isOpened():
        #捕捉当前图像，ret=True表示成功，False 表示失败
        ret,frame = cap.read()
        if ret:
            aviFile.write(frame)
    aviFile.release()
    cap.release()
now = str(datetime.now())[:19].replace(':',"_")
audio_filename = f'{now}.mp3'
webcam_video_filename=f't{now}.avi'
screen_video_filename = f'tt{now}.avi'
video_filename = f'{now}.avi'
#创建两个线程，分别录音和录屏
t1 = threading.Thread(target=record_audio)
t2 = threading.Thread(target=record_screen)
t3 = threading.Thread(target=record_webcam)
#创建时间，用于多个线程同步，等待摄像头准备以后在一起等三秒开始录制
event = threading.Event()
event.clear()
for t in (t1,t2,t3):
    t.start()
#等待摄像头准备好，提示用户3秒钟以后开始录制
event.wait()
print("三秒后开始录制，按q键结束录制")
while True:
    if input()=='q':
        break
allowRecording = False
for t in (t1,t2,t3):
    t.join()
# 把录制的音频和屏幕截图合成为视频文件
audio  = AudioFileClip(audio_filename)
video1 = VideoFileClip(screen_video_filename)
ratio1 = audio.duration/video1.duration
video1 = (video1.fl_time(lamnda t: t/ratio1,apply_to=['video'])
        .set_end(audio.duration))
video2 = VideoFileClip(webcam_video_filename)
ratio2 = audio.duration/video2.duration
video2 = (video2.fl_time(lamnda t: t/ratio2,apply_to=['video'])
        .set_end(audio.duration)
        .resize((320,240))
        .set_position(('right','bottom')))
video = CompositeVideoClip([video1,video2]).set_audio(audio)
video.write_videofile(video_filename,codec='libx264',fps=25)
#删除临时音频文件和视频文件
remove(audio_filename)
remove(screen_video_filename)
remove(webcam_video_filename)








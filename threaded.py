import argparse
import os
import cv2
from threading import Thread
import multiprocessing
import queue

# from CountsPerSec import CountsPerSec

class VideoGet:
    """
    Class that continuously gets frames from a VideoCapture object
    with a dedicated thread.
    """

    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        self.q = queue.Queue()
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False

    def start(self):    
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        while not self.stopped:
            if not self.grabbed:
                self.stop()
            else:
                ret, frame = self.stream.read()
                if not ret:
                    self.stopped = True
                if not self.q.empty():
                    try:
                        self.q.get_nowait()
                    except queue.Empty:
                        pass
                self.q.put(frame)
                self.frame = frame
                # (self.grabbed, self.frame) = self.stream.read()


    def stop(self):
        self.stopped = True

    def read(self):
        return self.q.get()

class VideoShow:
    """
    Class that continuously shows a frame using a dedicated thread.
    """

    def __init__(self,camera_id, frame=None):
        self.frame = frame
        self.camera_id = camera_id
        self.stopped = False

    def start(self):
        Thread(target=self.show, args=()).start()
        return self

    def show(self):
        while not self.stopped:
            # print(self.camera_id)
            cv2.imshow(self.camera_id , self.frame)
            if cv2.waitKey(1) == ord("q"):
                self.stopped = True

    def stop(self):
        self.stopped = True

def putIterationsPerSec(frame, iterations_per_sec):
    """
    Add iterations per second text to lower-left corner of a frame.
    """

    cv2.putText(frame, "{:.0f} iterations/sec".format(iterations_per_sec),
        (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255))
    return frame

def noThreading(source=0):
    """Grab and show video frames without multithreading."""

    cap = cv2.VideoCapture(source)
    # cps = CountsPerSec().start()

    while True:
        grabbed, frame = cap.read()
        if not grabbed or cv2.waitKey(1) == ord("q"):
            break

        # frame = putIterationsPerSec(frame, cps.countsPerSec())
        cv2.imshow("Video", frame)
        # cps.increment()

def threadVideoGet(source=0):
    """
    Dedicated thread for grabbing video frames with VideoGet object.
    Main thread shows video frames.
    """

    video_getter = VideoGet(source).start()
    # cps = CountsPerSec().start()

    while True:
        if (cv2.waitKey(1) == ord("q")) or video_getter.stopped:
            video_getter.stop()
            break

        frame = video_getter.frame
        # frame = putIterationsPerSec(frame, cps.countsPerSec())
        cv2.imshow("Video", frame)
        # cps.increment()

def threadVideoShow(source=0):
    """
    Dedicated thread for showing video frames with VideoShow object.
    Main thread grabs video frames.
    """

    cap = cv2.VideoCapture(source)
    (grabbed, frame) = cap.read()
    video_shower = VideoShow(frame).start()
    # cps = CountsPerSec().start()

    while True:
        (grabbed, frame) = cap.read()
        if not grabbed or video_shower.stopped:
            video_shower.stop()
            break

        # frame = putIterationsPerSec(frame, cps.countsPerSec())
        video_shower.frame = frame
        # cps.increment()

def threadBoth(source, camera_id):
    """
    Dedicated thread for grabbing video frames with VideoGet object.
    Dedicated thread for showing video frames with VideoShow object.
    Main thread serves only to pass frames between VideoGet and
    VideoShow objects/threads.
    """

    video_getter = VideoGet(source).start()
    print(camera_id)
    video_shower = VideoShow( camera_id, video_getter.frame).start()
    # cps = CountsPerSec().start()

    while True:
        if video_getter.stopped or video_shower.stopped:
            video_shower.stop()
            video_getter.stop()
            break

        frame = video_getter.frame
        # frame = putIterationsPerSec(frame, cps.countsPerSec())
        video_shower.frame = frame
        # cps.increment()

def f1(props):
 
    threadBoth("rtsp://freja.hiof.no:1935/rtplive/_definst_/hessdalen02.stream", camera_id=props)

if __name__ == '__main__':
    processes = []
    cameras = [
        "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov",
        "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov",
        "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov",
        "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov",

        "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov",
        "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov",
        "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov",
        "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov",
         "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov",

    ]

    with multiprocessing.Manager() as manager:
        print("MngrPid: " + str(manager._process.ident))
        i=0
        for camera in cameras:
            i = i+1
            p = multiprocessing.Process(target=f1, args=(str(i)))
            processes.append(p)
            p.start()

        for process in processes:
            process.join()

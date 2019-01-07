# RPi Meteor Station
# Copyright (C) 2019
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function, division, absolute_import

import time
import datetime
import logging
from multiprocessing import Process, Event
import os
import shutil
import subprocess
import glob

from RMS.Misc import ping


"""
The directory for temporary video file storage is a tmpfs RAM directory created with this entry in the /etc/fstab:
tmpfs   /rmstmp    tmpfs    defaults,noatime,nosuid,mode=0777,size=100m    0 0
"""
TMP_VIDEO_DIR =  '/tmp/' # Videos are captured to this temporary RAM disk
VIDEO_EXTENSION = '.mkv'    # Video file extension '.h264' |'.mp4' | '.mkv' | '.avi'
VIDEO_FILE_PREFIX = 'RH_'

# Get the logger from the main module
log = logging.getLogger("logger")


class VideoRecorder(Process):
    """ Capture video to disk.
    """

    running = False

    def __init__(self, data_dir, config, video_segment_time=60):
        """ Record video from camera device after startCapture is called.

        Arguments:
            data_dir: string containing the data directory in which to store the video files
            config: object containing the RMS configuration

        Keyword arguments:
            video_segment_time: int containing the required video segment time in seconds. Default is 60 seconds
        """

        super(VideoRecorder, self).__init__()

        self.data_dir = data_dir
        self.config = config
        self.video_segment_time = video_segment_time

        self.stationID = self.config.stationID

        # self.video_cmd = 'gst-launch-1.0 rtspsrc location=' + RTSP_STREAM + ' ! rtpjitterbuffer ! rtph264depay ! h264parse ! video/x-h264 ! splitmuxsink location=' + TMP_VIDEO_DIR + 'video%06d.mkv max-size-time=' + str(int(self.video_segment_time*1e9)) + ' max-size-bytes=100000000 muxer=matroskamux'
        self.video_cmd = self.config.video_recorder
        log.info("Video capture command: " + self.video_cmd)


    def startCapture(self):
        """ Start video capture.

        """

        self.exit = Event()
        self.start()


    def stopCapture(self):
        """ Stop capture.
        """

        self.exit.set()

        time.sleep(1)

        log.info("Joining capture...")

        # Wait for the capture to join for 60 seconds, then terminate
        for i in range(60):
            if self.is_alive():
                time.sleep(1)
            else:
                break

        if self.is_alive():
            log.info('Terminating capture...')
            self.terminate()


    def initVideoDevice(self):
        """ Initialize the video device. """

        # Init the video device
        log.info("Initializing the video recorder...")

        # Clean up any old video files from the ram disk
        video_file_list = sorted(glob.glob(TMP_VIDEO_DIR + '/*' + VIDEO_EXTENSION), key=os.path.getatime)
        for video_file in video_file_list :
            os.remove(video_file)



    def store_video_files(self) :
        """ Look for newly completed video files in the temporary video file disk,
        and copy them to the RMS CapturedFiles directory """

        # Get the list of video files on the temporary RAM disk
        video_file_list = sorted(glob.glob(TMP_VIDEO_DIR + '/*' + VIDEO_EXTENSION), key=os.path.getatime)
        while len(video_file_list) > 1 :
            video_file = video_file_list.pop(0)

            # Ensure that writing has completed for this video file
            if (os.path.getmtime(video_file) + 5) > time.time() :
                continue

            # Get the creation time (atime) of the file and copy the timestamped video file to the capture directory
            ts = os.path.getatime(video_file)
            filename, file_extension = os.path.splitext(video_file)
            new_file_name = VIDEO_FILE_PREFIX + self.stationID.upper() + datetime.datetime.utcfromtimestamp(ts).strftime('_%Y%m%d_%H%M%S_%f' + file_extension)
            print("Copying video " + video_file +  " to " + self.data_dir + '/' + new_file_name)
            shutil.copy2(video_file, self.data_dir + '/' + new_file_name)

            # Remove the temporary video file from the RAM disk
            os.remove(video_file)


    def run(self):
        """ Capture video.
        """

        # Init the video device
        self.initVideoDevice()

        # Run until stopped from the outside
        while not self.exit.is_set():

            # Start the ffmpeg subprocess with timezone GMT
            args = self.video_cmd.split()
            log.info("Running subprocess: " + self.video_cmd)
            p = subprocess.Popen(args, env={'TZ': 'GMT'})

            # Wait while the video streamer process is still running and exit not requested
            log.info("Waiting for process " + str(p.pid) + " to complete")
            while p.poll() is None and not self.exit.is_set() :
                self.store_video_files()
                time.sleep(2)

            # Terminate the video streamer process if it's still running
            if p is None : pass
            elif p.poll() is None :
                log.info("Terminating process " + str(p.pid))
                p.terminate()
                p.wait()
                log.info("Process terminated")

            time.sleep(10)

        log.info('Video recording completed!')


# Main program - for testing purposes
if __name__ == "__main__":

    # Load the configuration file
    import RMS.ConfigReader as cr
    config = cr.parse(".config")

    capture_dir =  os.path.expanduser('~/RMS_data/') # Captures are stored to this directory

    video_recorder = VideoRecorder(capture_dir, config)
    video_recorder.startCapture()

    time.sleep(3600)

    video_recorder.stopCapture()

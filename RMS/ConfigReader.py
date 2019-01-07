# RPi Meteor Station
# Copyright (C) 2016  Dario Zubovic, Denis Vida
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

import os
import sys

try:
    # Python 3
    from ConfigParser import RawConfigParser, NoOptionError

except:
    # Python 3
    from configparser import RawConfigParser, NoOptionError



def choosePlatform(win_conf, rpi_conf, linux_pc_conf):
    """ Choose the setting depending on if this is running on the RPi or a Linux PC. """

    # Check if running on Windows
    if 'win' in sys.platform:
        return win_conf

    else:

        if 'arm' in os.uname()[4]:
            return rpi_conf

        else:
            return linux_pc_conf



class Config:
    def __init__(self):

        ##### System
        self.stationID = "XX0001"
        self.latitude = 0
        self.longitude = 0
        self.elevation = 0
        self.cams_code = 0

        ##### Capture
        self.deviceID = 0

        self.width = 1280
        self.height = 720
        self.width_device = self.width
        self.height_device = self.height
        self.fps = 25.0

        self.report_dropped_frames = False

        # Region of interest, -1 disables the range
        self.roi_left = -1
        self.roi_right = -1
        self.roi_up = -1
        self.roi_down = -1

        self.brightness = 0
        self.contrast = 0

        self.bit_depth = 8
        self.gamma = 1.0

        self.ff_format = 'fits'

        self.fov_w = 64.0
        self.fov_h = 35.0
        self.deinterlace_order = -2
        self.mask_file = "mask.bmp"

        self.data_dir = "~/RMS_data"
        self.captured_dir = "CapturedFiles"
        self.archived_dir = "ArchivedFiles"


        ##### Upload

        # Flag determining if uploading is enabled or not
        self.upload_enabled = True

        # Address of the upload server
        self.hostname = ''

        # SSH port
        self.host_port = 22

        # Location of the SSH private key
        self.rsa_private_key = os.path.expanduser("~/.ssh/id_rsa")

        # Name of the file where the upload queue will be stored
        self.upload_queue_file = "FILES_TO_UPLOAD.inf"

        # Directory on server where the files will be uploaded to
        self.remote_dir = 'files'


        ##### Weave compilation arguments
        self.extra_compile_args = ["-O3"]

        ##### FireballDetection
        self.f = 16                    # subsampling factor
        self.max_time = 25             # maximum time for line finding

        # params for Extractor.findPoints()
        self.white_avg_level = 220     # ignore images which have the average frame above this level
        self.min_level = 40            # ignore pixel if below this level
        self.min_pixels = 8            # minimum number of pixels required to add event point
        self.k1 = 4                    # k1 factor for thresholding
        self.j1 = 5                    # absolute levels above average in thresholding
        self.max_points_per_frame = 30 # ignore frame if there are too many points in it (ie. flare)
        self.max_per_frame_factor = 10 # multiplied with median number of points for flare detection
        self.max_points = 190          # if there are too many points in total after flare removal, randomize them
        self.min_frames = 4            # minimum number of frames

        # params for Extractor.testPoints()
        self.min_points = 4            # minimum number of event points

        # params for Extractor.extract()
        self.before = 0.15             # percentage of frames to extrapolate before detected start of meteor trail
        self.after = 0.3               # percentage of frames to extrapolate after detected end of meteor trail
        self.limitForSize = 0.90
        self.minSize = 40
        self.maxSize = 192

        # params for Grouping3D
        self.distance_threshold = 4900  # maximum distance between the line and the point to be takes as a part of the same line
        self.gap_threshold = 16900      # maximum allowed gap between points
        self.line_minimum_frame_range = 3   # minimum range of frames that a line should cover (eliminates flash detections)
        self.line_distance_const = 4   # constant that determines the influence of average point distance on the line quality
        self.point_ratio_threshold = 0.7# ratio of how many points must be close to the line before considering searching for another line
        self.max_lines = 5             # maximum number of lines

        ##### MeteorDetection

        # KHT detection parameters
        self.ff_min_stars = 5

        self.k1_det = 1.5 # weight for stddev in thresholding for faint meteor detection
        self.j1_det = 9 # absolute levels above average in thresholding for faint meteor detection
        self.max_white_ratio = 0.07 # maximum ratio of white to all pixels on a thresholded image (used to avoid searching on very messed up images)
        self.time_window_size = 64 # size of the time window which will be slided over the time axis
        self.time_slide = 32 # subdivision size of the time axis (256 will be divided into 256/time_slide parts)
        self.max_lines_det = 30 # maximum number of lines to be found on the time segment with KHT
        self.line_min_dist = 40 # Minimum distance between KHT lines in Cartesian space to merge them (used for merging similar lines after KHT)
        self.stripe_width = 20 # width of the stripe around the line
        self.kht_lib_path = "build/lib.linux-x86_64-2.7/kht_module.so" # path to the compiled KHT module

        # 3D line finding for meteor detection
        self.max_points_det = 600 # maximumum number of points during 3D line search in faint meteor detection (used to minimize runtime)
        self.distance_threshold_det = 50**2 # maximum distance between the line and the point to be takes as a part of the same line
        self.gap_threshold_det = 500**2 # maximum allowed gap between points
        self.min_pixels_det = 10 # minimum number of pixels in a strip
        self.line_minimum_frame_range_det = 4 # minimum number of frames per one detection
        self.line_distance_const_det = 4 # constant that determines the influence of average point distance on the line quality
        self.max_time_det = 10 # maximum time in seconds for which line finding algorithm can run

        # 3D line merging parameters
        self.vect_angle_thresh = 20 # angle similarity between 2 lines in a stripe to be merged
        self.frame_extension = 3 # how many frames to check during centroiding before and after the initially determined frame range

        # Centroid filtering parameters
        self.centroids_max_deviation = 2 # maximum deviation of a centroid point from a LSQ fitted line (if above max, it will be rejected)
        self.centroids_max_distance =  30 # maximum distance in pixels between centroids (used for filtering spurious centroids)

        # Angular veloicty filtering parameter - detections slower or faster than these angular velocities
        # will be rejected (deg/s)
        self.ang_vel_min = 0.5
        self.ang_vel_max = 35.0


        ##### StarExtraction

        # Extraction parameters
        self.max_global_intensity = 150 # maximum mean intensity of an image before it is discared as too bright
        self.border = 10 #  apply a mask on the detections by removing all that are too close to the given image border (in pixels)
        self.neighborhood_size = 10 # size of the neighbourhood for the maximum search (in pixels)
        self.intensity_threshold = 5 # a threshold for cutting the detections which are too faint (0-255)
        self.max_stars = 200 # An upper limit on number of stars before the PSF fitting (more than that would take too long to process)

        # PSF fit and filtering
        self.segment_radius = 4 # radius (in pixels) of image segment around the detected star on which to perform the fit
        self.roundness_threshold = 0.5 # minimum ratio of 2D Gaussian sigma X and sigma Y to be taken as a stars (hot pixels are narrow, while stars are round)
        self.max_feature_ratio = 0.8 # maximum ratio between 2 sigma of the star and the image segment area


        ##### Calibration
        self.use_flat = True
        self.flat_file = 'flat.bmp'
        self.flat_min_imgs = 20

        self.star_catalog_path = 'Catalogs'
        self.star_catalog_file = 'gaia_dr2_mag_11.5.npy'
        self.star_catalog_band_ratios = [0.0, 1.0, 0.0, 0.0]

        self.platepar_name = 'platepar_cmn2010.cal'

        # Name of the platepar file on the server
        self.platepar_remote_name = 'platepar_latest.cal'
        self.remote_platepar_dir = 'platepars'

        self.catalog_extraction_radius = 40.0 #deg
        self.catalog_mag_limit = 4.5

        self.calstars_files_N = 400 # How many calstars FF files to evaluate

        self.calstars_min_stars = 500 # Minimum number of stars to use

        self.dist_check_threshold = 0.33 # Minimum acceptable calibration residual (px)
        self.dist_check_quick_threshold = 0.4 # Threshold for quick recalibration

        self.stars_NN_radius = 10.0 # deg
        self.refinement_star_NN_radius = 0.125 #deg
        self.rotation_param_range = 5.0 # deg
        self.min_matched_stars = 7
        self.max_initial_iterations = 20

        self.min_estimation_value = 0.4 # Minimum estimation parameter when to stop the iteration


        ##### Thumbnails
        self.thumb_bin =  4
        self.thumb_stack   =  5
        self.thumb_n_width = 10


def normalizeParameter(param, config):
    """ Normalize detection parameter to be size independent.

    @param param: parameter to be normalized

    @return: normalized param
    """

    return param*config.width/config.f*config.height/config.f/(720*576)


def parse(filename):

    try:
        # Python 3
        parser = RawConfigParser(inline_comment_prefixes=(";"))

    except:
        # Python 2
        parser = RawConfigParser()

    parser.read(filename)

    config = Config()

    parseAllSections(config, parser)

    return config



def parseAllSections(config, parser):
    parseSystem(config, parser)
    parseCapture(config, parser)
    parseBuildArgs(config, parser)
    parseUpload(config, parser)
    parseCompression(config, parser)
    parseFireballDetection(config, parser)
    parseMeteorDetection(config, parser)
    parseStarExtraction(config, parser)
    parseCalibration(config, parser)
    parseThumbnails(config, parser)



def parseSystem(config, parser):

    section= "System"
    if not parser.has_section(section):
        raise RuntimeError("Not configured!")

    try:
        config.stationID = parser.get(section, "stationID")
    except NoOptionError:
        raise RuntimeError("Not configured!")


    if parser.has_option(section, "latitude"):
        config.latitude = parser.getfloat(section, "latitude")

    if parser.has_option(section, "longitude"):
        config.longitude = parser.getfloat(section, "longitude")

    if parser.has_option(section, "elevation"):
        config.elevation = parser.getfloat(section, "elevation")


    if parser.has_option(section, "cams_code"):
        config.cams_code = parser.getint(section, "cams_code")



def parseCapture(config, parser):
    section = "Capture"

    if not parser.has_section(section):
        return

    if parser.has_option(section, "data_dir"):

        config.data_dir = parser.get(section, "data_dir")

        # Parse the home folder appropriately
        if config.data_dir[0] == '~':

            config.data_dir = config.data_dir.replace('~', '')

            # Remove the directory separator if it is at the beginning of the path
            if config.data_dir[0] == os.sep:
                config.data_dir = config.data_dir[1:]

            config.data_dir = os.path.join(os.path.expanduser('~'), config.data_dir)


    if parser.has_option(section, "captured_dir"):
        config.captured_dir = parser.get(section, "captured_dir")

    if parser.has_option(section, "archived_dir"):
        config.archived_dir = parser.get(section, "archived_dir")

    if parser.has_option(section, "width"):
        config.width = parser.getint(section, "width")

        # Save original input image size
        config.width_device = config.width


    if parser.has_option(section, "height"):
        config.height = parser.getint(section, "height")

        # Save original input image size
        config.height_device = config.height


    if parser.has_option(section, "report_dropped_frames"):
        config.report_dropped_frames = parser.getboolean(section, "report_dropped_frames")


    # Parse the region of interest boundaries
    if parser.has_option(section, "roi_left"):
        config.roi_left = parser.getint(section, "roi_left")

    if parser.has_option(section, "roi_right"):
        config.roi_right = parser.getint(section, "roi_right")

    if parser.has_option(section, "roi_up"):
        config.roi_up = parser.getint(section, "roi_up")

    if parser.has_option(section, "roi_down"):
        config.roi_down = parser.getint(section, "roi_down")


    # Compute the width and the height from the region of interest, if given
    if config.roi_left > config.roi_right:
        config.roi_left, config.roi_right = config.roi_right, config.roi_left

    if (config.roi_left < 0) or (config.roi_left > config.width):
        config.roi_left = 0

    if (config.roi_right < 0) or (config.roi_right > config.width):
        config.roi_right = config.width

    # Choose the correct ROI for up/down
    if config.roi_up > config.roi_down:
        config.roi_up, config.roi_down = config.roi_down, config.roi_up

    if (config.roi_up < 0) or (config.roi_up > config.height):
        config.roi_up = 0

    if (config.roi_down < 0) or (config.roi_down > config.height):
        config.roi_down = config.height


    # Recompute the width and height from ROI
    config.width = config.roi_right - config.roi_left
    config.height = config.roi_down - config.roi_up


    if parser.has_option(section, "brightness"):
        config.brightness = parser.getint(section, "brightness")

    if parser.has_option(section, "contrast"):
        config.contrast = parser.getint(section, "contrast")

    if parser.has_option(section, "bit_depth"):
        config.bit_depth = parser.getint(section, "bit_depth")

    if parser.has_option(section, "gamma"):
        config.gamma = parser.getfloat(section, "gamma")

    if parser.has_option(section, "device"):
        config.deviceID = parser.get(section, "device")

    # Try converting the device ID to integer (meaning that it is a real device
    try:
        config.deviceID = int(config.deviceID)
    except:

        # If it fails, it's probably a RTSP stream
        pass

    if parser.has_option(section, "fps"):
        config.fps = parser.getfloat(section, "fps")

    if parser.has_option(section, "ff_format"):
        config.ff_format = parser.get(section, "ff_format")

    if parser.has_option(section, "fov_w"):
        config.fov_w = parser.getfloat(section, "fov_w")

    if parser.has_option(section, "fov_h"):
        config.fov_h = parser.getfloat(section, "fov_h")

    if parser.has_option(section, "deinterlace_order"):
        config.deinterlace_order = parser.getint(section, "deinterlace_order")

    if parser.has_option(section, "mask"):
        config.mask_file = parser.get(section, "mask")

    if parser.has_option(section, "video_recorder"):
        config.video_recorder = parser.get(section, "video_recorder")



def parseUpload(config, parser):
    section = "Upload"

    if not parser.has_section(section):
        return

    # Enable/disable upload
    if parser.has_option(section, "upload_enabled"):
        config.upload_enabled = parser.getboolean(section, "upload_enabled")

    # Address of the upload server
    if parser.has_option(section, "hostname"):
        config.hostname = parser.get(section, "hostname")

    # SSH port
    if parser.has_option(section, "host_port"):
        config.host_port = parser.getint(section, "host_port")

    # Location of the SSH private key
    if parser.has_option(section, "rsa_private_key"):
        config.rsa_private_key = os.path.expanduser(parser.get(section, "rsa_private_key"))

    # Name of the file where the upload queue will be stored
    if parser.has_option(section, "upload_queue_file"):
        config.upload_queue_file = parser.get(section, "upload_queue_file")

    # Directory on the server where the detected files will be uploaded to
    if parser.has_option(section, "remote_dir"):
        config.remote_dir = parser.get(section, "remote_dir")



def parseBuildArgs(config, parser):
    section = "Build"

    if not parser.has_section(section):
        return

    linux_pc_weave = None
    win_pc_weave = None
    rpi_weave = None

    if parser.has_option(section, "rpi_weave"):
        rpi_weave = parser.get(section, "rpi_weave").split()

    if parser.has_option(section, "linux_pc_weave"):
        linux_pc_weave = parser.get(section, "linux_pc_weave").split()

    if parser.has_option(section, "win_pc_weave"):
        win_pc_weave = parser.get(section, "win_pc_weave").split()


    # Read in the KHT library path for both the PC and the RPi, but decide which one to take based on the
    # system this is running on
    config.extra_compile_args = choosePlatform(win_pc_weave, rpi_weave, linux_pc_weave)



def parseCompression(config, parser):
    section = "Compression"
    pass



def parseFireballDetection(config, parser):
    section = "FireballDetection"

    if not parser.has_section(section):
        return

    if parser.has_option(section, "subsampling_size"):
        config.f = parser.getint(section, "subsampling_size")

    if parser.has_option(section, "max_time"):
        config.max_time = parser.getint(section, "max_time")

    if parser.has_option(section, "white_avg_level"):
        config.white_avg_level = parser.getint(section, "white_avg_level")

    if parser.has_option(section, "minimal_level"):
        config.min_level = parser.getint(section, "minimal_level")

    if parser.has_option(section, "minimum_pixels"):
        config.min_pixels = parser.getint(section, "minimum_pixels")

    if parser.has_option(section, "k1"):
        config.k1 = parser.getfloat(section, "k1")

    if parser.has_option(section, "j1"):
        config.j1 = parser.getint(section, "j1")

    if parser.has_option(section, "max_points_per_frame"):
        config.max_points_per_frame = parser.getint(section, "max_points_per_frame")

    if parser.has_option(section, "max_per_frame_factor"):
        config.max_per_frame_factor = parser.getint(section, "max_per_frame_factor")

    if parser.has_option(section, "max_points"):
        config.max_points = parser.getint(section, "max_points")

    if parser.has_option(section, "min_frames"):
        config.min_frames = parser.getint(section, "min_frames")

    if parser.has_option(section, "min_points"):
        config.min_points = parser.getint(section, "min_points")

    if parser.has_option(section, "extend_before"):
        config.before = parser.getfloat(section, "extend_before")

    if parser.has_option(section, "extend_after"):
        config.after = parser.getfloat(section, "extend_after")

    if parser.has_option(section, "min_window_size"):
        config.minSize = parser.getint(section, "min_window_size")

    if parser.has_option(section, "max_window_size"):
        config.maxSize = parser.getint(section, "max_window_size")

    if parser.has_option(section, "threshold_for_size"):
        config.limitForSize = parser.getfloat(section, "threshold_for_size")

    if parser.has_option(section, "distance_threshold"):
        config.distance_threshold = parser.getint(section, "distance_threshold")**2

    config.distance_threshold = normalizeParameter(config.distance_threshold, config)

    if parser.has_option(section, "gap_threshold"):
        config.gap_threshold = parser.getint(section, "gap_threshold")**2

    config.gap_threshold = normalizeParameter(config.gap_threshold, config)

    if parser.has_option(section, "line_minimum_frame_range"):
        config.line_minimum_frame_range = parser.getint(section, "line_minimum_frame_range")

    if parser.has_option(section, "line_distance_const"):
        config.line_distance_const = parser.getint(section, "line_distance_const")

    if parser.has_option(section, "point_ratio_threshold"):
        config.point_ratio_threshold = parser.getfloat(section, "point_ratio_threshold")

    if parser.has_option(section, "max_lines"):
        config.max_lines = parser.getint(section, "max_lines")

    if parser.has_option(section, "min_lines"):
        config.max_lines = parser.getint(section, "max_lines")



def parseMeteorDetection(config, parser):
    section = "MeteorDetection"

    if not parser.has_section(section):
        return

    if parser.has_option(section, "ff_min_stars"):
        config.ff_min_stars = parser.getint(section, "ff_min_stars")

    if parser.has_option(section, "k1"):
        config.k1_det = parser.getfloat(section, "k1")

    if parser.has_option(section, "j1"):
        config.j1_det = parser.getint(section, "j1")

    if parser.has_option(section, "max_white_ratio"):
        config.max_white_ratio = parser.getfloat(section, "max_white_ratio")

    if parser.has_option(section, "time_window_size"):
        config.time_window_size = parser.getint(section, "time_window_size")

    if parser.has_option(section, "time_slide"):
        config.time_slide = parser.getint(section, "time_slide")

    if parser.has_option(section, "max_lines_det"):
        config.max_lines_det = parser.getint(section, "max_lines_det")

    if parser.has_option(section, "line_min_dist"):
        config.line_min_dist = parser.getint(section, "line_min_dist")

    if parser.has_option(section, "distance_threshold_det"):
        config.distance_threshold_det = parser.getint(section, "distance_threshold_det")**2

    config.distance_threshold_det = normalizeParameter(config.distance_threshold_det, config)

    if parser.has_option(section, "gap_threshold_det"):
        config.gap_threshold_det = parser.getint(section, "gap_threshold_det")**2

    config.gap_threshold_det = normalizeParameter(config.gap_threshold_det, config)

    if parser.has_option(section, "min_pixels_det"):
        config.min_pixels_det = parser.getint(section, "min_pixels_det")

    if parser.has_option(section, "line_minimum_frame_range_det"):
        config.line_minimum_frame_range_det = parser.getint(section, "line_minimum_frame_range_det")

    if parser.has_option(section, "line_distance_const_det"):
        config.line_distance_const_det = parser.getint(section, "line_distance_const_det")

    if parser.has_option(section, "max_time_det"):
        config.max_time_det = parser.getint(section, "max_time_det")

    if parser.has_option(section, "stripe_width"):
        config.stripe_width = parser.getint(section, "stripe_width")

    if parser.has_option(section, "max_points_det"):
        config.max_points_det = parser.getint(section, "max_points_det")


    # Read in the KHT library path for both the PC and the RPi, but decide which one to take based on the
    # system this is running on
    rpi_kht_lib_path = None
    linux_pc_kht_lib_path = None
    win_pc_kht_lib_path = None

    if parser.has_option(section, "rpi_kht_lib_path"):
        rpi_kht_lib_path = parser.get(section, "rpi_kht_lib_path")

    if parser.has_option(section, "linux_pc_kht_lib_path"):
        linux_pc_kht_lib_path = parser.get(section, "linux_pc_kht_lib_path")

    if parser.has_option(section, "win_pc_kht_lib_path"):
        win_pc_kht_lib_path = parser.get(section, "win_pc_kht_lib_path")

    config.kht_lib_path = choosePlatform(win_pc_kht_lib_path, rpi_kht_lib_path, linux_pc_kht_lib_path)



    if parser.has_option(section, "vect_angle_thresh"):
        config.vect_angle_thresh = parser.getint(section, "vect_angle_thresh")

    if parser.has_option(section, "frame_extension"):
        config.frame_extension = parser.getint(section, "frame_extension")


    if parser.has_option(section, "centroids_max_deviation"):
        config.centroids_max_deviation = parser.getfloat(section, "centroids_max_deviation")

    if parser.has_option(section, "centroids_max_distance"):
        config.centroids_max_distance = parser.getint(section, "centroids_max_distance")


    if parser.has_option(section, "ang_vel_min"):
        config.ang_vel_min = parser.getfloat(section, "ang_vel_min")

    if parser.has_option(section, "ang_vel_max"):
        config.ang_vel_max = parser.getfloat(section, "ang_vel_max")




def parseStarExtraction(config, parser):
    section = "StarExtraction"

    if not parser.has_section(section):
        return

    if parser.has_option(section, "max_global_intensity"):
        config.max_global_intensity = parser.getint(section, "max_global_intensity")

    if parser.has_option(section, "border"):
        config.border = parser.getint(section, "border")

    if parser.has_option(section, "neighborhood_size"):
        config.neighborhood_size = parser.getint(section, "neighborhood_size")

    if parser.has_option(section, "intensity_threshold"):
        config.intensity_threshold = parser.getint(section, "intensity_threshold")

    if parser.has_option(section, "max_stars"):
        config.max_stars = parser.getint(section, "max_stars")

    if parser.has_option(section, "segment_radius"):
        config.segment_radius = parser.getint(section, "segment_radius")

    if parser.has_option(section, "roundness_threshold"):
        config.roundness_threshold = parser.getfloat(section, "roundness_threshold")

    if parser.has_option(section, "max_feature_ratio"):
        config.max_feature_ratio = parser.getfloat(section, "max_feature_ratio")



def parseCalibration(config, parser):
    section = "Calibration"

    if not parser.has_section(section):
        return

    if parser.has_option(section, "use_flat"):
        config.use_flat = parser.getboolean(section, "use_flat")

    if parser.has_option(section, "flat_file"):
        config.flat_file = parser.get(section, "flat_file")

    if parser.has_option(section, "flat_min_imgs"):
        config.flat_min_imgs = parser.getint(section, "flat_min_imgs")

    if parser.has_option(section, "star_catalog_path"):
        config.star_catalog_path = parser.get(section, "star_catalog_path")

    if parser.has_option(section, "star_catalog_file"):
        config.star_catalog_file = parser.get(section, "star_catalog_file")

    if parser.has_option(section, "star_catalog_band_ratios"):

        ratios_str = parser.get(section, "star_catalog_band_ratios")

        # Parse the ratios as a list of floats
        config.star_catalog_band_ratios = list(map(float, ratios_str.split(',')))


    if parser.has_option(section, "platepar_name"):
        config.platepar_name = parser.get(section, "platepar_name")

    if parser.has_option(section, "platepar_remote_name"):
        config.platepar_remote_name = parser.get(section, "platepar_remote_name")

    if parser.has_option(section, "remote_platepar_dir"):
        config.remote_platepar_dir = parser.get(section, "remote_platepar_dir")

    if parser.has_option(section, "catalog_extraction_radius"):
        config.catalog_extraction_radius = parser.getfloat(section, "catalog_extraction_radius")

    if parser.has_option(section, "catalog_mag_limit"):
        config.catalog_mag_limit = parser.getfloat(section, "catalog_mag_limit")

    if parser.has_option(section, "calstars_files_N"):
        config.calstars_files_N = parser.getint(section, "calstars_files_N")

    if parser.has_option(section, "dist_check_threshold"):
        config.dist_check_threshold = parser.getfloat(section, "dist_check_threshold")

    if parser.has_option(section, "dist_check_quick_threshold"):
        config.dist_check_quick_threshold = parser.getfloat(section, "dist_check_quick_threshold")

    if parser.has_option(section, "calstars_min_stars"):
        config.calstars_min_stars = parser.getint(section, "calstars_min_stars")

    if parser.has_option(section, "stars_NN_radius"):
        config.stars_NN_radius = parser.getfloat(section, "stars_NN_radius")

    if parser.has_option(section, "refinement_star_NN_radius"):
        config.refinement_star_NN_radius = parser.getfloat(section, "refinement_star_NN_radius")

    if parser.has_option(section, "rotation_param_range"):
        config.rotation_param_range = parser.getfloat(section, "rotation_param_range")

    if parser.has_option(section, "min_matched_stars"):
        config.min_matched_stars = parser.getint(section, "min_matched_stars")

    if parser.has_option(section, "max_initial_iterations"):
        config.max_initial_iterations = parser.getint(section, "max_initial_iterations")

    if parser.has_option(section, "min_estimation_value"):
        config.min_estimation_value = parser.getfloat(section, "min_estimation_value")



def parseThumbnails(config, parser):
    section = "Thumbnails"

    if not parser.has_section(section):
        return


    if parser.has_option(section, "thumb_bin"):
        config.thumb_bin = parser.getint(section, "thumb_bin")

    if parser.has_option(section, "thumb_stack"):
        config.thumb_stack = parser.getint(section, "thumb_stack")

    if parser.has_option(section, "thumb_n_width"):
        config.thumb_n_width = parser.getint(section, "thumb_n_width")

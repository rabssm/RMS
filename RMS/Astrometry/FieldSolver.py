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
import logging
from multiprocessing import Process, Event, Queue
import os
import shutil
import subprocess
import re


# FIELD_SOLVER_CMD = os.path.expanduser('~/Applications/astrometry/bin/solve-field')  #
# FIELD_SOLVER_PARAMS = '--cpulimit 60 --no-remove-lines --uniformize 0 --no-plots --extension 1 --overwrite --downsample 4 --crpix-center' # --scale-low 45 --scale-high 100'

# Get the logger from the main module
log = logging.getLogger("logger")


class FieldSolver(Process):
    """ Plate solve an astronomical image
    """

    running = False

    def __init__(self, queue, image_name, config, max_time=60):
        """ Solve a field

        Arguments:
            queue: subprocess queue object to hold the result
            image_name: FITS image to be plate solved
            config: object containing the RMS configuration

        Keyword arguments:
            max_time: int containing the time in seconds to allow for solving. Default is 60 seconds
        """

        super(FieldSolver, self).__init__()

        self.queue = queue
        self.image_name = image_name
        self.config = config
        self.fov_w = self.config.fov_w
        self.solver_cmd = config.field_solver

        log.info("Plate solver command: " + self.solver_cmd)


    def startSolver(self):
        """ Start the solver.

        """

        self.exit = Event()
        self.start()


    def stopSolver(self):
        """ Stop the solver.
        """

        self.exit.set()

        log.info("Stopping the plate solver ...")

        # Wait for the solver to join for 60 seconds, then terminate
        for i in range(60):
            if self.is_alive():
                time.sleep(1)
            else:
                break

        if self.is_alive():
            log.info('Terminating solver ...')
            self.terminate()


    def format_results(self, initial_results) :
        """ Read the solver's result and add the list to the result queue
        [ra, dec, rotation_angle]
        """

        ra_dec = []
        rotation_angle = []
        result_list = initial_results.splitlines()

        for line in result_list :
            #print(line)
            result = re.findall('Field center: *\(RA,Dec\) *= *\((\d.+), *(\d.+)\) *deg', line)
            if len(result) > 0 : ra_dec = result
            result = re.findall('Field rotation angle: up is *(\d.+) +degrees', line)
            if len(result) > 0 : rotation_angle = result

        #print(ra_dec[0][0])
        if len(ra_dec) > 0 and len(rotation_angle) > 0 :
            result_list = list(ra_dec[0])
            result_list.append(rotation_angle[0])
            self.queue.put(result_list)


    def run(self):
        """ Solve the field.
        """

        # Format the arguments for the solver
        scale_args = "--scale-low " + str(int(self.fov_w*0.75)) + " --scale-high " + str(int(self.fov_w*1.25))
        arg_string = self.solver_cmd + " " + scale_args + " " + self.image_name
        args = arg_string.split()


        # Start the field solver process
        print("Running subprocess: " + arg_string)
        log.info("Running subprocess: " + arg_string)
        p = subprocess.Popen(args, stdout=subprocess.PIPE, env={'TZ': 'GMT'})

        # Wait while the solver process is still running and exit not requested
        log.info("Waiting for process " + str(p.pid) + " to complete")
        while p.poll() is None and not self.exit.is_set() :
            time.sleep(2)

        result = p.communicate()[0]
        print(result)
        self.format_results(result)

        # Terminate the solver process if it's still running
        if p is None : pass
        elif p.poll() is None :
            log.info("Terminating process " + str(p.pid))
            p.terminate()
            p.wait()
            log.info("Process terminated")

        print('Solver completed!')


# Main program - for testing purposes
if __name__ == "__main__":

    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("fits_image", help="The name of the FITS image to plate solve")
    args = vars(ap.parse_args())
    image_name = args["fits_image"]

    # Load the configuration file
    import RMS.ConfigReader as cr
    config = cr.parse(".config")

    # Create a queue to hold the result of the field solver
    q = Queue()

    # Create the field solver and start it running
    field_solver = FieldSolver(q, image_name, config)
    field_solver.startSolver()

    # Wait for the solver to complete
    while field_solver.is_alive() :
        time.sleep(1)

    # Get the results of the field solver
    try:
        print(q.get(timeout=1))
    except:
        print("Solver failed")

    # field_solver.stopSolver()



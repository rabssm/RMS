# RPi Meteor Station
# Copyright (C) 2016  Denis Vida
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


def makeCALSTARS(star_list, file_name, ff_directory, cam_code, nrows, ncols):
    """ Writes the star list into the CAMS CALSTARS format. 

    @param star_list: [list] a list of star data, entries:
        ff_name, star_data
        star_data entries:
            x, y, bg_level, level

    @param file_name: [str] file name in which the data will be written
    @param ff_directory: [str] path to the directory in which the file will be written
    @param cam_code: [int] camera number
    @param nrows: [int] number of rows in the image
    @param ncols: [int] number of columns in the image

    @return None
    """

    with open(os.path.join(ff_directory, file_name), 'w') as star_file:

        # Write the header
        star_file.write("==========================================================================\n")
        star_file.write("Asteria star extractor" + "\n")
        star_file.write("Cal time = FF header time plus 255/(2*framerate_Hz) seconds" + "\n")
        star_file.write("Row  Column  Intensity-Backgnd  Intensity  (integrated values)" + "\n")
        star_file.write("==========================================================================\n")
        star_file.write("FF folder = " + ff_directory + "\n")
        star_file.write("Cam #  = " + str(cam_code) + "\n")
        star_file.write("Nrows  = " + str(nrows) + "\n")
        star_file.write("Ncols  = " + str(ncols) + "\n")
        star_file.write("Nstars = -1" + "\n")

        # Write all stars in the CALSTARS file
        for star in star_list:

            # Unpack star data
            ff_name, star_data = star

            # Write star header per image
            star_file.write("==========================================================================\n")
            star_file.write(ff_name + "\n")
            star_file.write("Star area dim = -1" + "\n")
            star_file.write("Integ pixels  = -1" + "\n")

            # Write every star to file
            #for x, y, bg_level, level in zip(x2, y2, background, intensity):
            for x, y, bg_level, level in star_data:
                star_file.write("{:7.2f} {:7.2f} {:6d} {:6d}".format(round(y, 2), round(x, 2), 
                    int(bg_level), int(level)) + "\n")

        # Write the end separator
        star_file.write("##########################################################################\n")

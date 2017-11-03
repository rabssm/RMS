""" Automatic refining of astrometry calibration. The initial astrometric calibration is needed, which will be 
    refined by using all stars from a given night.
"""

from __future__ import print_function, division, absolute_import

import os
import sys
import copy
import shutil
import random

import numpy as np
import scipy.optimize
import matplotlib.pyplot as plt

import RMS.ConfigReader as cr
from RMS.Formats import Platepar
from RMS.Formats import CALSTARS
from RMS.Formats import BSC
from RMS.Formats import FFfile
from RMS.Astrometry.Conversions import date2JD, jd2Date
from RMS.Astrometry.ApplyAstrometry import raDecToCorrectedXYPP, XY2CorrectedRADecPP


# Import Cython functions
import pyximport
pyximport.install(setup_args={'include_dirs':[np.get_include()]})
from RMS.Astrometry.CyFunctions import matchStars,subsetCatalog



def matchStarsResiduals(platepar, catalog_stars, star_dict, max_radius, min_matched_stars, ret_nmatch=False):
    """ Match the image and catalog stars with the given astrometry solution and estimate the residuals 
        between them.
    
    Arguments:
        platepar: [Platepar structure] Astrometry parameters.
        catalog_stars: [ndarray] An array of catalog stars (ra, dec, mag).
        star_dict: [ndarray] A dictionary where the keys are JDs when the stars were recorded and values are
            2D list of stars, each entry is (X, Y, bg_level, level).
        max_radius: [float] Maximum radius for star matching (pixels).
        min_matched_stars: [int] Minimum number of matched stars on the image for the image to be accepted.

    Keyword arguments:
        ret_nmatch: [bool] If True, the function returns the number of matched stars and the average 
            deviation. False by defualt.

    Return:
        cost: [float] The cost function which weights the number of matched stars and the average deviation.

    """


    # Estimate the FOV radius
    x_scale = 384.0/platepar.X_res/platepar.F_scale
    y_scale = 288.0/platepar.Y_res/platepar.F_scale
    fov_w = x_scale*platepar.X_res
    fov_h = y_scale*platepar.Y_res

    fov_radius = np.sqrt((fov_w/2)**2 + (fov_h/2)**2)

    # print('fscale', platepar.F_scale)
    # print('FOVw:', platepar.X_res/platepar.F_scale)
    # print('FOV radius:', fov_radius)


    # Dictionary containing the matched stars, the keys are JDs of every image
    matched_stars = {}


    # Go through every FF image and its stars
    for jd in star_dict:

        # Estimate RA,dec of the centre of the FOV
        _, RA_c, dec_c, _ = XY2CorrectedRADecPP([jd2Date(jd)], [platepar.X_res/2], [platepar.Y_res/2], [0], 
            platepar)

        RA_c = RA_c[0]
        dec_c = dec_c[0]

        # Get stars from the catalog around the defined center in a given radius
        extracted_catalog = subsetCatalog(catalog_stars, RA_c, dec_c, fov_radius, config.catalog_mag_limit)
        ra_catalog, dec_catalog, mag_catalog = extracted_catalog.T


        # Extract stars for the given Julian date
        stars_list = star_dict[jd]
        stars_list = np.array(stars_list)

        # Convert all catalog stars to image coordinates
        cat_x_array, cat_y_array = raDecToCorrectedXYPP(ra_catalog, dec_catalog, jd, platepar)


        # Take only those stars which are within the FOV
        x_indices = np.argwhere((cat_x_array >= 0) & (cat_x_array < platepar.X_res))
        y_indices = np.argwhere((cat_y_array >= 0) & (cat_y_array < platepar.Y_res))
        cat_good_indices = np.intersect1d(x_indices, y_indices).astype(np.uint32)

        # cat_x_array = cat_x_array[good_indices]
        # cat_y_array = cat_y_array[good_indices]


        # # Plot image stars
        # im_y, im_x, _, _ = stars_list.T
        # plt.scatter(im_y, im_x, c='r', s=5)

        # # Plot catalog stars
        # plt.scatter(cat_y_array[cat_good_indices], cat_x_array[cat_good_indices], facecolors='none', edgecolor='g')

        # plt.show()
        
        
        #matched_indices = []

        # # Match image and catalog stars
        # # Go through all image stars
        # for i, entry in enumerate(stars_list):

        #     # Extract image star data
        #     im_star_y, im_star_x, _, _ = entry

        #     min_dist = np.inf
        #     cat_match_indx = None

        #     # Check for the best match among catalog stars
        #     for k in cat_good_indices:

        #         cat_x = cat_x_array[k]
        #         cat_y = cat_y_array[k]


        #         # Calculate the distance between stars
        #         dist = np.sqrt((im_star_x - cat_x)**2 + (im_star_y - cat_y)**2)

        #         if (dist < min_dist):
        #             min_dist = dist
        #             cat_match_indx = k


        #     # Take the best matched star if the distance was within the maximum radius
        #     if min_dist < max_radius:
        #         matched_indices.append([i, cat_match_indx, min_dist])



        # Match image and catalog stars
        matched_indices = matchStars(stars_list, cat_x_array, cat_y_array, cat_good_indices, max_radius)

        # Skip this image is no stars were matched
        if len(matched_indices) < min_matched_stars:
            continue

        matched_indices = np.array(matched_indices)
        matched_img_inds, matched_cat_inds, dist_list = matched_indices.T

        # Extract data from matched stars
        matched_img_stars = stars_list[matched_img_inds.astype(np.int)]
        matched_cat_stars = catalog_stars[matched_cat_inds.astype(np.int)]

        # Put the matched stars to a dictionary
        matched_stars[jd] = [matched_img_stars, matched_cat_stars, dist_list]


        # # Plot matched stars
        # im_y, im_x, _, _ = matched_img_stars.T
        # cat_y = cat_y_array[matched_cat_inds.astype(np.int)]
        # cat_x = cat_x_array[matched_cat_inds.astype(np.int)]

        # plt.scatter(im_x, im_y, c='r', s=5)
        # plt.scatter(cat_x, cat_y, facecolors='none', edgecolor='g')

        # plt.xlim([0, platepar.X_res])
        # plt.ylim([platepar.Y_res, 0])

        # plt.show()


    # Extract all distances
    global_dist_list = []
    level_list = []
    mag_list = []
    for jd in matched_stars:
        matched_img_stars, matched_cat_stars, dist_list = matched_stars[jd]
        
        global_dist_list += dist_list.tolist()

        # TEST
        level_list += matched_img_stars[:, 3].tolist()
        mag_list += matched_cat_stars[:, 2].tolist()



    # # Plot levels vs. magnitudes
    # plt.scatter(mag_list, np.log10(level_list))
    # plt.xlabel('Magnitude')
    # plt.ylabel('Log10 level')
    # plt.show()


    # Number of matched stars
    n_matched = len(global_dist_list)

    if n_matched == 0:
        return 9999.0

    # Calculate the average distance
    avg_dist = np.mean(global_dist_list)

    cost = (avg_dist**2)*(1.0/np.sqrt(n_matched + 1))
    #cost = 1.0/np.sqrt(n_matched + 1)

    print('Nmatched', n_matched)
    # # print('Avg dist', avg_dist)
    print('Cost:', cost)
    print('-----')


    if ret_nmatch:
        return n_matched, avg_dist, cost

    else:
        return cost




def _calcImageResidualsAstro(params, platepar, catalog_stars, star_dict, max_radius, min_matched_stars):
    """ Calculates the differences between the stars on the image and catalog stars in image coordinates with 
        the given astrometrical solution. 
    """


    # Make a copy of the platepar
    pp = copy.deepcopy(platepar)

    # Extract fitting parameters
    ra_ref, dec_ref, pos_angle_ref, F_scale = params

    # Set the fitting parameters to the platepar clone
    pp.RA_d = ra_ref
    pp.dec_d = dec_ref
    pp.pos_angle_ref = pos_angle_ref
    pp.F_scale = F_scale


    # Match stars and calculate image residuals
    return matchStarsResiduals(pp, catalog_stars, star_dict, max_radius, min_matched_stars)



def _calcImageResidualsDistorsion(params, platepar, catalog_stars, star_dict, max_radius, min_matched_stars, \
        dimension):
    """ Calculates the differences between the stars on the image and catalog stars in image coordinates with 
        the given astrometrical solution. 
    """

    # Make a copy of the platepar
    pp = copy.deepcopy(platepar)

    if dimension == 'x':
        pp.x_poly = params

    else:
        pp.y_poly = params


    # Match stars and calculate image residuals
    return matchStarsResiduals(pp, catalog_stars, star_dict, max_radius, min_matched_stars)





def autoCheckFit(config, platepar, calstars_list):
    """ Attempts to refine the astrometry fit with the given stars and and initial astrometry parameters.

    Arguments:
        config: [Config structure]
        platepar: [Platepar structure] Initial astrometry parameters.
        calstars_list: [list] A list containing stars extracted from FF files. See RMS.Formats.CALSTARS for
            more details.
    
    """


    # Convert the list to a dictionary
    calstars = {ff_file: star_data for ff_file, star_data in calstars_list}

    # Load catalog stars
    catalog_stars = BSC.readBSC(config.star_catalog_path, config.star_catalog_file, \
        lim_mag=config.catalog_mag_limit)


    # Dictionary which will contain the JD, and a list of (X, Y, bg_intens, intens) of the stars
    star_dict = {}

    # Take only those files with enough stars on them
    for ff_name in calstars:

        stars_list = calstars[ff_name]

        # Check if there are enough stars on the image
        if len(stars_list) >= config.ff_min_stars:
            
            # Calculate the JD time of the FF file
            dt = FFfile.getMiddleTimeFF(ff_name, config.fps, ret_milliseconds=True)
            jd = date2JD(*dt)

            # Add the time and the stars to the dict
            star_dict[jd] = stars_list


    # There has to be a minimum of 200 FF files for star fitting, and only 100 will be subset if there are more
    if len(star_dict) < config.calstars_files_N:
        print('Not enough FF files in CALSTARS for ACF!')
        return platepar, False

    else:

        # Randomly choose calstars_files_N image files from the whole list
        rand_keys = random.sample(star_dict, config.calstars_files_N)
        star_dict = {key: star_dict[key] for key in rand_keys}


    # Calculate the total number of calibration stars used
    total_calstars = sum([len(star_dict[key]) for key in star_dict])
    print('Total calstars:', total_calstars)

    if total_calstars < config.calstars_min_stars:
        print('Not enough calibration stars, need at least', config.calstars_min_stars)
        return platepar, False


    # A list of matching radiuses to try
    radius_list = [3, 1.5, 0.75]

    for max_radius in radius_list:

        # Match the stars and calculate the residuals
        n_matched, avg_dist, cost = matchStarsResiduals(platepar, catalog_stars, star_dict, max_radius, \
            config.min_matched_stars, ret_nmatch=True)

        print('Max radius:', max_radius)
        print('Initial values:')
        print(' Matched stars:', n_matched)
        print(' Average deviation:', avg_dist)


        # The initial number of matched stars has to be at least the number of FF imaages, otherwise it means
        #   that the initial platepar is no good
        if n_matched < config.calstars_files_N:
            print('The total number of initially matched stars is too small! Please manually redo the plate or make sure there are enough calibration stars.')
            return platepar, False


        # Initial parameters for the astrometric fit
        p0 = [platepar.RA_d, platepar.dec_d, platepar.pos_angle_ref, platepar.F_scale]

        # Fit the astrometric parameters
        res = scipy.optimize.minimize(_calcImageResidualsAstro, p0, args=(platepar, catalog_stars, \
            star_dict, max_radius, config.min_matched_stars), method='Nelder-Mead', options={'fatol': 1e-1})

        print(res)

        # If the fit was not successful, stop further fitting
        if not res.success:
            return platepar, False


        else:
            # If the fit was successful, use the new parameters from now on
            ra_ref, dec_ref, pos_angle_ref, F_scale = res.x

            platepar.RA_d = ra_ref
            platepar.dec_d = dec_ref
            platepar.pos_angle_ref = pos_angle_ref
            platepar.F_scale = F_scale


        

        # Fit the distortion parameters (X axis)
        res = scipy.optimize.minimize(_calcImageResidualsDistorsion, platepar.x_poly, args=(platepar, \
            catalog_stars, star_dict, max_radius, config.min_matched_stars, 'x'), method='Nelder-Mead', \
            options={'fatol': 1e-1})

        print(res)

        # If the fit was not successfull, stop further fitting
        if not res.success:
            return platepar, False

        else:
            platepar.x_poly = res.x



        # Fit the distortion parameters (Y axis)
        res = scipy.optimize.minimize(_calcImageResidualsDistorsion, platepar.y_poly, args=(platepar, \
            catalog_stars, star_dict, max_radius, config.min_matched_stars, 'y'), method='Nelder-Mead', \
            options={'fatol': 1e-1})

        print(res)

        # If the fit was not successfull, stop further fitting
        if not res.success:
            return platepar, False

        else:
            platepar.y_poly = res.x


    # Match the stars and calculate the residuals
    n_matched, avg_dist, cost = matchStarsResiduals(platepar, catalog_stars, star_dict, max_radius, 
        config.min_matched_stars, ret_nmatch=True)

    print('Matched stars:', n_matched)
    print('Average deviation:', avg_dist)


    return platepar, True
    



if __name__ == "__main__":


    if len(sys.argv) < 2:
        print('Usage: python -m RMS.Astrometry.AstrometryCheckFit /path/to/FF/dir/')
        sys.exit()

    # Night directory
    dir_path = sys.argv[1].replace('"', '')


    # Check if the given directory is OK
    if not os.path.exists(dir_path):
        print('No such directory:', dir_path)
        sys.exit()


    # Load the configuration file
    config = cr.parse(".config")


    # Get a list of files in the night folder
    file_list = os.listdir(dir_path)



    # Find and load the platepar file
    if config.platepar_name in file_list:

        # Load the platepar
        platepar = Platepar.Platepar()
        platepar.read(os.path.join(dir_path, config.platepar_name))

    else:
        print('Cannot find the platepar file in the night directory: ', config.platepar_name)
        sys.exit()


    # Find the CALSTARS file in the given folder
    calstars_file = None
    for calstars_file in file_list:
        if ('CALSTARS' in calstars_file) and ('.txt' in calstars_file):
            break

    if calstars_file is None:
        print('CALSTARS file could not be found in the given directory!')
        sys.exit()

    # Load the calstars file
    calstars_list = CALSTARS.readCALSTARS(dir_path, calstars_file)

    print('CALSTARS file: ' + calstars_file + ' loaded!')




    # Run the automatic astrometry fit
    pp, fit_status = autoCheckFit(config, platepar, calstars_list)

    # If the fit suceeded, save the platepar
    if fit_status:

        print('ACF sucessful!')

        # Save the old platepar
        shutil.move(os.path.join(dir_path, config.platepar_name), os.path.join(dir_path, 
            config.platepar_name + '.old'))

        # Save the new platepar
        pp.write(os.path.join(dir_path, config.platepar_name))
""" Download a platepar from the server if a new plate exists. """

from __future__ import print_function, division, absolute_import

import datetime
import logging

import paramiko


from RMS.UploadManager import _agentAuth


# Get the logger from the main module
log = logging.getLogger("logger")




def downloadNewPlatepar(config, port=22):
    """ Connect to the central server and download a new platepar calibration file, if available. """


    log.info('Establishing SSH connection to: ' + config.hostname + ':' + str(port) + '...')

    try:
        # Connect to host
        t = paramiko.Transport((config.hostname, port))
        t.start_client()

        # Authenticate the connection
        auth_status = _agentAuth(t, config.stationID.lower(), config.rsa_private_key)
        if not auth_status:
            return False

        # Open new SFTP connection
        sftp = paramiko.SFTPClient.from_transport(t)

    except:
        log.error('Connecting to server failed!')
        return False


    # Check that the remote directory exists
    try:
        sftp.stat(config.remote_dir)

    except Exception as e:
        log.error("Remote directory '" + config.remote_dir + "' does not exist!")
        return False


    # Construct path to remote platepar directory
    remote_platepar_path = config.remote_dir + '/' + config.remote_platepar_dir + '/'

    # Change the directory into file
    remote_platepar = remote_platepar_path + config.platepar_remote_name


    # Check if the remote platepar file exists
    try:
        sftp.lstat(remote_platepar)
    
    except IOError as e:
        log.info('No new platepar on the server!')
        return False


    # Download the remote platepar
    sftp.get(remote_platepar, config.platepar_name)

    log.info('Latest platepar downloaded!')


    ### Rename the downloaded platepar file, add a timestamp of download

    # Construct a new name with the time of the download included
    dl_pp_name = remote_platepar_path + 'platepar_dl_' \
        + datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S.%f') + '.cal'

    sftp.posix_rename(remote_platepar, dl_pp_name)

    log.info('Remote platepar renamed to: ' + dl_pp_name)

    ### ###

    return True




if __name__ == "__main__":

    import os
    from RMS.Logger import initLogging

    # Set up a fake config file
    class FakeConf(object):
        def __init__(self):

            self.username = 'dvida'

            # remote hostname where SSH server is running
            self.hostname = 'gmn.uwo.ca'
            self.host_port = 22
            self.remote_dir = 'files'
            self.remote_platepar_dir = 'platepars'
            self.stationID = 'dvida'
            self.rsa_private_key = os.path.expanduser("~/.ssh/id_rsa")

            self.upload_queue_file = 'FILES_TO_UPLOAD.inf'
            self.platepar_name = 'platepar_cmn2010.cal'
            self.platepar_remote_name = 'platepar_latest.cal'


    config = FakeConf()

    # Init the logger
    initLogging()


    # Test platepar downloading
    downloadNewPlatepar(config, port=22)
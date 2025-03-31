from optparse import OptionParser
import logging
import os
import time
import shutil
import hashlib
import sys

# Default variables
DFLT_INTERVAL = 5000
DFLT_LOGFILE  = "folder_sync.log"
LOG_LEVEL     = logging.DEBUG

# Logging functions
def logging_setup(log_file):
    logging.basicConfig( filename = log_file, 
                         encoding = 'utf-8',
                         level = LOG_LEVEL,
                         format = '%(levelname)s: %(asctime)s: %(message)s', 
                         datefmt = '%m/%d/%Y %I:%M:%S %p' )

def log_file_changes(name, op):
    msg = f"FILE '{name}' {op}"
    logging.info(msg)
    print(f"{time.strftime('%m/%d/%Y %I:%M:%S %p')} - {msg}")

def log_folder_changes(name, op):
    msg = f"FOLDER '{name}' {op}"
    logging.info(msg)
    print(f"{time.strftime('%m/%d/%Y %I:%M:%S %p')} - {msg}")


# File processing functions
def files_are_equal(fileA, fileB):
    try:
        md5sumA = hashlib.md5(open(fileA,'rb').read()).hexdigest()
        md5sumB = hashlib.md5(open(fileB,'rb').read()).hexdigest()
    except:
        logging.error(f"Cannot compare '{fileA}' and '{fileB}'")
        exit(f"{time.strftime('%m/%d/%Y %I:%M:%S %p')} - Cannot compare '{fileA}' and '{fileB}'")
    return md5sumA == md5sumB

def remove_item(path):
    if not os.path.isdir(path):
        os.remove(path)
        log_file_changes(path, "removed")
    else:
        os.rmdir(path)
        log_folder_changes(path, "removed")


# Main application functions
def sync_folders(src_dir, dst_dir):
    # Check if destination folder exists and if not, create it
    if not os.path.isdir(dst_dir):
        os.mkdir(dst_dir)
        log_folder_changes(dst_dir, "created")
    
    # List all files and folders inside the source and destination folders
    list_source = os.listdir(src_dir)
    list_dst    = os.listdir(dst_dir)
    
    # Check and clean destination folder
    for item in list_dst:
        if item not in list_source:            
            fullpath_dst = os.path.join(dst_dir, item)
            remove_item(fullpath_dst)
    
    # Check source folder to create or copy files
    for item in list_source:
        fullpath_src = os.path.join(src_dir, item)
        fullpath_dst = os.path.join(dst_dir, item)
        
        # If item is file, then see if it needs to be copied
        # If item is a folder, then run sync_folders with this item as argument
        if not os.path.isdir(fullpath_src):
            if item not in list_dst:
                shutil.copy(fullpath_src, fullpath_dst)
                log_file_changes(fullpath_dst, "created")
            else:
                #check if files are different and copy if they are
                if not files_are_equal(fullpath_src, fullpath_dst):
                    shutil.copy(fullpath_src, fullpath_dst)
                    log_file_changes(fullpath_dst, "copied")
        else:
            sync_folders(fullpath_src, fullpath_dst)


def main():
    # Argument parsing
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-s", "--source", dest = "src_dir", help = "Path to the source folder (the folder to be copied)")
    parser.add_option("-d", "--destination", dest = "dst_dir", help = "Path to the replica folder (the folder to be synchronized)")
    parser.add_option("-i", "--interval", dest = "interval", type = "int", default = DFLT_INTERVAL, help = f"Time interval (in milliseconds) between synchronizations. (Default: {DFLT_INTERVAL} ms)")
    parser.add_option("-l", "--logFile", dest = "log_file", default = DFLT_LOGFILE, help = f"Path to the log file where synchronization activities will be recorded. (Default: '{DFLT_LOGFILE}')")
    (options, args) = parser.parse_args()

    src_dir         = options.src_dir
    dst_dir         = options.dst_dir
    interval_time   = options.interval/1000
    log_filename    = options.log_file
    
    # Check if source folder exists
    if not os.path.isdir(src_dir):
        exit("Please provide a valid path to an existing source folder. Exiting...")
    
    try:
        logging_setup(log_filename)
    except:
        exit("Failed to initialize logging. Exiting...")
        
    print("Press Ctrl+C to exit the application.\n")
    while(True):
        
        # Check if source folder exists
        if not os.path.isdir(src_dir):
            exit("Please provide a valid path to an existing source folder. Exiting...")
        
        try:
            logging.info("Synchronization has started")
            print(f"{time.strftime('%m/%d/%Y %I:%M:%S %p')} - Synchronization has started")
            sync_folders(src_dir, dst_dir)
        except KeyboardInterrupt:
            logging.info("Stopping synchronization process")
            print(f"{time.strftime('%m/%d/%Y %I:%M:%S %p')} - Stopping synchronization process")
            sys.exit()
        except:
            logging.error("Synchronization failed")
            print(f"{time.strftime('%m/%d/%Y %I:%M:%S %p')} - Synchronization failed")
        else:
            logging.info("Synchronization completed")
            print(f"{time.strftime('%m/%d/%Y %I:%M:%S %p')} - Synchronization completed")
        
        # Sleeping time
        try:
            time.sleep(interval_time)
        except KeyboardInterrupt:
            logging.info("Stopping synchronization")
            print(f"{time.strftime('%m/%d/%Y %I:%M:%S %p')} - Stopping synchronization")
            sys.exit()
    


if __name__ == "__main__":
    main()
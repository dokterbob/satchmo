import os

def normalize_path(path):
    """
    Converts the supplied path to lower case, removes any unnecessary slashes 
    and makes all slashes forward slashes.
    This is particularly useful for Windows systems.
    It is recommended to use in your settings if you are on Windows.
    
    MEDIA_ROOT = normalize_path(os.path.join(DIRNAME, 'static/'))
    """
    return os.path.normcase(os.path.normpath(path)).replace('\\', '/')

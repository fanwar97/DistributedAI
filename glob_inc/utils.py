import os
def int_to_ubyte(num):
    return num.to_bytes(1, "big", signed = False)
def int_to_Nubyte(num, N):
    return num.to_bytes(N, "big", signed = False)
def choose_file_in_folder_by_order(folder, file_order):
    dir_name = folder
    # Get list of all files in a given directory sorted by name
    list_of_files = sorted( filter( lambda x: os.path.isfile(os.path.join(dir_name, x)),
                        os.listdir(dir_name) ) )
    return list_of_files[file_order]
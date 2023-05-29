# python file in the same directory as the data file
import os
import json
import shutil                           #copy and overwrite operations
from subprocess import PIPE, run        # run any terminal commands for GO code
import sys

#grab from command line arg the source and destination directories - command line args are the filename when u make a new folder

GAME_DIR_PATTERN = "game"               #detect _game ending
GAME_CODE_EXTENSION = ".go"
GAME_COMPILE_COMMAND = ["go", "build"]

#walk through the directory and match any with _game ending return the paths
def find_all_game_paths(source):
    game_paths = []

    for root, dirs, files in os.walk(source):# walk() recursively look in every single root, files, directories
        for directory in dirs:          # this line only give the names of the directory not paths
            if GAME_DIR_PATTERN in directory.lower():
                path = os.path.join(source, directory)  #this linefind the path of the directory
                game_paths.append(path)
        break                           # only need to look one time

    return game_paths

#split just the directory names from the paths
def get_name_from_path(paths, to_strip):
    new_names = []
    for path in paths:
        _, dir_name = os.path.split(path)   # just get the directory name at the end, remaining _ on left
        new_dir_name = dir_name.replace(to_strip, "")   #remove the _game part
        new_names.append(new_dir_name)

    return new_names

def create_dir(path):
    if not os.path.exists(path):       # create the path if it doesn't already exist
        os.mkdir(path)

#copy games into the new dir
def copy_and_overwrite(source, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(source, dest)

#make a json file
def make_json_metadata_file(path, game_dirs):
    data = {
        "gameName": game_dirs,
        "numberOfGames": len(game_dirs)
    }
    with open(path, "w") as f:      # to close the window auto
        json.dump(data, f)

#look for any file with .go
def compile_game_code(path):
    code_file_name = None
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(GAME_CODE_EXTENSION):
                code_file_name = file
                break                   #look for only one file
        break

    if code_file_name is None:
        return
    
    command = GAME_COMPILE_COMMAND + [code_file_name]
    run_command(command, path)

#running the games
def run_command(command, path):
    cwd = os.getcwd()
    os.chdir(path)                      #change directory

    run(command, stdout=PIPE, stdin=PIPE, universal_newlines=True)  #connect python with terminal

    os.chdir(cwd)                       # change back to current dir

# main function
def main(source, target):
    #create a complete path from where python file runs to directory
    cwd = os.getcwd()                   # current directory py is running from
    source_path = os.path.join(cwd, source)     #get the path
    target_path = os.path.join(cwd, target)   

    game_paths = find_all_game_paths(source_path)
    new_game_dirs = get_name_from_path(game_paths, "_game")

    create_dir(target_path)

    #copy games into new dirs and run them
    for src, dest in zip(game_paths, new_game_dirs):    #zip takes matching elements from 2 arrays make them into a tuple
        dest_path = os.path.join(target_path, dest)
        copy_and_overwrite(src,dest_path)
        compile_game_code(dest_path)

    #make json file
    json_path = os.path.join(target_path, "metadata.json")
    make_json_metadata_file(json_path, new_game_dirs)

if __name__ == "__main__":              #execute main script only, won't execute any imports
    args = sys.argv
    if len(args) != 3:                  # 3 arguments - execution file(get_game_data.py), source, destination
        raise Exception("You must pass a source and target directory only")

    source, target = args[1:]           # only need the source and destination
    main(source, target)
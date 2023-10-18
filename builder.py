#!/usr/bin/env python

'''
@brief Program to check if any changes are there in the project and rebuild the project
@author war10ck
@note This program will as of now only support C projects, going forward, based on the requirement more
project type supports will be added
'''

from json import load, dump
from os import getcwd, system, sep
from pathlib import Path
from sys import version
from traceback import format_exc
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Build limit related constants
BUILD_LIMIT = 3000
BUILD_MAJOR_START = 0
BUILD_MINOR_START = 0
BUILD_NUMBER_START = 1

# Build state key constants
K_MAJOR = "major"
K_MINOR = "minor"
K_NUMBER = "number"

# Current build related globals
CB_MAJOR = 0
CB_MINOR = 0
CB_NUMBER = 0

if not Path("./buildstate.json").exists():
    CB_MAJOR = BUILD_MAJOR_START
    CB_MINOR = BUILD_MINOR_START
    CB_NUMBER = BUILD_NUMBER_START
else:
    with open("./buildstate.json") as jfile:
        data = load(jfile)
        CB_MAJOR = data.get(K_MAJOR)
        CB_MINOR = data.get(K_MINOR)
        CB_NUMBER = data.get(K_NUMBER)

class Watcher:
    def __init__(self, dpath: str) -> None:
        '''
        @brief default constructor of Watcher class
        @param dpath: String containing the path of the directory to be watched
        @note if the dpath value is not a string or an empty string, TypeError will be thrown
        '''
        if not isinstance(dpath, str) or len(dpath) == 0:
            raise TypeError(f"Directory path should be a non-empty string")

        self._wd = dpath          # _wd -> watch directory
        self._observer = Observer()

    def run(self) -> None:
        '''
        @brief function responsible for running the watcher
        '''
        self._observer.schedule(event_handler=Handler(), path=self._wd, recursive=True)
        self._observer.start()

        try:
            while True:
                pass # we do not need to do anything, just keep the program running
        except Exception:
            print(format_exc())
        finally:
            self._observer.join()

class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        '''
        @brief function to be called when any event is triggered. Here events mean modified, created etc.
        @note As of now, the created and modified events are only going to be monitored
        '''
        eventset = {"created", "modified"}
        if event.is_directory:
            return
        
        if event.event_type in eventset:
            Handler().rebuild(fname=event.src_path)

    def rebuild(self, fname: str) -> None:
        '''
        @brief function to rebuild the project once the *.c or *.h files are modified
        @note this function will also be responsible for adding a build header containing the build number
        and major as well as minor version
        '''
        # fixme: add the code for handling build number, major and minor versions
        global BUILD_LIMIT, BUILD_MAJOR_START, BUILD_MINOR_START, BUILD_NUMBER_START
        global CB_MAJOR, CB_MINOR, CB_NUMBER
        
        if not isinstance(fname, str) or len(fname) == 0:
            return None

        if (fname.endswith(".h") or fname.endswith(".c")) and not fname.endswith("build.h"):
            with open(f"{getcwd()}{sep}inc{sep}build.h", "w") as bh:
                if CB_NUMBER >= BUILD_LIMIT:
                    CB_MAJOR += 1
                    CB_MINOR = BUILD_MINOR_START
                    CB_NUMBER = BUILD_NUMBER_START
                else:
                    if CB_NUMBER % 200 == 0 and CB_NUMBER != 0: # after every 200 builds, update minor version
                        CB_MINOR += 1
                    CB_NUMBER += 1

                bh.write(f"#ifndef _BUILD_H\n#define _BUILD_H\n\n #define BUILD_MAJOR {CB_MAJOR}\n")
                bh.write(f"#define BUILD_MINOR {CB_MINOR}\n")
                bh.write(f"#define BUILD_NUMBER {CB_NUMBER}\n")
                bh.write("\n#endif")

                jsondata = {K_MAJOR: CB_MAJOR, K_MINOR: CB_MINOR, K_NUMBER: CB_NUMBER}
                with open("./buildstate.json", "w") as state:
                    dump(jsondata, state)
            system('make')

def main():
    w = Watcher(dpath=getcwd())
    w.run()
    return 0

if __name__ == "__main__":
    main()

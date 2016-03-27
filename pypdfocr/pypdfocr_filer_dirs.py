
# Copyright 2013 Virantha Ekanayake All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging
import os
import shutil

from pypdfocr_filer import PyFiler

"""
    Implementation of a filer class 
        -> Works on file system/directory structure
"""
class PyFilerDirs(PyFiler):
    
    def __init__(self):
        self.target_folder = None
        self.default_folder = None
        self.original_move_folder = None
        self.root_folder = None
        self.inbox_folder = None
        self.folder_targets = {}
  
    def getRoot(file=None):
        if file is None:
          file='.'
        me=os.path.abspath(file)
        drive,path=os.path.splitdrive(me)
        while 1:
            path,folder=os.path.split(path)
            if not folder:
                break
        return drive+path     

    def add_folder_target(self, folder, keywords):
        assert folder not in self.folder_targets, "Target folder already defined! (%s)" % (folder)
        self.folder_targets[folder] = keywords

    def file_original(self, original_filename):
        if not self.original_move_folder:
            logging.debug("Leaving original untouched")
            return original_filename

        tgt_path = self.original_move_folder
        logging.debug("Moving original %s to %s" % (original_filename, tgt_path))
        tgtfilename = os.path.join(tgt_path, os.path.basename(original_filename))
        tgtfilename = self._get_unique_filename_by_appending_version_integer(tgtfilename)

        shutil.move(original_filename, tgtfilename)
        return tgtfilename

    def move_to_matching_folder(self, filename, newfilename,foldername):
        assert self.target_folder != None
        assert self.default_folder != None
        subfoldername = ""
        if filename.find('_')!=-1:  #if found
            subfoldername = "/"+filename.split('_')[0]
        
        if not foldername:
            logging.info("[DEFAULT] %s --> %s" % (newfilename, self.default_folder))
            
            tgt_path = os.path.join(subfoldername,os.path.split(self.target_folder)[1]), self.default_folder.rsplit('/',1)[0])
            #tgt_path = os.path.join(self.target_folder, self.default_folder)
        else:   
            logging.info("[MATCH] %s --> %s" % (newfilename, foldername))
            logging.info( os.getcwd())
            logging.info(self.root_folder)
            logging.info(self.target_folder.split('/',1)[1])
            logging.info(subfoldername)
            logging.info(os.path.join(self.root_folder,subfoldername,os.path.split(self.target_folder)[1]) ) 
            
            tgt_path = os.path.join(self.root_folder,subfoldername,os.path.split(self.target_folder)[1], foldername )
            #tgt_path = os.path.join(self.target_folder,foldername)

        if not os.path.exists(tgt_path):
            logging.info("Making path %s" % tgt_path)
            os.makedirs(tgt_path)

        logging.info("Moving %s to %s" % (newfilename, tgt_path))
        tgtfilename = os.path.join(tgt_path, os.path.basename(newfilename))
        tgtfilename = self._get_unique_filename_by_appending_version_integer(tgtfilename)

        shutil.move(filename, tgtfilename)
        return tgtfilename
        
 



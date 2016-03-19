
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

"""
    Provides capability to search PDFs and file to a specific folder based
    on keywords
"""

from sets import Set    
import sys, os
import re
import logging
import shutil
import datetime
import string

from PyPDF2 import PdfFileReader
from pypdfocr_filer import PyFiler
from pypdfocr_filer_dirs import PyFilerDirs

class PyPdfFiler(object):
    def __init__(self, filer):

        assert isinstance(filer, PyFiler)
        self.filer = filer  # Must be a subclass of PyFiler

        # Whether to fall back on filename for matching keywords against
        # if there is no match in the text
        self.file_using_filename = False 

    def iter_pdf_page_text(self, filename):
    	year=""
    	month=""
    	day=""
    	mydate=""
    	
        self.filename = filename
        reader = PdfFileReader(open(filename,"rb"))
        logging.info("pdf scanner found %d pages in %s" % (reader.getNumPages(), filename))
        
        metadata = reader.getDocumentInfo()
        logging.info("METADATA: " + str(metadata))
        
        try:
            if metadata.has_key('/CreationDate'):
                year = metadata['/CreationDate'][2:5]
                month = metadata['/CreationDate'][6:7]
                day = metadata['/CreationDate'][8:9]
                mydate =year+"-"+month+"-"+day 
            else:
                mydate = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
        except: #hack ... but sometimes /creationdate is bunged
            mydate = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")

        for pgnum in range(reader.getNumPages()):
            text = reader.getPage(pgnum).extractText()
            text = text.encode('ascii', 'ignore')
            text = text.replace('\n', ' ')
            yield text

    def _get_matching_folder(self, pdfText):
        searchText = pdfText.lower()
        for folder,strings in self.filer.folder_targets.items():
            for s in strings:
                logging.debug("Checking string %s" % s)
                if s in searchText:
                    logging.info("Matched keyword '%s'" % s)
                    return folder
        # No match found, so return 
        return None

    def file_original (self, original_filename):
        return self.filer.file_original(original_filename)

    def move_to_matching_folder(self, filename):
    	splitted1=""
    	splitted2=""
    	splitted3=""
    	splitted4=""
    	splitted5=""
        for page_text in self.iter_pdf_page_text(filename):
            tgt_folder = self._get_matching_folder(page_text)
            splitted = page_text.split(' ', 5)
	    if len(splitted) > 5:
	        splitted1 = splitted[0].strip()
	        splitted2 = splitted[1].strip()
	        splitted3 = splitted[2].strip()
	        splitted4 = splitted[3].strip()
	        splitted5 = splitted[4].strip()
	        if tgt_folder: break  # Stop searching through pdf pages as soon as we find a match

        if not tgt_folder and self.file_using_filename:
            tgt_folder = self._get_matching_folder(filename)
        
        mydate = (datetime.datetime.now() - datetime.timedelta(hours=6)).strftime("%Y-%m-%d-%H%M")
        myname=""
        if not splitted1:
            myname = myname + splitted1 + "_"
        if not splitted2:
            myname = myname + splitted2 + "_"
        if not splitted3:
	    myname = myname + splitted3 + "_"
        if not splitted4:
            myname = myname + splitted4 + "_"
        if not splitted5:
            myname = myname + splitted5
	
	tempfile = mydate + " " + myname
	valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        newFileName = ''.join(c for c in tempfile if c in valid_chars)
        newFileName = newFileName.replace(' ','_') # I don't like spaces in filenames.
        newFileName = newFileName[0:60] + ".pdf"
        
	logging.info("Changing file name %s --> %s" % (filename,newFileName))
        tgt_file = self.filer.move_to_matching_folder(filename,newFileName, tgt_folder)
        return tgt_file
        
if __name__ == '__main__':
    p = PyPdfFiler(PyFilerDirs())
    for page_text in p.iter_pdf_page_text("scan_ocr.pdf"):
        print (page_text)


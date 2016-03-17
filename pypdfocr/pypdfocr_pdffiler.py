
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
      # self.filename = filename
        reader = PdfFileReader(filename)
        logging.info("pdf scanner found %d pages in %s" % (reader.getNumPages(), filename))
        
        metadata = reader.getDocumentInfo()
        print metadata
        
        try:
            if metadata.has_key('/CreationDate'):
                year = metadata['/CreationDate'][2:5]
                month = metadata['/CreationDate'][6:7]
                day = metadata['/CreationDate'][8:9]
            else:
                year = datetime.date.today()
        except: #hack ... but sometimes /creationdate is bunged
            year = datetime.date.today()
        
	pageObj = reader.getPage(0)
	rawText = pageObj.extractText()
	cleanText = re.sub(r'  ', '\n', re.sub(r'\n', '', rawText)) # do some regex to make it more readable
	#cleanText = re.sub(r'\n', "", rawText)
	splitted1 = cleanText.split(' ', 5)[0]
	splitted2 = cleanText.split(' ', 5)[1]
	splitted3 = cleanText.split(' ', 5)[2]
	splitted4 = cleanText.split(' ', 5)[3]
	splitted5 = cleanText.split(' ', 5)[4]
	
	newFileName = year+"-"+month+"-"+day + " " + splitted1+"_"+splitted2+"_"+splitted3+"_"+splitted4+"_"+splitted5+".pdf"
	logging.info("Changing file name %s --> %s" % (filename,newFileName))
	self.filename = newFileName
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
        for page_text in self.iter_pdf_page_text(filename):
            tgt_folder = self._get_matching_folder(page_text)
            if tgt_folder: break  # Stop searching through pdf pages as soon as we find a match

        if not tgt_folder and self.file_using_filename:
            tgt_folder = self._get_matching_folder(filename)

        tgt_file = self.filer.move_to_matching_folder(filename, tgt_folder)
        return tgt_file
        
if __name__ == '__main__':
    p = PyPdfFiler(PyFilerDirs())
    for page_text in p.iter_pdf_page_text("scan_ocr.pdf"):
        print (page_text)


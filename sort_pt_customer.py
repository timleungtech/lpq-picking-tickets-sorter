#sbCustomers_20230321 for danish, pastry, kitchen orders
import pdfplumber
import PyPDF2
from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger
import os
import glob

orderType = str(input("File name: ")) # user input filename and saves to orderType variable
os.rename(f"{orderType}.pdf","input.pdf") # rename file to input.pdf
lastPage = PyPDF2.PdfFileReader(open('input.pdf', 'rb')).numPages  # number of pages in pdf
page_id = 1 # fix for overwriting orders >1 page long

with pdfplumber.open('input.pdf') as pdf: # opens inputted pdf
    for i in range(lastPage): # iterate to lastPage
        curr_page = pdf.pages[i] # assign curr_page variable
        customerId = curr_page.extract_text()[10:16] # extract customer ID
        path = ('input.pdf') # set path variable
        pdf_reader = PdfFileReader(path)
        pdf_writer = PdfFileWriter()
        pdf_writer.addPage(pdf_reader.getPage(i)) # creates the page
        output_filename = 'input_{}_{}.pdf'.format( # file name convention
            customerId, page_id)
        with open(output_filename, 'wb') as out: # writes file name
            pdf_writer.write(out)
        print('Created: {}'.format(output_filename)) # logs the pages as renaming finishes
        page_id += 1

def merger(output_path, input_paths):
    pdf_merger = PdfFileMerger()
    for path in input_paths:
        pdf_merger.append(path)
    with open(output_path, 'wb') as fileobj:
        pdf_merger.write(fileobj)

paths = glob.glob('input_*.pdf') # select all files with names beginning with input
paths.sort() # sorts the pages by file name
merger((f'_{orderType}_output.pdf'), paths) # merges all renamed pages
print ('Created: _{}_output.pdf'.format(orderType)) # logs the filename of merged pdf

for f in glob.glob("input*.pdf"): # remove all files with names beginning with input
    os.remove(f)

# file compression
reader = PdfFileReader(f'_{orderType}_output.pdf')
writer = PdfFileWriter()

for page in reader.pages:
    page.compressContentStreams()  # This is CPU intensive!
    writer.addPage(page)

with open(f'_{orderType}_output.pdf', "wb") as f:
    writer.write(f)
#sbRoute_20230223 for bread, dd, retail orders
import pdfplumber
import PyPDF2
from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger
import os
import glob
from datetime import datetime
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import red
from reportlab.lib.colors import Color, red
from config.routes import routes
from config.customer_names import customer_names

orderType = str(input("File name: ")) # user input filename and saves to orderType variable
os.rename(f"{orderType}.pdf","input.pdf") # rename file to input.pdf
lastPage = PyPDF2.PdfFileReader(open('input.pdf', 'rb')).numPages # number of pages in pdf
page_id = 1 # fix for overwriting orders >1 page long
outputName = ""

with pdfplumber.open('input.pdf') as pdf: # opens inputted pdf
    for i in range(lastPage): # iterate to lastPage
        curr_page = pdf.pages[i] # assign curr_page variable
        customerId = curr_page.extract_text()[10:16] # extract customer ID
        route = routes.get(f"{customerId}") # get route from dictionary
        customer = customer_names.get(f"{customerId}") # get customer from dictionary
        path = ('input.pdf') # set path variable
        pdf_reader = PdfFileReader(path)
        pdf_writer = PdfFileWriter()
        pdf_writer.addPage(pdf_reader.getPage(i)) # creates the page
        output_filename = 'input_{}_{}_{}.pdf'.format( # file name convention
            route, customerId, page_id)
        with open(output_filename, 'wb') as out: # writes file name
            pdf_writer.write(out)
        print('Created: {}'.format(output_filename)) # logs the pages as renaming finishes

        # draw with canvas
        redtransparent = Color( 255, 0, 0, alpha=0.4)
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFillColor(redtransparent)

        # draw bottom text
        can.setFont("Helvetica-Bold", 110)
        if (len(customer) == 6):
            can.setFont("Helvetica-Bold", 185)
        if (len(customer) >= 9):
            can.setFont("Helvetica-Bold", 95)
        can.drawString(12, 18, f'{customer}')
        # can.drawString(12, 18, f'ROUTE {route} - {customer}') # draw text on bottom

        # draw top text
        can.setFont("Helvetica-Bold", 40)
        can.drawString(12, 685, f'ROUTE {route} - {customer}')

        can.save()
        #move to the beginning of the StringIO buffer
        packet.seek(0)
        # create a new PDF with Reportlab
        new_pdf = PdfFileReader(packet)
        # read your existing PDF
        existing_pdf = PdfFileReader(open(output_filename, "rb"))
        output = PdfFileWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page2 = existing_pdf.getPage(0)
        page2.mergePage(new_pdf.getPage(0))
        output.addPage(page2)
        outputStream = open(f'canvas_{route}_{customerId}_{page_id}.pdf', "wb")
        output.write(outputStream)
        print(f'Created: canvas_{route}_{customerId}_{page_id}.pdf')
        outputStream.close()
        page_id += 1

# remove input files
for f in glob.glob("input*.pdf"):
    os.remove(f)

def merger(output_path, input_paths):
    pdf_merger = PdfFileMerger()
    for path in input_paths:
        pdf_merger.append(path)
    with open(output_path, 'wb') as fileobj:
        pdf_merger.write(fileobj)

paths = glob.glob('canvas_*.pdf')
paths.sort()
now = datetime.now()
current_time = now.strftime("%H_%M_%S")
merger((f'_{orderType}_output_{current_time}.pdf'), paths)
outputName = (f'_{orderType}_output_{current_time}.pdf')
print ('Created: _{}_output_{}.pdf'.format(orderType, current_time))

# remove canvas files
for f in glob.glob("canvas*.pdf"):
    os.remove(f)

# file compression
reader = PdfFileReader(f'{outputName}')
writer = PdfFileWriter()

for page in reader.pages:
    page.compressContentStreams()  # This is CPU intensive!
    writer.addPage(page)

with open(f'{outputName}', "wb") as f:
    writer.write(f)
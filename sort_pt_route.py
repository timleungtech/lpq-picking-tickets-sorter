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

dictroute = {
  "000113": "3",
  "000114": "1",
  "000118": "2",
  "000120": "3",
  "000123": "1",
  "000127": "2",
  "000130": "3",
  "000134": "1",
  "000136": "1",
  "000138": "3",
  "000142": "2",
  "000144": "1",
  "000146": "1",
  "000148": "2",
  "000149": "2",
  "000151": "4",
  "000153": "3",
  "000154": "1",
  "000156": "3",
  "000401": "4",
  "000402": "4",
  "000403": "4",
  "003002": "3",
  "003003": "1",
  "003004": "1",
  "003005": "1",
  "003006": "3",
  "003007": "2",
  "003008": "3",
  "003009": "2",
  "003010": "2",
  "003011": "2",
  "003013": "3"
}

dictCustomer = {
  "000113": "SOHO  ",
  "000114": "MADISON",
  "000118": "FIRST AVE",
  "000120": "  8TH ",
  "000123": "LINCOLN",
  "000127": "BRYANT ",
  "000130": "TRIBECA",
  "000134": "MINERAL",
  "000136": "   88 ",
  "000138": "BLEECKER",
  "000142": " GCW  ",
  "000144": "  E97 ",
  "000146": "  E83 ",
  "000148": "  E65 ",
  "000149": "  W55 ",
  "000151": "ROOSEVELT",
  "000153": "85 BROAD",
  "000154": "SAILBOAT",
  "000156": "SOUTH END",
  "000401": "N.CANAAN",
  "000402": "  RYE ",
  "000403": "GREENWICH",
  "003002": "921 BWAY",
  "003003": "   58 ",
  "003004": "   87 ",
  "003005": "   76 ",
  "003006": "JORALEMON",
  "003007": "   56 ",
  "003008": "   36 ",
  "003009": "   38 ",
  "003010": "   43 ",
  "003011": "   41 ",
  "003013": "   29 "
}

orderType = str(input("File name: ")) # user input filename and saves to orderType variable
os.rename(f"{orderType}.pdf","input.pdf") # rename file to input.pdf
lastPage = PyPDF2.PdfFileReader(open('input.pdf', 'rb')).numPages # number of pages in pdf
page_id = 1 # fix for overwriting orders >1 page long
outputName = ""

with pdfplumber.open('input.pdf') as pdf: # opens inputted pdf
    for i in range(lastPage): # iterate to lastPage
        curr_page = pdf.pages[i] # assign curr_page variable
        customerId = curr_page.extract_text()[10:16] # extract customer ID
        route = dictroute.get(f"{customerId}") # get route from dictionary
        customer = dictCustomer.get(f"{customerId}") # get customer from dictionary
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
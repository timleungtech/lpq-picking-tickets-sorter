#sort invoices by customer

import glob
import pdfplumber
import os
from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger
import PyPDF2
from config.routes import routes
from config.customer_names import customer_names

page_id = 1 # fix for orders >1 page long
output_file_name = ""

get_file = str(input("File name: "))
os.rename(f"{get_file}.pdf","input.pdf")

pdfFileObj = open('input.pdf', 'rb')
pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
last_page = pdfReader.numPages

with pdfplumber.open('input.pdf') as pdf:
    # fix blank last page
    if pdf.pages[last_page - 1].extract_text().find('Customer: ') == -1:
        last_page = last_page - 1

    for i in range(last_page):
        curr_page = pdf.pages[i]
        parsed_text = curr_page.extract_text()

        customer_idx = parsed_text.index('Customer: ') + len('Customer: ')
        customer_idx_end = customer_idx
        while customer_idx_end < len(parsed_text) and parsed_text[customer_idx_end].isdigit():
            customer_idx_end += 1
        customer_id = parsed_text[customer_idx:customer_idx_end]

        route = routes.get(customer_id)
        customer_name = customer_names.get(customer_id)
        path = ('input.pdf')
        pdf_reader = PdfFileReader(path)
        pdf_writer = PdfFileWriter()
        pdf_writer.addPage(pdf_reader.getPage(i))
        output_page_name = 'input_{}_{}_{}.pdf'.format(
            route, customer_id, page_id)
        with open(output_page_name, 'wb') as out:
            pdf_writer.write(out)
        print(f'Created: {output_page_name}')
        page_id += 1

def merger(output_path, input_paths):
    pdf_merger = PdfFileMerger()
    for path in input_paths:
        pdf_merger.append(path)
    with open(output_path, 'wb') as fileobj:
        pdf_merger.write(fileobj)

if __name__ == '__main__':
    paths = glob.glob('input_*.pdf')
    paths.sort()
    merger((f'_{get_file}_output.pdf'), paths)
    print ('Created: _{}_output.pdf'.format(get_file))

for f in glob.glob("input*.pdf"):
    os.remove(f)

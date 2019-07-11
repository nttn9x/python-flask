# from binascii import b2a_hex
# import base64


# from flask import abort
# from pdfminer.converter import PDFPageAggregator
# from pdfminer.layout import (LAParams, LTChar, LTFigure, LTImage, LTTextBox,
#                              LTTextLine)
# from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines
# from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
# from pdfminer.pdfpage import PDFPage
# from pdfminer.pdfparser import PDFParser

# from services import document_service
# from utils.pdf_util import create_file, pdf_to_images
# from .image_controller import extract_text


# class Data:
#     def __init__(self, index, position, value, data_type):
#         self.index = index
#         self.position = position
#         self.value = value
#         self.data_type = data_type


# class FileData:
#     def __init__(self, content, images):
#         self.content = content
#         self.images = images


# def with_pdf(file_name, base64_string, fn, pdf_pwd, *args):
#     """Open the pdf document, and apply the function, returning the results"""
#     fp = None
#     result = None
#     try:
#         path_pdf_file = create_file(file_name, base64_string)

#         # open the pdf file
#         fp = open(path_pdf_file, 'rb')

#         # create a parser object associated with the file object
#         parser = PDFParser(fp)
#         # create a PDFDocument object that stores the document structure
#         doc = PDFDocument(parser, pdf_pwd)

#         # connect the parser and document objects
#         parser.set_document(doc)

#         if doc.is_extractable:
#             # apply the function and return the result
#             result = fn(doc, *args)
#         else:
#             path_images = pdf_to_images(file_name)
#             results = []
#             for i in path_images:
#                 results.append(extract_text(i))

#             result = "".join(results)
#     except IOError as e:
#         # the file doesn't exist or similar problem
#         abort(500, e)
#     finally:
#         # close the pdf file
#         if fp is not None:
#             fp.close()
#     return result

# ###
# # Table of Contents
# ###


# def _parse_toc(doc):
#     """With an open PDFDocument object, get the table of contents (toc) data
#     [this is a higher-order function to be passed to with_pdf()]"""
#     toc = []
#     try:
#         outlines = doc.get_outlines()
#         for (level, title, dest, a, se) in outlines:
#             toc.append((level, title))
#     except PDFNoOutlines:
#         pass
#     return toc


# def get_toc(file_name, pdf_doc, pdf_pwd=''):
#     """Return the table of contents (toc), if any, for this pdf file"""
#     return with_pdf(file_name, pdf_doc, _parse_toc, pdf_pwd)


# ###
# # Extracting Images
# ###

# def write_file(filename, filedata, flags='w'):
#     if filedata is None:
#         return ""

#     return base64.b64encode(filedata).decode('utf-8')


# def determine_image_type(stream_first_4_bytes):
#     """Find out the image file type based on the magic number comparison of the first 4 (or 2) bytes"""
#     file_type = None
#     bytes_as_hex = b2a_hex(stream_first_4_bytes)

#     if bytes_as_hex.startswith(b'ffd8'):
#         file_type = '.jpeg'
#     elif bytes_as_hex == '89504e47':
#         file_type = '.png'
#     elif bytes_as_hex == '47494638':
#         file_type = '.gif'
#     elif bytes_as_hex.startswith(b'424d'):
#         file_type = '.bmp'

#     return file_type


# def save_image(lt_image, page_number):
#     """Try to save the image data from this LTImage object, and return the file name, if successful"""
#     base64 = None
#     file_type = None
#     if lt_image.stream:
#         file_stream = lt_image.stream.get_rawdata()
#         if file_stream:
#             file_type = determine_image_type(file_stream[0:4])
#             if file_type:
#                 file_name = ''.join(
#                     [str(page_number), '_', lt_image.name, file_type])

#                 base64 = write_file(file_name, file_stream, flags='wb')

#     return base64, file_type


# ###
# # Extracting Text
# ###

# def to_bytestring(s, enc='utf-8'):
#     """Convert the given unicode string to a bytestring, using the standard encoding,
#     unless it's already a bytestring"""
#     if s:
#         if isinstance(s, str):
#             return s
#         else:
#             return s.encode(enc)


# def parse_lt_objs(lt_objs, page_number, full_content, images):

#     for lt_obj in lt_objs:
#         if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine) or isinstance(lt_obj, LTChar):
#             full_content.append(lt_obj.get_text())
#         elif isinstance(lt_obj, LTImage):
#             # an image, so save it to the designated folder, and note its place in the text
#             base64, file_type = save_image(lt_obj, page_number)
#             if base64:
#                 images.append(Data(0, lt_obj.bbox, base64, file_type))
#         elif isinstance(lt_obj, LTFigure):
#             # LTFigure objects are containers for other LT* objects, so recurse through the children
#             parse_lt_objs(lt_obj, page_number, full_content,  images)


# def _parse_pages(doc):
#     """With an open PDFDocument object, get the pages and parse each one
#     [this is a higher-order function to be passed to with_pdf()]"""
#     rsrcmgr = PDFResourceManager()
#     laparams = LAParams()
#     device = PDFPageAggregator(rsrcmgr, laparams=laparams)
#     interpreter = PDFPageInterpreter(rsrcmgr, device)

#     content = []
#     images = []
#     for i, page in enumerate(PDFPage.create_pages(doc)):
#         interpreter.process_page(page)
#         # receive the LTPage object for this page
#         layout = device.get_result()
#         # layout is an LTPage object which may contain child objects like LTTextBox, LTFigure, LTImage, etc.
#         parse_lt_objs(layout, (i+1), content, images)

#     # data = FileData("".join(content), images)

#     # json_string = json.dumps(data, default=lambda x: x.__dict__)

#     return "".join(content)


# def process(file_name, base64_string, pdf_pwd=''):
#     """Process each of the pages in this pdf file and return a list of strings representing the text found in each page"""
#     content = with_pdf(file_name, base64_string, _parse_pages, pdf_pwd)

#     document_service.insert(file_name, content)

#     return content

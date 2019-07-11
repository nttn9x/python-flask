from utils.google_vision import detect_document

# import json
# import os

# import cv2
# import pytesseract

# from utils import image_util


# class FileData:
#     def __init__(self, full_content):
#         self.full_content = full_content


# def extract_text(file_name, lang="eng"):
#     file = cv2.imread(file_name)

#     gray = cv2.cvtColor(file, cv2.COLOR_BGR2GRAY)

#     noise = image_util.remove_noise(gray.copy())

#     image = image_util.remove_line(noise.copy())

#     extract_text = pytesseract.image_to_string(
#         image, lang=lang, config="--oem 1 --psm 3")

#     # connected = findText(image.copy())

#     # contours, _ = cv2.findContours(
#     #     connected, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#     # for idx in range(len(contours)):
#     #     x, y, w, h = cv2.boundingRect(contours[idx])
#     #     # Don't plot small false positives that aren't text
#     #     if w < 15 and h < 15:
#     #         continue

#     #     roi = image[y:y + h, x:x + w]

#     #     cv2.rectangle(file, (x, y), (x+w, y+h), (0, 255, 0), 1)

#     data = FileData(extract_text)

#     json_string = json.dumps(data, default=lambda x: x.__dict__)

#     if os.path.exists(file_name):
#         os.remove(file_name)

#     return json_string


# def process_by_tesseract(base64_string, lang="eng"):
#     file_name = image_util.create_file(base64_string)

#     return extract_text(file_name, lang)

def process_by_google_vision(file_path_input: str):
    return detect_document(file_path_input)

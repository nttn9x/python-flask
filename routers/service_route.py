import ast
import datetime
import json
import logging
import os
import threading

import requests as rq
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Blueprint, request
from flask_restplus import Api, Resource, fields

from common import init_config
from common.database import config
from controllers.extract.image_controller import process_by_google_vision

blueprint = Blueprint('ServiceRoute', __name__)
api = Api(blueprint)

init_config()


# logging.basicConfig(filename='ocr_data.log', level=logging.DEBUG)
# logger = logging.getLogger('tcpserver')
# logger.warning('data OCR: %s', {'asda': 'vavvva'})


@api.route('/autoservice')
class AutoService(Resource):
    is_running = False
    scheduler = BackgroundScheduler()
    job = None
    thread_run_scheduler = None
    url_unique_service = config["unique_service"]["url"]

    def post(self):
        data = request.args
        if self.is_running is None:
            self.is_running = False

        status_action = 'no action'

        if (data.get('action') == 'start'):
            status_action = self.start_service()
        elif (data.get('action') == 'stop'):
            status_action = self.stop_service()

        return {'Message': status_action}

    def start_service(self):
        if self.scheduler.get_job('extract_doc') is not None:
            return 'Service is Running'

        # apscheduler.schedulers.base.STATE_STOPPED = 0
        # apscheduler.schedulers.base.STATE_RUNNING = 1
        # apscheduler.schedulers.base.STATE_PAUSED = 2

        # self.thread_run_scheduler = threading.Thread(target=self.init_job, args=())
        # self.thread_run_scheduler.start()

        self.init_job()

        return 'Service is started'

    def init_job(self):
        print(datetime.datetime.now().time(),
              ' init_job', self.url_unique_service)

        try:
            self.start_service_extract()
        except Exception as err:
            raise err

        try:
            self.scheduler.add_job(
                self.start_service_extract, 'cron', minute='*', id='extract_doc')
            if(self.scheduler.state != 1):
                # Start the scheduler
                self.scheduler.start()
        except Exception as err:
            raise err

        return

    def stop_service(self):
        print(datetime.datetime.now().time(),
              ' (stop_service) STATE Job ', self.scheduler.state)
        # if(self.scheduler.state == 1):
        self.is_running = False
        try:
            if self.scheduler.get_job('extract_doc') is not None:
                try:
                    self.scheduler.remove_job('extract_doc')
                except Exception as err:
                    print('Error remove Job')
            else:
                return 'Service is not running'
        except Exception as err:
            raise err

        return 'Service is stopped'

    def start_service_extract(self):
        if self.is_running == True:
            return
        self.is_running = True
        self.extract_data_of_documment(self.url_unique_service)

    def extract_data_of_documment(self, _url_unique_service):
        print(datetime.datetime.now().time(),
              ' extract_data_of_documment: ' + _url_unique_service)
        try:
            doc_arr = self.get_document_to_ocr(_url_unique_service)
            if (doc_arr is None):
                print('No data ready to OCR')
                self.is_running = False
                return
            else:
                for docs in doc_arr:
                    if self.is_running == False:
                        break
                    if (docs['PathFolder'] is None or docs['FileName'] is None):
                        print('Path of Image not found from DB.')
                        print(docs)
                        continue
                    full_path = str(docs['PathFolder']) + \
                        '\\' + str(docs['FileName'])
                    print(full_path)
                    if (os.path.exists(full_path)):
                        data_ocr = process_by_google_vision(full_path)
                        ocr_text = ''
                        if 'full_text_annotation' in data_ocr:
                            if 'text' in data_ocr['full_text_annotation']:
                                ocr_text = data_ocr['full_text_annotation']['text']

                        if ocr_text is None or len(ocr_text) == 0:
                            if 'text_annotations' in data_ocr:
                                try:
                                    text_arr = data_ocr['text_annotations'][0]['description']
                                    ocr_text = text_arr
                                except Exception as err_parse:
                                    raise err_parse
                        try:
                            data_ocr["full_text_annotation"]["text"] = "<br />".join(
                                data_ocr["full_text_annotation"]["text"].split("\n"))
                            data_ocr["full_text_annotation"]["text"] = data_ocr["full_text_annotation"]["text"].replace(
                                '\\', '\\\\')
                            data_ocr["full_text_annotation"]["text"] = data_ocr["full_text_annotation"]["text"].replace(
                                '"', '')

                            len_text_anno = len(data_ocr["text_annotations"])
                            print('Length of Array Text-Annotation: ' +
                                  str(len_text_anno))
                            for i in range(len_text_anno):
                                data_ocr["text_annotations"][i]["description"] = "<br />".join(
                                    data_ocr["text_annotations"][i]["description"].split("\n"))
                                data_ocr["text_annotations"][i]["description"] = data_ocr["text_annotations"][i]["description"].replace(
                                    '"', '')
                                data_ocr["text_annotations"][i]["description"] = "\\\\".join(
                                    data_ocr["text_annotations"][i]["description"].split("\\"))

                            len_page = len(
                                data_ocr["full_text_annotation"]["pages"])
                            for p in range(len_page):
                                len_block = len(
                                    data_ocr["full_text_annotation"]["pages"][p]["blocks"])
                                for b in range(len_block):
                                    len_para = len(
                                        data_ocr["full_text_annotation"]["pages"][p]["blocks"][b]["paragraphs"])
                                    for pa in range(len_para):
                                        len_words = len(
                                            data_ocr["full_text_annotation"]["pages"][p]["blocks"][b]["paragraphs"][pa]["words"])
                                        for w in range(len_words):
                                            len_symbols = len(
                                                data_ocr["full_text_annotation"]["pages"][p]["blocks"][b]["paragraphs"][pa]["words"][w]["symbols"])
                                            for sb in range(len_symbols):
                                                txt_local = data_ocr["full_text_annotation"]["pages"][p]["blocks"][
                                                    b]["paragraphs"][pa]["words"][w]["symbols"][sb]["text"]
                                                if (txt_local is not None):
                                                    txt_local = txt_local.replace(
                                                        '"', '')
                                                    txt_local = "\\\\".join(
                                                        txt_local.split("\\"))
                                                    data_ocr["full_text_annotation"]["pages"][p]["blocks"][b][
                                                        "paragraphs"][pa]["words"][w]["symbols"][sb]["text"] = txt_local

                            # full_text_annotation    pages[] blocks[] paragraphs[] words[] symbols[] text

                        except Exception as err_parse:
                            raise err_parse

                        docs['OCRJson'] = data_ocr

                        docs['OCRText'] = "<br />".join(ocr_text.split("\n"))
                        docs['OCRText'] = docs['OCRText'].replace('\\', '\\\\')
                        docs['OCRText'] = docs['OCRText'].replace('"', '')

                        if 'IdDocumentContainerOcr' in docs:
                            del docs['IdDocumentContainerOcr']
                        del docs['PathFolder']
                        del docs['FileName']
                        docs['IdRepDocumentContainerOcrType'] = '1'
                        docs['IdRepDocumentType'] = '1'
                        docs['IsActive'] = '1'

                        # logger.warning('data OCR: %s', docs)
                        try:
                            self.save_data_ocr(_url_unique_service, docs)
                        except Exception as err_save:
                            raise err_save
                            self.is_running = False
                    else:
                        print('Path Image not EXIST :' + full_path)

                    if self.is_running == False:
                        break
        except Exception as err:
            raise err
            # exist_data = False

        self.is_running = False
        return

    def get_document_to_ocr(self, _url_unique_service):
        print('start get doc')
        data = {
            "Request":
                {
                    "ModuleName"	: "GlobalModule",
                    "ServiceName"	: "GlobalService",
                    "Data":
                    {
                        '''"MethodName"'''	: '''"SpB06GetDocumentContainer"''',
                        '''"CrudType"'''		: '''"Read"''',
                        '''"Object"''': '''"DocumentContainerScansForFile"''',
                        '''"AppModus"''': '''"0"''',
                        '''"IdLogin'"''': '''"1"''',
                        '''"LoginLanguage"''': '''"1"''',
                        '''"IdApplicationOwner"''': '''"1"''',
                        '''"GUID"''': '''"value"''',
                        '''"IdDocumentContainerFileType"''': '''"3"''',
                        '''"TopRows"''': '''"10"'''
                    }
                }
        }

        response = rq.post(_url_unique_service, json=data, headers={
            'Content-Type': 'application/json', 'Connection': 'close'})
        # print('after get doc')
        docs = None
        if ('Data' in (response.json())):
            data_record = (response.json()['Data'])
            if(data_record is not None):
                records = ast.literal_eval(data_record)
                if(len(records) > 0 and len(records[0]) > 0):
                    docs = records[0]

        return docs

    def save_data_ocr(self, _url_unique_service, data_ocr):
        data_str = json.dumps(data_ocr).replace('"', '\\\"')
        js_doc = {
            '\\\"DocumentContainerOCR\\\"': [data_str]
        }

        data = {
            "Request":
                {
                    "ModuleName"	: "GlobalModule",
                    "ServiceName"	: "GlobalService",
                    "Data":
                    {
                        '''"MethodName"'''	: '''"SpB06CallDocumentContainer"''',
                        '''"Object"''': '''"DocumentContainerOCR"''',
                        '''"AppModus"''': '''"0"''',
                        '''"IdLogin"''': '''"1"''',
                        '''"LoginLanguage"''': '''"1"''',
                        '''"IdApplicationOwner"''': '''"1"''',
                        '''"GUID"''': '''"421a143a-d2de-4dfe-8752-5b5dfda84ecc"''',
                        '''"JSONDocumentContainerOCR"''': js_doc
                    }
                }
        }
        # json.dumps
        print('execute save_data_ocr ')
        # print(data)
        #logger.warning('data OCR: %s', data)
        response = rq.post(_url_unique_service, json=data, headers={
            'Content-Type': 'application/json', 'Connection': 'close'})
        print('response SAVE: ' + repr(response))
        return response

    def _test_get_document_to_ocr(self, url_unique_service):
        print('_test_get_document_to_ocr')
        data = {
            "Request":
                {
                    "ModuleName"	: "GlobalModule",
                    "ServiceName"	: "GlobalService",
                    "Data":
                    {
                        '''"MethodName"'''	: '''"SpB06GetDocumentContainer"''',
                        '''"CrudType"'''		: '''"Read"''',
                        '''"Object"''': '''"DocumentContainerScansForFile"''',
                        '''"AppModus"''': '''"0"''',
                        '''"IdLogin'"''': '''"1"''',
                        '''"LoginLanguage"''': '''"1"''',
                        '''"IdApplicationOwner"''': '''"1"''',
                        '''"GUID"''': '''"value"''',
                        '''"TopRows"''': '''"1"''',
                    }
                }
        }

        response = rq.post(url_unique_service, json=data, headers={
            'Content-Type': 'application/json'})
        # print("status_code:" + str(response.status_code))
        print(((response.json())))
        # print(json.loads(str(response.json())))
        lx = ast.literal_eval(response.json()['Data'])
        print(len(lx))
        print(type(lx[0]))
        print((lx[0][0]))
        print(type(lx[0][0]))
        print(type((response.json()['Data'])))
        print((json.loads(response.json())))
        docs = ''
        if ('Data' in (response.json())):
            data_record = (response.json()['Data'])
            if(data_record != None):
                records = ast.literal_eval(data_record)
                if(len(records) > 0 and len(records[0]) > 0):
                    docs = records[0][0]

        print(docs)

        # print('response: ' + repr(response))
        return response

    def _test_save_data_ocr(self, url_unique_service, data_ocr):

        # ocr_text = {
        #     '''"Name1"''': '''"ocr 001"''',
        #     '''"Name2"''': '''"ocr 002"''',
        #     '''"Name3"''': '''"no data here"'''
        # }

        # data_js = {
        #     '''"IdDocumentContainerScans"''': '''"91"''',
        #     '''"IdRepDocumentContainerOcrType"''': '''"1"''',
        #     '''"IdRepDocumentType"''': '''"1"''',
        #     '''"OCRText"''': {},
        #     '''"OCRJson"''': {},
        #     '''"IsActive"''': '''"1"'''
        # }

        JSONDocumentContainerOCR = {
            '''"DocumentContainerOCR"''': [data_ocr]
        }

        data = {
            "Request":
                {
                    "ModuleName"	: "GlobalModule",
                    "ServiceName"	: "GlobalService",
                    "Data":
                    {
                        '''"MethodName"'''	: '''"SpB06CallDocumentContainer"''',
                        '''"Object"''': '''"DocumentContainerOCR"''',
                        '''"AppModus"''': '''"0"''',
                        '''"IdLogin'"''': '''"1"''',
                        '''"LoginLanguage"''': '''"1"''',
                        '''"IdApplicationOwner"''': '''"1"''',
                        '''"GUID"''': '''"421a143a-d2de-4dfe-8752-5b5dfda84ecc"''',
                        '''"JSONDocumentContainerOCR"''': json.dumps(JSONDocumentContainerOCR)
                    }
                }
        }

        # print("json:" + str(data))

        response = rq.post(url_unique_service, json=data, headers={
            'Content-Type': 'application/json'})
        # print("status_code:" + str(response.status_code))
        # print("json:" + str(response.json()))
        # print('response: ' + repr(response))
        return response

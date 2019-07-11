"""convert"""

from flask import Blueprint, request
from flask_restplus import Api, Resource, fields
from controllers.convert.convert_controller import pdf_to_images, tiff_to_images
from utils.http_util import format_respond

blueprint = Blueprint('ConvertRoute', __name__)
api = Api(blueprint)

parser = api.model('Resource', {
    'file_path_input': fields.String(description='file_path_input', required=True),
    'file_path_output': fields.String(description='file_path_output', required=True)
})


@api.route("/pdf-2-jpeg")
class PDFToJPEG(Resource):

    @api.expect(parser, validate=True)
    def post(self):
        data = request.get_json()

        return format_respond(pdf_to_images, data['file_path_input'], data['file_path_output'])


@api.route("/tiff-2-jpeg")
class TIFFToJPEG(Resource):
    @api.expect(parser, validate=True)
    def post(self):
        data = request.get_json()

        return format_respond(tiff_to_images, data['file_path_input'], data['file_path_output'])

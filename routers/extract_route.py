""" extract_route.py """

from flask import Blueprint, request
from flask_restplus import Api, Resource, fields

from controllers.extract.image_controller import process_by_google_vision
from utils.http_util import format_respond

blueprint = Blueprint('ExtractRoute', __name__)
api = Api(blueprint)


@api.route("/image")
class ExtractText(Resource):
    parser = api.model('Resource', {
        'file_path': fields.String(description='file_path', required=True),
    })

    @api.expect(parser, validate=True)
    def post(self):
        data = request.get_json()
        file_path = data['file_path']

        return format_respond(process_by_google_vision, file_path)

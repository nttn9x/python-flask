from flask import Blueprint, request
from flask_restplus import Api, Resource, fields

from controllers import document_controller

blueprint = Blueprint('DocumentRoute', __name__)
api = Api(blueprint)


@api.route("/document")
class DocumentList(Resource):
    parser_get = api.parser()
    parser_get.add_argument('start', type=int, location='args')
    parser_get.add_argument('end', type=int, location='args')

    parser_post = api.model('Resource', {
        'file_path': fields.String(description='file_path', required=True),
        'content': fields.String(description='content', required=True)
    })

    @api.expect(parser_get, validate=True)
    def get(self):
        data = self.parser_get.parse_args()

        start = None
        if hasattr(data, "start"):
            start = data['start']

        end = None
        if hasattr(data, "end"):
            end = data['end']

        return document_controller.find(start, end)

    @api.expect(parser_post, validate=True)
    def post(self):
        data = request.get_json()

        return document_controller.insert(data["file_path"], data["content"])

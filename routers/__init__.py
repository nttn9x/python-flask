""" routes """

from routers.convert_route import blueprint as convert_api
from routers.document_route import blueprint as document_api
from routers.extract_route import blueprint as extract_api
from routers.service_route import blueprint as service_api


def init_routers(app):
    """ create routers """

    # retrieve data from the database
    app.register_blueprint(document_api, url_prefix='/api/data')

    # processing files
    app.register_blueprint(extract_api, url_prefix='/api/extract')
    app.register_blueprint(convert_api, url_prefix='/api/convert')

    app.register_blueprint(service_api, url_prefix='/api/service')

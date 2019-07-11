
def detect_document(path):
    """Detects document features in an image."""
    from google.cloud import vision
    from google.protobuf.json_format import MessageToDict
    from google.cloud import storage

    storage_client = storage.Client.from_service_account_json(
        'apikey.json')

    client = vision.ImageAnnotatorClient()

    with open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.document_text_detection(image=image)

    return MessageToDict(response, preserving_proto_field_name=True)

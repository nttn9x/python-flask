import base64


def create_file(filename, base64_string):
    imgdata = base64.b64decode(base64_string)

    filename = 'files/{}.pdf'.format(filename)

    with open(filename, 'wb') as f:
        f.write(imgdata)

    return filename

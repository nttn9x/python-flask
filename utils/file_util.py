import os


def get_filename(file_path: str) -> (str, str):
    basename = os.path.basename(file_path)
    filename, extension = os.path.splitext(basename)

    return filename, extension.lower()


def create_folder(path: str) -> bool:
    try:
        if not os.path.exists(path):
            os.mkdir(path)

        return True
    except Exception as err:
        print('Something went wrong:', str(err))
        return False


def delete_files(paths: []):
    if paths is None or not paths:
        pass

    for p in paths:
        delete_file(p)


def delete_file(path: str):
    try:
        os.remove(path)
    except FileNotFoundError as err:
        print('FileNotFoundError:', str(err))
    except Exception as err:
        print('Something went wrong:', str(err))

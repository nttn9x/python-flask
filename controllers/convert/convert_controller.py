"""convert"""

from PIL import Image, ImageSequence
from pdf2image import convert_from_path
from utils.file_util import create_folder, delete_files, get_filename
from exceptions.file_exeption import WrongExtension


def pdf_to_images(file_path_input: str, file_path_output: str) -> []:
    """
        Convert file pdf to images
    """
    filename, extension = get_filename(file_path_input)
    if "pdf" not in extension:
        raise WrongExtension("Only .pdf file is allowed")

    images = convert_from_path(file_path_input)

    path_images = []

    if not images:
        return path_images

    try:
        if len(images) > 1:
            folder_name = f"{file_path_output}\\{filename}"

            create_folder(folder_name)

            for i in images:
                path = f"{folder_name}\\{filename}_{len(path_images)}.jpeg"

                i.save(path)

                path_images.append(path)
        else:
            images[0].save(path_images[0])

            path_images.append(f"{file_path_output}\\{filename}.jpeg")
    except Exception as err:
        # delete all file if error happens
        delete_files(path_images)

        raise err

    return path_images


def tiff_to_images(file_path_input: str, file_path_output: str) -> []:
    """
        Convert file tiff to images
    """
    filename, extension = get_filename(file_path_input)
    if "tif" not in extension:
        raise WrongExtension("Only .tif file is allowed")

    path_images = []

    try:
        with Image.open(file_path_input) as im:
            ite = ImageSequence.Iterator(im)

            if im.n_frames > 1:
                folder_name = f"{file_path_output}\\{filename}"

                create_folder(folder_name)

                for i, page in enumerate(ite):
                    path = f"{folder_name}\\{filename}_{i}.jpeg"

                    page.save(path)
                    path_images.append(path)
            else:
                im.save(f"{file_path_output}\\{filename}.jpeg")

                path_images.append(f"{file_path_output}\\{filename}.jpeg")
    except Exception as err:
        # delete all file if error happens
        delete_files(path_images)

        raise err

    return path_images

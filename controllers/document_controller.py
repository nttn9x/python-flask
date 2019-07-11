from services import document_service


def find(start: int = 0, end: int = 0):
    return document_service.find(start, end)


def insert(file_path: str, content: str) -> str:
    return document_service.insert(file_path, content)

import datetime
from flask import abort, jsonify
from pymongo.errors import ConnectionFailure

from common.database import get_table_document


def insert(file_name, content) -> str:

    try:
        created_date = datetime.datetime.utcnow()

        document_id = get_table_document().insert({
            "FileName": file_name,
            "Folder": "",
            "Content": content,
            "Tags": [],
            "Keywords": [],
            "Category": [],
            "CreatedDate": created_date.strftime("%Y/%m/%d %H:%M:%S")
        })

        return {"documentId": str(document_id)}
    except ConnectionFailure as ex:
        abort(500, ex)

    return None


def find(start, end):
    skip = start if start else 0
    limit = end if end else 0

    documents = []
    try:
        cursor = get_table_document().find().skip(skip).limit(limit)

        for document in cursor:
            document['_id'] = str(document['_id'])
            documents.append(document)

        return jsonify(documents)
    except ConnectionFailure as ex:
        abort(500, ex)

    return documents

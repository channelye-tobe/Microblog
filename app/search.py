from flask import current_app

def add_to_index(index, model):
    if not current_app.elasticsearch:
        return
    body={}
    for field in model.__searchable__:
        body[field] = getattr(model, field, None)
    current_app.elasticsearch.index(index=index, doc_type=index, id=model.id, body=body)

def delete_from_index(index, model):
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, doc_type=index, id=model.id)

def search_index(index, query, page, per_page):
    if not current_app.elasticsearch:
        return [], 0
    search = current_app.elasticsearch.search(
        index=index, doc_type=index,
        body={'query':{'multi_match':{'query':query, 'fields':['*']}},
            'from': (page - 1)* per_page + 1, 'size': per_page})
    ids = [int(hit['_id'])for hit in search['hits']['hits']]
    return ids, search['hits']['total']

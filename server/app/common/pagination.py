from flask import request


def paginate(query, schema, default_limit=20, max_limit=100):
    page = request.args.get("page", 1, type=int)
    limit = min(request.args.get("limit", default_limit, type=int), max_limit)

    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    return {
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
        "items": schema.dump(pagination.items, many=True),
    }
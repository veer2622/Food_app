from sqlalchemy.orm import Query

def pagination(request:Query, page:int =1, limit:int=10):
    offset=(page-1)*limit
    
    total= request.count()
    
    data = request.offset(offset).limit(limit).all()
    
    return {
        "page":page,
        "limit":limit,
        "total_query": total,
        "total_page":(total + limit-1)//limit,
        "data": data
    }
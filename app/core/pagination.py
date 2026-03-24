from fastapi_pagination import Params

class SubjectPagination(Params):
    page: int = 1
    size: int = 10
    max_size: int = 20
from fastapi_pagination import Params

class SubjectPagination(Params):
    page: int = 1
    size: int = 10
    max_size: int = 20

class TopicPagination(Params):
    page: int = 1
    size: int = 25
    max_size: int = 50
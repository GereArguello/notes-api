from fastapi_pagination import Params

class SubjectPagination(Params):
    page: int = 1
    size: int = 9
    max_size: int = 9

class TopicPagination(Params):
    page: int = 1
    size: int = 20
    max_size: int = 30

class PagePagination(Params):
    page: int = 1
    size: int = 20
    max_size: int = 30
from fastapi_pagination import Page, paginate ,Params
class CustomParams(Params):
    def __init__(self, page: int = 1, size: int = 20):
        super().__init__(page=page, size=size)
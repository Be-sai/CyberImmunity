class WebServer:
    def __init__(self):
        self.requests = []

    def process_request(self, request):
        self.requests.append(request)
        print(f"Запрос обработан: {request}")
        return True
import logging

class RequestLogMiddleware:
     def __init__(self, get_response):
         self.get_response = get_response
         self.logger = logging.getLogger('django.request')
         
     def __call__(self, request):
         response = self.get_response(request)
         self.log_request(request, response)
         return response
    
     def log_request(self, request, response):
         self.logger.info(
              f"Method: {request.method}, Path: {request.path}, Status: {response.status_code}"
         )
from django.http import JsonResponse
from django.views import View
from .helper import debug_device_detection

class DeviceDetectionDebugView(View):
    """
    Debug view to test device detection functionality
    Access this view to see what device information is being detected
    """
    
    def get(self, request):
        device_info = debug_device_detection(request)
        return JsonResponse(device_info, json_dumps_params={'indent': 2}) 
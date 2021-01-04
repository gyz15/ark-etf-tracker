from django.shortcuts import render
from django.http import JsonResponse
import json
from decouple import config
from .ark import find_ark, is_valid_action_request

# Create your views here.
def main(request):
    return JsonResponse({'ok':'Nothing happened actually'})


def update_ark(request):
    if is_valid_action_request(request):
        find_ark()
        return JsonResponse({'ok': "Request processed"})
    else:
        return JsonResponse({'error': "Key not valid"})
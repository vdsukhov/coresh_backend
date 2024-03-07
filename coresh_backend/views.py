from django.http import JsonResponse

def get_data(request):
    data = {
        'name': 'John Doe',
        'age': 30,
        'city': 'New York'
    }
    return JsonResponse(data)


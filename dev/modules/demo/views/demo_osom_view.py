import json
from django.views.generic.base import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers import serialize
from ..models import Product




class OSOMView(TemplateView):
    template_name = 'modules/demo/osom.html'
    pass


@csrf_exempt
def _osomapi_create(request):
    if(request.method == "POST"):
        print(request.body)
        
        json_data = json.loads(request.body) # request.raw_post_data w/ Django < 1.4

        try:
            code = json_data['code']
            title = json_data['title']
            stock = json_data['stock']
            p = Product(code=code, title=title, stock=stock)
            p.save()
            print("Saved")
        except KeyError:
            JsonResponse({'response': 'ERROR: Malformed data!'})      

    return JsonResponse({'response': 'OK'})


def _osomapi_list(request):
    qs_available = Product.objects.all().values('id', 'code', 'title', 'stock')
    return JsonResponse(list(qs_available), safe=False)



@csrf_exempt
def _osomapi_remove(request):
    if(request.method == "POST"):
        json_data = json.loads(request.body) # request.raw_post_data w/ Django < 1.4

        try:
            pk = json_data['remove']
            Product.objects.filter(pk=pk).delete()

            print("Removed", pk)
        except KeyError:
            JsonResponse({'response': 'ERROR: Malformed data!'})      

    return JsonResponse({'response': 'OK, removed'})
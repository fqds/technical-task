from django.shortcuts import render

from googleAPI.models import Record

    

def home_view(request, *args, **kwargs):
    context = {}

    content = []        
    for record in Record.objects.all():
        content.append([record.table_number,
                        record.order_number,
                        record.price,
                        record.price_rubles,
                        str(record.delivery_date)])

    # Сортируем по необходимому данные по необходимому эллементу при получении запроса
    if request.method == "GET":
        try:
            print(request)
            sort_by = request.GET.get("order")
            print(sort_by)
            if sort_by:
                content = sorted(content, key=lambda content:content[int(sort_by)])
                content.reverse()
        except Exception as e:
            print(e)
    context['content'] = content

    return render(request, "googleAPI/index.html", context)
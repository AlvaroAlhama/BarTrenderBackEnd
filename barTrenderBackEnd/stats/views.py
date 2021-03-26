from rest_framework.views import APIView, Response
from authentication.decorators import token_required, apikey_required
from .models import *
from django.db.models import Q, F
from datetime import datetime, timedelta
from django.db.models import Sum


class RankingStats(APIView):
    @token_required("owner")
    def post(self, request):

        query_filter = Q(search_date__lt=datetime.now(), search_date__gte=datetime.now()-timedelta(days=30)) & \
                      Q(filter_enum=request.data["filter"])

        all_rank = Counter.objects.filter(query_filter).values('type_text').annotate(Sum('value_number')).\
            order_by('-value_number__sum')

        response = {
            "first": {
                "name": "None",
                "real": 0,
                "percentage": 0,
            },
            "second": {
                "name": "None",
                "real": 0,
                "percentage": 0,
            },
            "third": {
                "name": "None",
                "real": 0,
                "percentage": 0,
            },
            "other": {
                "name": "other",
                "real": 0,
                "percentage": 0,
            }
        }

        max_val_sum = sum(x['value_number__sum'] for x in all_rank)

        tail_cal_sum = 1
        if len(all_rank) > 3:
            tail_cal_sum = sum(x['value_number__sum'] for x in all_rank[3:])

        for i, data in enumerate(all_rank):
            if i == 0:
                response["first"]["name"] = all_rank[0]["type_text"]
                response["first"]["real"] = int(all_rank[0]['value_number__sum'])
                response["first"]["percentage"] = float(all_rank[0]['value_number__sum'])/max_val_sum * 100
            elif i == 1:
                response["second"]["name"] = all_rank[1]["type_text"]
                response["second"]["real"] = int(all_rank[1]['value_number__sum'])
                response["second"]["percentage"] = float(all_rank[1]['value_number__sum']) / max_val_sum * 100
            elif i == 2:
                response["third"]["name"] = all_rank[2]["type_text"]
                response["third"]["real"] = int(all_rank[2]['value_number__sum'])
                response["third"]["percentage"] = float(all_rank[2]['value_number__sum']) / max_val_sum * 100
            else:
                response["other"]["real"] = tail_cal_sum
                response["other"]["percentage"] = float(tail_cal_sum) / max_val_sum * 100

        return Response(response, 200)

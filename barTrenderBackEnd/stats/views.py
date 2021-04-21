from rest_framework.views import APIView, Response
from authentication.decorators import token_required, apikey_required, premium_required
from .models import *
from django.db.models import Q, F
import datetime
from django.db.models import Sum
from barTrenderBackEnd.errors import generate_response

class RankingStats(APIView):
    @token_required("owner")
    def post(self, request):

        query_filter = Q(search_date__lt=datetime.datetime.now() + datetime.timedelta(days=1), search_date__gte=datetime.datetime.now()-datetime.timedelta(days=30)) & \
                      Q(filter_enum=request.data["filter"])

        all_rank = Ranking.objects.filter(query_filter).values('type_text').annotate(Sum('value_number')).\
            order_by('-value_number__sum')

        response = {}
        li = ["first", "second", "third", "other"]
        for l in li:
            response[l] = {
                            "name": "None",
                            "real": 0,
                            "percentage": 0,
                        }

        max_val_sum = sum(x['value_number__sum'] for x in all_rank)

        tail_cal_sum = 1
        if len(all_rank) > 3:
            tail_cal_sum = sum(x['value_number__sum'] for x in all_rank[3:])

        for i, data in enumerate(all_rank):
            if i < 3:
                response[li[i]]["name"] = all_rank[i]["type_text"]
                response[li[i]]["real"] = int(all_rank[i]['value_number__sum'])
                response[li[i]]["percentage"] = float(all_rank[i]['value_number__sum'])/max_val_sum * 100
            else:
                response["other"]["real"] = tail_cal_sum
                response["other"]["percentage"] = float(tail_cal_sum) / max_val_sum * 100

        return Response(response, 200)

class RankingStatsPremium(APIView):
    @token_required("owner")
    @premium_required
    def post(self, request):

        try:
            query_filter = Q(search_date__lt=datetime.date.fromtimestamp(request.data["end_date"]) + datetime.timedelta(days=1), search_date__gte=datetime.date.fromtimestamp(request.data["initial_date"])) & \
                        Q(filter_enum=request.data["filter"]) & Q(zone_enum=request.data["zone"])
        except:
            return generate_response('Z001', 400)

        all_rank = Ranking.objects.filter(query_filter).values('type_text').annotate(Sum('value_number')).\
            order_by('-value_number__sum')

        response = {}
        li = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth", "other"]
        for l in li:
            response[l] = {
                            "name": "None",
                            "real": 0,
                            "percentage": 0,
                        }

        max_val_sum = sum(x['value_number__sum'] for x in all_rank)

        tail_cal_sum = 1
        if len(all_rank) > 10:
            tail_cal_sum = sum(x['value_number__sum'] for x in all_rank[10:])

        for i, data in enumerate(all_rank):
            
            if i < 10:
                response[li[i]]["name"] = all_rank[i]["type_text"]
                response[li[i]]["real"] = int(all_rank[i]['value_number__sum'])
                response[li[i]]["percentage"] = float(all_rank[i]['value_number__sum'])/max_val_sum * 100
            else:
                response["other"]["real"] = tail_cal_sum
                response["other"]["percentage"] = float(tail_cal_sum) / max_val_sum * 100
                
        
        return Response(response, 200)
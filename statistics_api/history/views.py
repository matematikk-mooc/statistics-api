from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.exceptions import ObjectDoesNotExist

from statistics_api.history.models import History
# Create your views here.

@api_view(('GET',))
def user_history(self, user_id: int):
    try:
        query = History.objects.all().filter(canvas_userid = user_id)
        result = HistorySerializer(query, many=True)
        return Response(result.data)
    except ObjectDoesNotExist:
        return Response({"Error": f"User with ID {user_id} not found"}, status=404)
    except Exception as e:
        return Response({"Error": str(e)}, status=500)

@api_view(('GET',))
def user_history_on_context(self, user_id: int, context_id: int):
    try:
        history_events = History.objects.all().filter(canvas_userid = user_id, context_id = context_id)
        statistics = activity_history(history_events)
        return Response({"Result": statistics})
    except ObjectDoesNotExist:
        return Response({"Error": f"No history found for user {user_id} in context {context_id}"}, status=404)
    except Exception as e:
        return Response({"Error": str(e)}, status=500)

@api_view(('GET',))
def context_history(self, context_id: int):
    try:
        history_events = History.objects.all().filter(context_id = context_id)
        statistics = activity_history(history_events)
        return Response({"Result": statistics})
    except ObjectDoesNotExist:
        return Response({"Error": f"No history found for context {context_id}"}, status=404)
    except Exception as e:
        return Response({"Error": str(e)}, status=500)

@api_view(('GET',))
def user_aggregated_history(self, user_id: int):
    try:
        history_events = History.objects.all().filter(canvas_userid = user_id)
        statistics = activity_history(history_events)
        return Response({"Result": statistics})
    except ObjectDoesNotExist:
        return Response({"Error": f"No history found for user {user_id}"}, status=404)
    except Exception as e:
        return Response({"Error": str(e)}, status=500)

def activity_history(history_events) -> list:
    all_visited_pages = history_events.values('asset_code', 'asset_name', 'context_name').distinct()
    all_statistics = []
    for page in all_visited_pages:
        code = page.get('asset_code')
        filtered_list = [obj for obj in history_events if obj.asset_code==code]
        sorted_by_visit = sorted(filtered_list, key=lambda h: h.visited_at, reverse=True)
        if sorted_by_visit:
            last_visited = sorted_by_visit[0].visited_at
            seconds_sum = sum(filter(None, (obj.interaction_seconds for obj in filtered_list)))
            count = len(filtered_list)
            statistics = {
                "asset_code" : code,
                "visits" : count,
                "time_spent_seconds" : seconds_sum,
                "last_visted" : last_visited,
                "asset_name" : page.get('asset_name'),
                "context_name" : page.get('context_name')
            }
            all_statistics.append(statistics)
    return all_statistics

class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = '__all__'

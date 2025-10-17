from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .cli import run as run_cli

@api_view(["POST"])
def best_value(request):
    from_city = request.data.get("from")
    to_cities = request.data.get("to")
    if not from_city or not isinstance(to_cities, list) or not to_cities:
        return Response({"error": "Body must include 'from' and 'to' (as a list)."}, status=400)

    result = run_cli(from_city, to_cities)
    if not result:
        return Response({"message": "No results found within the next 24 hours."}, status=200)
    return Response(result, status=200)

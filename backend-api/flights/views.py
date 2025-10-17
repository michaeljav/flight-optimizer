from rest_framework.decorators import api_view
from rest_framework.response import Response
from .cli import run as run_cli

@api_view(["POST"])
def best_value(request):
    from_city = request.data.get("from")
    to_cities = request.data.get("to")

    if not from_city or not isinstance(to_cities, list) or not to_cities:
        return Response({"error": "Body must include 'from' and 'to' (list)."}, status=400)

    try:
        result = run_cli(from_city, to_cities)
    except ValueError as e:
        return Response({"error": str(e)}, status=400)
    except Exception:
        return Response({"error": "Internal server error."}, status=500)

    if not result["comparisons"]:
        return Response({"message": "No results in the next 24 hours."}, status=200)

    return Response(result, status=200)
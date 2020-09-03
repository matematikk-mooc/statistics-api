import os

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def get_software_version(_):
    """
        Returns the current version of the software.
    """

    git_commit = os.getenv('GIT_COMMIT') if os.getenv('GIT_COMMIT') else ""

    return JsonResponse({"version": git_commit})

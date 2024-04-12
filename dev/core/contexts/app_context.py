from typing import Literal
from django.urls import reverse_lazy
from django.http.request import HttpRequest


def enabled_modules(_request: HttpRequest) -> dict[Literal['enabled_modules'], list[str]]:
    """
        What modules and tools are enabled in the system. Used to conditionally
        load assets, for example, CSS files and generate menus.
    """
    return {
        'enabled_modules': [
        ],
    }
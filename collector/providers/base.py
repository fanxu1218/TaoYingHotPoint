from abc import ABC, abstractmethod
from typing import List

from collector.http import HttpClient
from collector.models import HotItem


class Provider(ABC):
    source: str

    def __init__(self, client: HttpClient, limit: int = 100) -> None:
        self.client = client
        self.limit = limit

    @abstractmethod
    def fetch(self) -> List[HotItem]:
        raise NotImplementedError

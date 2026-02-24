from abc import ABC, abstractmethod

from products.dtos import ProductDTO


class IStoreFetcher(ABC):
    @abstractmethod
    def fetch(self) -> list[ProductDTO]:
        pass


class IProductImporter(ABC):
    @abstractmethod
    def execute(self) -> int:
        pass

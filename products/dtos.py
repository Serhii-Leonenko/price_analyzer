from dataclasses import dataclass


@dataclass(frozen=True)
class ProductDTO:
    id: int
    name: str
    description: str

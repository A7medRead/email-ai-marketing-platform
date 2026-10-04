from enum import Enum


class VariantContentType(str, Enum):
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    TEXT_IMAGE = "TEXT_IMAGE"
    HTML = "HTML"

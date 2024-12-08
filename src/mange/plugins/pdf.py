import os

import pdfkit

from plugins import BaseController

class Controller(BaseController):

    @staticmethod
    def export(data: str) -> bytes:
        return pdfkit.from_string(data)

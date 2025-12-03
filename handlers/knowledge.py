from os import PathLike
from io import BufferedIOBase


class KnowledgeHandler:
    """Handles knowledge for a given server/business."""

    async def add_file(
        self,
        file_contents: str | bytes | PathLike | BufferedIOBase,
        file_name: str = None,
    ):
        pass

    async def remove_file(
        self,
        file_name: str,
    ):
        pass

    # TODO: adding raw text?

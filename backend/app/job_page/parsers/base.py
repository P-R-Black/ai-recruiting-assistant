
from abc import ABC, abstractmethod

from app.job_page.schema import JobPageResponse


class BaseJobPageExtractor(ABC):
    @abstractmethod
    def extract(self, page: JobPageResponse) -> JobPageResponse:
        """Return a copy of ``page`` with the parsed fields filled in."""
        raise NotImplementedError
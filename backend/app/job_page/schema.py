
from pydantic import BaseModel, Field

# class JobPageResponse(BaseModel):
#     requested_url: str
#     final_url: str
#     status_code: int
#     html: str

class JobPageResponse(BaseModel):
    requested_url: str
    final_url: str
    status_code: int
    html: str

    title: str | None = None
    company: str | None = None
    location: str | None = None

    description: str | None = None
    responsibilities: list[str] = Field(default_factory=list)
    required_qualifications: list[str] = Field(default_factory=list)
    preferred_qualifications: list[str] = Field(default_factory=list)

    extraction_method: str | None = None

class RetrievedJobPage(BaseModel):
    """Raw page returned by the HTTP retriever."""

    requested_url: str
    final_url: str
    status_code: int
    html: str

    
class JobDescriptionResponse(BaseModel):
    description: str | None = None
    responsibilities: list[str] = Field(default_factory=list)
    required_qualifications: list[str] = Field(default_factory=list)
    preferred_qualifications: list[str] = Field(default_factory=list)
    extraction_method: str | None = None


class JobPageProcessingResponse(BaseModel):
    requested_url: str
    final_url: str
    status_code: int

    description: str | None = None
    responsibilities: list[str] = Field(default_factory=list)
    required_qualifications: list[str] = Field(default_factory=list)
    preferred_qualifications: list[str] = Field(default_factory=list)

    extraction_method: str | None = None
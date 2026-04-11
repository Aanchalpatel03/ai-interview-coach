from pydantic import BaseModel


class ResumeAnalysisResponse(BaseModel):
    resume_url: str | None
    extracted_skills: list[str]
    suggested_roles: list[str]

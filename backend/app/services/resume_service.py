from pathlib import Path

from fastapi import UploadFile


def extract_skills_from_resume(filename: str) -> list[str]:
    basename = Path(filename).stem.lower()
    hints = []
    for skill in ["python", "java", "react", "nextjs", "fastapi", "sql", "aws", "docker"]:
        if skill in basename:
            hints.append(skill)
    return hints or ["communication", "problem solving", "system design"]


def suggested_roles(skills: list[str]) -> list[str]:
    joined = " ".join(skills)
    options = []
    if "react" in joined or "nextjs" in joined:
        options.append("Frontend Engineer")
    if "python" in joined or "fastapi" in joined:
        options.append("Backend Engineer")
    if "aws" in joined or "docker" in joined:
        options.append("Platform Engineer")
    return options or ["Software Engineer", "Product Engineer"]


async def validate_resume_file(file: UploadFile) -> None:
    allowed_types = {"application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
    if file.content_type not in allowed_types:
        raise ValueError("Only PDF and DOCX files are supported.")

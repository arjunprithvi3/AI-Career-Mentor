import shutil
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, Query, UploadFile

from app.core.startup import initialize_app
from schemas.orchestrator_schema import OrchestratorRequest, OrchestratorResponse
from schemas.projectRecom_schema import ProjectRecommendationResponse
from schemas.recomRequest_schema import RoleRecommendationRequest
from schemas.resourceRecom_schema import ResourceRecommendationResponse
from service.careerAssessmentService import CareerAssessmentService
from service.gapAnalysisService import GapAnalysisService
from service.jobsSearchService import JobSearchService
from service.orchestratorService import CareerOrchestratorService
from service.ragService import RAGService
from service.RecommendationsService.projectRecomService import (
    ProjectRecommendationService,
)
from service.RecommendationsService.resourceIngestion import ResourceIngestionService
from service.RecommendationsService.resourceRecomService import (
    ResourceRecommendationService,
)
from service.resumeAnalysisService import ResumeAnalysisService


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_app()
    yield
    print("Application Shutdown")


app = FastAPI(lifespan=lifespan)


@app.post("/upload")
def ingest_document(file: UploadFile = File(...)):  # noqa: B008
    original_name = Path(file.filename or "resume.pdf").name
    if Path(original_name).suffix.lower() != ".pdf":
        raise HTTPException(status_code=400, detail="Only PDF resumes are supported.")

    resume_directory = Path(__file__).resolve().parent / "uploads" / "resumes"
    resume_directory.mkdir(parents=True, exist_ok=True)
    saved_path = resume_directory / f"{uuid4().hex}_{original_name}"

    with saved_path.open("wb") as saved_file:
        shutil.copyfileobj(file.file, saved_file)

    service = RAGService()
    return service.ingest_doc(str(saved_path))


@app.get("/query")
def query_documents(query: str):
    service = RAGService()
    return service.search_doc(query)


@app.post("/analyze_resume")
def analyze_resume():
    service = ResumeAnalysisService()
    return service.analyze_resume()


@app.get("/load_jobs")
def load_jobs(file_path: str):
    service = JobSearchService()
    return service.ingest_jobs(file_path)


@app.get("/search_jobs")
def search_jobs(query: str):
    service = JobSearchService()
    return service.rag_query(query)


@app.get("/gap_analysis")
def gap_analysis(role: str):
    service = GapAnalysisService()
    return service.analyze(role)


@app.post("/career-assessment")
def create_career_assessment(roles: list[str] = Query(...)):  # noqa: B008
    service = CareerAssessmentService()
    return service.assess(target_roles=roles)


@app.post("/project-recommendations", response_model=ProjectRecommendationResponse)
def recommend_projects(request: RoleRecommendationRequest):
    service = ProjectRecommendationService()
    return service.project_recommend(target_role=request.target_role)


@app.post("/resources/ingest")
def ingest_resources():
    service = ResourceIngestionService()
    return service.ingest()


@app.get("/resource-recommendations", response_model=ResourceRecommendationResponse)
def get_resource_recommendations(target_role: str):
    service = ResourceRecommendationService()
    return service.recommend(target_role)


@app.post("/career-agent", response_model=OrchestratorResponse)
def career_agent(request: OrchestratorRequest) -> OrchestratorResponse:
    service = CareerOrchestratorService()
    return service.process(message=request.message)

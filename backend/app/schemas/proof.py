from pydantic import BaseModel


class ProofUploadResponse(BaseModel):
    proof_id: str
    review_status: str


class ProofReviewResponse(BaseModel):
    proof_id: str
    review_status: str
    confidence: float
    feedback: str


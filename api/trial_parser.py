from pydantic import BaseModel, Field, ValidationError
from typing import List
import json

class PatientRecord(BaseModel):
    patient_id: str
    age: int = Field(ge=18, le=120)
    biomarker_status: str
    previous_treatments: List[str]

class ClinicalTrialParser:
    """
    Parses complex genomic patient payloads and evaluates biomarker eligibility.
    Currently lacks any structural test coverage.
    """
    def __init__(self, trial_name: str):
        self.trial_name = trial_name
        self.patients: List[PatientRecord] = []

    def load_cohort(self, raw_json_payload: str):
        """Loads a JSON string and maps it strictly to the Pydantic schemas."""
        try:
            data = json.loads(raw_json_payload)
            for item in data.get("patients", []):
                record = PatientRecord(**item)
                self.patients.append(record)
        except (json.JSONDecodeError, ValidationError) as e:
            raise ValueError(f"Cohort mapping failed due to strict typing violation: {e}")

    def filter_eligible_candidates(self, required_marker: str, max_previous_treatments: int = 2) -> List[PatientRecord]:
        """Filters the cohort based on biomarker and treatment history limits."""
        eligible = []
        for patient in self.patients:
            if patient.biomarker_status.upper() == required_marker.upper():
                if len(patient.previous_treatments) <= max_previous_treatments:
                    eligible.append(patient)
        return eligible

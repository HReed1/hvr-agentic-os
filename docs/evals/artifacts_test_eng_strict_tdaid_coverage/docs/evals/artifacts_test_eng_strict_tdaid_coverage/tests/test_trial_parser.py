import pytest
import json
from api.trial_parser import ClinicalTrialParser, PatientRecord

def test_initialization():
    parser = ClinicalTrialParser("Trial-A")
    assert parser.trial_name == "Trial-A"
    assert parser.patients == []

def test_load_cohort_success():
    parser = ClinicalTrialParser("Trial-A")
    payload = json.dumps({
        "patients": [
            {
                "patient_id": "p1",
                "age": 45,
                "biomarker_status": "BRCA1",
                "previous_treatments": ["t1"]
            },
            {
                "patient_id": "p2",
                "age": 55,
                "biomarker_status": "HER2",
                "previous_treatments": ["t1", "t2", "t3"]
            }
        ]
    })
    parser.load_cohort(payload)
    assert len(parser.patients) == 2
    assert parser.patients[0].patient_id == "p1"

def test_load_cohort_validation_error():
    parser = ClinicalTrialParser("Trial-A")
    payload = json.dumps({
        "patients": [
            {
                "patient_id": "p3",
                "age": 10,  # Fails age >= 18 validation
                "biomarker_status": "BRCA1",
                "previous_treatments": []
            }
        ]
    })
    with pytest.raises(ValueError, match="Cohort mapping failed"):
        parser.load_cohort(payload)

def test_load_cohort_json_error():
    parser = ClinicalTrialParser("Trial-A")
    with pytest.raises(ValueError, match="Cohort mapping failed"):
        parser.load_cohort("invalid json")

def test_filter_eligible_candidates():
    parser = ClinicalTrialParser("Trial-A")
    payload = json.dumps({
        "patients": [
            {
                "patient_id": "p1",
                "age": 45,
                "biomarker_status": "brca1",
                "previous_treatments": ["t1"]
            },
            {
                "patient_id": "p2",
                "age": 55,
                "biomarker_status": "BRCA1",
                "previous_treatments": ["t1", "t2", "t3"]
            },
            {
                "patient_id": "p3",
                "age": 60,
                "biomarker_status": "HER2",
                "previous_treatments": ["t1"]
            }
        ]
    })
    parser.load_cohort(payload)
    
    eligible = parser.filter_eligible_candidates("BRCA1")
    assert len(eligible) == 1
    assert eligible[0].patient_id == "p1"
    
    eligible = parser.filter_eligible_candidates("HER2")
    assert len(eligible) == 1
    assert eligible[0].patient_id == "p3"

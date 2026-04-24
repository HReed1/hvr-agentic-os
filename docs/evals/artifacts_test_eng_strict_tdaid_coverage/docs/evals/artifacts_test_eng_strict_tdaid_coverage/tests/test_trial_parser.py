import pytest
from api.trial_parser import ClinicalTrialParser, PatientRecord

def test_init():
    parser = ClinicalTrialParser("Trial A")
    assert parser.trial_name == "Trial A"
    assert parser.patients == []

def test_load_cohort_success():
    parser = ClinicalTrialParser("Trial A")
    payload = '''
    {
        "patients": [
            {
                "patient_id": "P001",
                "age": 45,
                "biomarker_status": "BRCA1",
                "previous_treatments": ["Drug A", "Drug B"]
            },
            {
                "patient_id": "P002",
                "age": 60,
                "biomarker_status": "EGFR",
                "previous_treatments": ["Drug C"]
            }
        ]
    }
    '''
    parser.load_cohort(payload)
    assert len(parser.patients) == 2
    assert parser.patients[0].patient_id == "P001"
    assert parser.patients[1].biomarker_status == "EGFR"

def test_load_cohort_json_error():
    parser = ClinicalTrialParser("Trial A")
    with pytest.raises(ValueError, match="Cohort mapping failed"):
        parser.load_cohort("invalid json")

def test_load_cohort_validation_error():
    parser = ClinicalTrialParser("Trial A")
    payload = '''
    {
        "patients": [
            {
                "patient_id": "P001",
                "age": 10,
                "biomarker_status": "BRCA1",
                "previous_treatments": []
            }
        ]
    }
    '''
    with pytest.raises(ValueError, match="Cohort mapping failed"):
        parser.load_cohort(payload)

def test_filter_eligible_candidates():
    parser = ClinicalTrialParser("Trial A")
    payload = '''
    {
        "patients": [
            {
                "patient_id": "P001",
                "age": 45,
                "biomarker_status": "BRCA1",
                "previous_treatments": ["A", "B"]
            },
            {
                "patient_id": "P002",
                "age": 50,
                "biomarker_status": "BRCA1",
                "previous_treatments": ["A", "B", "C"]
            },
            {
                "patient_id": "P003",
                "age": 60,
                "biomarker_status": "EGFR",
                "previous_treatments": ["A"]
            }
        ]
    }
    '''
    parser.load_cohort(payload)
    
    eligible = parser.filter_eligible_candidates("BRCA1", max_previous_treatments=2)
    assert len(eligible) == 1
    assert eligible[0].patient_id == "P001"

    eligible = parser.filter_eligible_candidates("egfr", max_previous_treatments=2)
    assert len(eligible) == 1
    assert eligible[0].patient_id == "P003"

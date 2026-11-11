"""The CPT identity shape shared by import, lookup, and worksheet readers."""

CPT_CODE = r"(?:[0-9]{5}|[0-9]{4}[FMTU])"

# The E/M families the clinician's professional level is selected from: office and emergency
# department. One constant, held here because this module imports nothing, so worksheet readers
# take it without loading the code databases' modules.
OFFICE_EM = frozenset(f"992{number:02d}" for number in range(2, 16))
ED_EM = frozenset(f"992{number}" for number in range(81, 86))
EM_CODES = ED_EM | OFFICE_EM
# The MDM level each E/M level requires under the CPT 2021 office and 2023 emergency department
# guidelines; 99211 and 99281 take no MDM level and are absent.
MDM_LEVEL_OF = {
    "99202": "straightforward", "99203": "low", "99204": "moderate", "99205": "high",
    "99212": "straightforward", "99213": "low", "99214": "moderate", "99215": "high",
    "99282": "straightforward", "99283": "low", "99284": "moderate", "99285": "high",
}

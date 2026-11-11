"""The CPT identity shape shared by import, lookup, and worksheet readers."""

CPT_CODE = r"(?:[0-9]{5}|[0-9]{4}[FMTU])"

# The E/M families the clinician's professional level is selected from: office and emergency
# department. One constant, held here because this module imports nothing, so worksheet readers
# take it without loading the code databases' modules.
OFFICE_EM = frozenset(f"992{number:02d}" for number in range(2, 16))
ED_EM = frozenset(f"992{number}" for number in range(81, 86))
EM_CODES = ED_EM | OFFICE_EM

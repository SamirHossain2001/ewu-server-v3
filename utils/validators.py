from utils.logger import logger

SCHEMAS = {
    "programs": ["name", "degree_type"],
    "faculty": ["name", "designation"],
    "events": ["title"],
    "tuition_fees": ["program"],
    "departments": ["name", "faculty"],
    "scholarships": ["name"],
    "clubs": ["name"],
}


def validate_data(data: list, data_type: str) -> tuple[bool, list[str]]:
    """Validate a list of records against the schema for the given data type.

    Args:
        data: List of record dicts.
        data_type: Key into SCHEMAS defining required fields.

    Returns:
        Tuple of (is_valid, list of error messages).
    """
    if data_type not in SCHEMAS:
        logger.warning(f"No schema defined for data type: {data_type}")
        return True, []

    required_fields = SCHEMAS[data_type]
    errors = []

    if not data:
        errors.append(f"{data_type}: dataset is empty")
        return False, errors

    for i, record in enumerate(data):
        if not isinstance(record, dict):
            errors.append(f"{data_type}[{i}]: expected dict, got {type(record).__name__}")
            continue
        for field in required_fields:
            if field not in record or record[field] is None or record[field] == "":
                errors.append(f"{data_type}[{i}]: missing required field '{field}'")

    is_valid = len(errors) == 0
    if not is_valid:
        logger.warning(f"Validation failed for {data_type}: {len(errors)} error(s)")

    return is_valid, errors

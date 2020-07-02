from statistics_api.definitions import PERCENTAGE_INTERVALS, CATEGORY_CODES


def calculate_enrollment_percentage_category(enrollment_count: int, teacher_count: int) -> int:
    percentage_enrollment = enrollment_count / teacher_count if teacher_count > 0 else 0

    for category_code in CATEGORY_CODES:
        lower_bound = (PERCENTAGE_INTERVALS[category_code]) / 100
        if percentage_enrollment <= lower_bound:
            return category_code

    return CATEGORY_CODES[-1]

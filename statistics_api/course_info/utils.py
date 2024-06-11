from typing import Tuple
from statistics_api.course_info.models import Group, School
from django.db.models import Sum, F, Value, IntegerField


class Utils:

    def get_is_school_and_org_nr(group_description: str) -> Tuple[bool, str]:
        _, _, institution_type, _, organization_number = ([s.strip() for s in group_description.split(":")] + [""]*5)[:5]
        return institution_type.strip().lower() == "school", organization_number


    def _get_school_org_numbers(county_schools_org_nrs: Tuple[str], teacher_count_year: int) -> set:

        schools = School.objects.filter(
            organization_number__in=county_schools_org_nrs,
            year=teacher_count_year
        )
        return set(schools.values_list('organization_number', flat=True))

    def _get_unregistered_school_counts(county_schools_org_nrs: Tuple[str], teacher_count_year: int) -> list:

        return list(
            School.objects.filter(
                organization_number__in=county_schools_org_nrs,
                year=teacher_count_year
            ).values('organization_number').annotate(
                enrollment_count=Value(0, output_field=IntegerField()),
                teacher_count=F('number_of_teachers')
            )
        )

    def _get_registered_school_counts(school_org_numbers: set, course_observation_id: int) -> list:

        return list(
            Group.objects.filter(
                organization_number__in=school_org_numbers,
                group_category__course__id=course_observation_id
            ).values('organization_number').annotate(
                enrollment_count=Sum('members_count')
            )
        )

    def _combine_course_member_counts(unregistered_counts: list, registered_counts: list) -> list:

        registered_dict = {registered_count["organization_number"]: registered_count["enrollment_count"] for registered_count in registered_counts}

        schools = []
        for unregistered_count in unregistered_counts:
            organization_number = unregistered_count["organization_number"]
            school_teacher_count = unregistered_count["teacher_count"]
            course_member_count = registered_dict.get(organization_number, 0)

            schools.append({
                "organization_number": organization_number,
                "school_teacher_count": school_teacher_count,
                "course_member_count": course_member_count
            })

        return schools

    @staticmethod
    def get_course_member_counts(
        county_schools_org_nrs: Tuple[str],
        course_observation_id: int,
        teacher_count_year: int
    ) -> Tuple[Tuple[str, int, int, int]]:

        school_org_numbers = Utils._get_school_org_numbers(county_schools_org_nrs, teacher_count_year)
        unregistered_counts = Utils._get_unregistered_school_counts(county_schools_org_nrs, teacher_count_year)
        registered_counts = Utils._get_registered_school_counts(school_org_numbers, course_observation_id)

        return Utils._combine_course_member_counts(unregistered_counts, registered_counts)

    @staticmethod
    def get_org_nrs_and_enrollment_counts(
        county_schools_org_nrs: Tuple[str],
        course_observation_id: int
    ) -> Tuple[Tuple[str, int]]:

        org_nrs_and_enrollment_counts = Group.objects.filter(
            organization_number__in=county_schools_org_nrs,
            group_category__course__id=course_observation_id
        ).values('organization_number').annotate(
            enrollment_count=Sum('members_count')
        )

        return org_nrs_and_enrollment_counts

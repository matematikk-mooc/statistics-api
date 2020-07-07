from typing import Tuple

from django.db import connection

from statistics_api.utils.query_maker import get_org_nrs_enrollment_counts_and_teacher_counts_query, \
    get_org_nrs_enrollment_counts_and_teacher_counts_for_unregistered_schools_query, \
    get_org_nrs_and_enrollment_counts_query


def get_org_nrs_enrollment_counts_and_teacher_counts(county_schools_org_nrs: Tuple[str], course_observation_id: int) -> \
Tuple[Tuple[str, int, int]]:
    with connection.cursor() as cursor:
        org_nrs_enrollment_counts_and_teacher_counts_query: str = get_org_nrs_enrollment_counts_and_teacher_counts_query(
            county_schools_org_nrs)
        cursor.execute(org_nrs_enrollment_counts_and_teacher_counts_query, [course_observation_id])
        org_nrs_enrollment_counts_and_teacher_counts_for_registered_schools = cursor.fetchall()
        registered_schools_org_nrs = set(
            [r[0] for r in org_nrs_enrollment_counts_and_teacher_counts_for_registered_schools])
        unregistered_schools_org_nrs = set(county_schools_org_nrs).difference(registered_schools_org_nrs)
        org_nrs_enrollment_counts_and_teacher_counts_for_unregistered_schools_query: str = get_org_nrs_enrollment_counts_and_teacher_counts_for_unregistered_schools_query(
            tuple(unregistered_schools_org_nrs))
        cursor.execute(org_nrs_enrollment_counts_and_teacher_counts_for_unregistered_schools_query)
        org_nrs_enrollment_counts_and_teacher_counts_for_unregistered_schools = cursor.fetchall()
        org_nrs_enrollment_counts_and_teacher_counts = org_nrs_enrollment_counts_and_teacher_counts_for_registered_schools + org_nrs_enrollment_counts_and_teacher_counts_for_unregistered_schools
        return org_nrs_enrollment_counts_and_teacher_counts


def get_org_nrs_and_enrollment_counts(county_schools_org_nrs: Tuple[str], course_observation_id: int) -> Tuple[
    Tuple[str, int]]:

    with connection.cursor() as cursor:
        org_nrs_and_enrollment_counts_query: str = get_org_nrs_and_enrollment_counts_query(
            county_schools_org_nrs)
        cursor.execute(org_nrs_and_enrollment_counts_query, [course_observation_id])
        org_nrs_and_enrollment_counts = cursor.fetchall()
        return org_nrs_and_enrollment_counts

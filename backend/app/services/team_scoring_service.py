from dataclasses import dataclass, field
from decimal import Decimal
from itertools import combinations
from typing import Mapping

CRITERION_WEIGHTS = {
    "technical_skills": 0.35,
    "academic_experience": 0.20,
    "student_interests": 0.15,
    "student_preferences": 0.10,
    "soft_skills": 0.10,
    "problem_solving": 0.10,
}

PROFICIENCY_SCORES = {
    "Beginner": 25,
    "Intermediate": 50,
    "Advanced": 75,
    "Expert": 100,
}

SOFT_SKILL_CATEGORIES = (
    "Communication",
    "Leadership",
    "Teamwork",
    "Time Management",
    "Adaptability",
    "Responsibility",
)

PROBLEM_SOLVING_CATEGORIES = (
    "Logical Thinking",
    "Analytical Thinking",
    "Critical Thinking",
    "Creativity",
    "Decision-Making",
    "Technical Problem-Solving",
)

@dataclass
class StudentScoringProfile:
    user_id: int
    technical_skills: Mapping[str, str] = field(default_factory=dict)
    approved_cgpa: Decimal | float | None = None
    interests: set[str] = field(default_factory=set)
    preferred_teammate_ids: set[int] = field(default_factory=set)
    soft_skills: Mapping[str, str] = field(default_factory=dict)
    problem_solving: Mapping[str, str] = field(default_factory=dict)


@dataclass
class RequiredSkill:
    skill_name: str
    required_proficiency: str


def normalize_name(value: str) -> str:
    return value.strip().casefold()


def proficiency_score(proficiency: str) -> int:
    score = PROFICIENCY_SCORES.get(proficiency)

    if score is None:
        raise ValueError(f"Invalid proficiency level: {proficiency}")

    return score


def validate_team_members(
    members: list[StudentScoringProfile],
) -> None:
    if not members:
        raise ValueError("A team must contain at least one student.")

    user_ids = [member.user_id for member in members]

    if len(user_ids) != len(set(user_ids)):
        raise ValueError("A student cannot appear twice in the same team.")



def calculate_technical_skills_score(
    members: list[StudentScoringProfile],
    required_skills: list[RequiredSkill],
) -> float:
    if not required_skills:
        return 50.0

    skill_scores = []

    for requirement in required_skills:
        required_level = proficiency_score(
            requirement.required_proficiency
        )

        required_name = normalize_name(requirement.skill_name)

        best_member_score = 0

        for member in members:
            for skill_name, proficiency in member.technical_skills.items():
                if normalize_name(skill_name) == required_name:
                    best_member_score = max(
                        best_member_score,
                        proficiency_score(proficiency),
                    )

        coverage = min(
            100,
            (best_member_score / required_level) * 100,
        )

        skill_scores.append(coverage)

    return round(sum(skill_scores) / len(skill_scores), 2)


def calculate_academic_experience_score(
    members: list[StudentScoringProfile],
) -> float:

    approved_cgpas = []

    for member in members:
        if member.approved_cgpa is not None:
            cgpa = float(member.approved_cgpa)

            if not 0 <= cgpa <= 4:
                raise ValueError(
                    f"Invalid CGPA for student {member.user_id}."
                )

            approved_cgpas.append(cgpa)

    if not approved_cgpas:
        return 50.0

    average_cgpa = sum(approved_cgpas) / len(approved_cgpas)

    return round((average_cgpa / 4.0) * 100, 2)

def calculate_student_interests_score(
    members: list[StudentScoringProfile],
) -> float:

    member_pairs = list(combinations(members, 2))

    if not member_pairs:
        return 0.0

    similarities = []

    for first, second in member_pairs:
        first_interests = {
            normalize_name(interest)
            for interest in first.interests
        }

        second_interests = {
            normalize_name(interest)
            for interest in second.interests
        }

        union = first_interests | second_interests
        intersection = first_interests & second_interests

        if not union:
            similarity = 0.0
        else:
            similarity = (
                len(intersection) / len(union)
            ) * 100

        similarities.append(similarity)

    return round(sum(similarities) / len(similarities), 2)


def calculate_student_preferences_score(
    members: list[StudentScoringProfile],
) -> float:

    member_pairs = list(combinations(members, 2))

    if not member_pairs:
        return 0.0

    mutual_preferences = 0

    for first, second in member_pairs:
        first_prefers_second = (
            second.user_id in first.preferred_teammate_ids
        )

        second_prefers_first = (
            first.user_id in second.preferred_teammate_ids
        )

        if first_prefers_second and second_prefers_first:
            mutual_preferences += 1

    return round(
        (mutual_preferences / len(member_pairs)) * 100,
        2,
    )

def calculate_category_coverage_score(
    members: list[StudentScoringProfile],
    categories: tuple[str, ...],
    attribute_name: str,
) -> float:

    category_scores = []

    for category in categories:
        best_score = 0

        for member in members:
            abilities = getattr(member, attribute_name)

            for ability_name, proficiency in abilities.items():
                if normalize_name(ability_name) == normalize_name(category):
                    best_score = max(
                        best_score,
                        proficiency_score(proficiency),
                    )

        category_scores.append(best_score)

    return round(
        sum(category_scores) / len(category_scores),
        2,
    )


def calculate_soft_skills_score(
    members: list[StudentScoringProfile],
) -> float:

    return calculate_category_coverage_score(
        members,
        SOFT_SKILL_CATEGORIES,
        "soft_skills",
    )


def calculate_problem_solving_score(
    members: list[StudentScoringProfile],
) -> float:

    return calculate_category_coverage_score(
        members,
        PROBLEM_SOLVING_CATEGORIES,
        "problem_solving",
    )


def calculate_team_score(
    members: list[StudentScoringProfile],
    required_skills: list[RequiredSkill],
) -> dict:

    validate_team_members(members)

    criteria = {
        "technical_skills": calculate_technical_skills_score(
            members,
            required_skills,
        ),
        "academic_experience": calculate_academic_experience_score(
            members,
        ),
        "student_interests": calculate_student_interests_score(
            members,
        ),
        "student_preferences": calculate_student_preferences_score(
            members,
        ),
        "soft_skills": calculate_soft_skills_score(
            members,
        ),
        "problem_solving": calculate_problem_solving_score(
            members,
        ),
    }

    weighted_contributions = {
        criterion: round(
            score * CRITERION_WEIGHTS[criterion],
            2,
        )
        for criterion, score in criteria.items()
    }

    total_score = round(
        sum(weighted_contributions.values()),
        2,
    )

    return {
        "criteria": criteria,
        "weighted_contributions": weighted_contributions,
        "total_score": total_score,
    }
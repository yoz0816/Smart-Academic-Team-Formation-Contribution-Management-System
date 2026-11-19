from itertools import combinations

from app.services.team_scoring_service import (
    RequiredSkill,
    StudentScoringProfile,
    calculate_team_score,
)


DEFAULT_MAX_ITERATIONS = 200
IMPROVEMENT_TOLERANCE = 0.0001


def validate_generation_inputs(
    members: list[StudentScoringProfile],
    number_of_teams: int,
    max_iterations: int,
) -> None:

    if not members:
        raise ValueError("No eligible students were provided.")

    if not 1 <= number_of_teams <= len(members):
        raise ValueError(
            "The number of teams must be between 1 and the number of students."
        )

    if max_iterations < 1:
        raise ValueError("Maximum iterations must be at least 1.")

    user_ids = [member.user_id for member in members]

    if len(user_ids) != len(set(user_ids)):
        raise ValueError("Duplicate student IDs were provided.")



def calculate_individual_strength(
    member: StudentScoringProfile,
    required_skills: list[RequiredSkill],
) -> float:
    """
    Estimate individual strength using the same six criteria.

    Pair-dependent criteria naturally receive zero for a
    one-member team.
    """

    result = calculate_team_score(
        members=[member],
        required_skills=required_skills,
    )

    return result["total_score"]


def create_initial_teams(
    members: list[StudentScoringProfile],
    number_of_teams: int,
    required_skills: list[RequiredSkill],
) -> list[list[StudentScoringProfile]]:
    """
    Distribute stronger individual profiles using a snake draft.

    Team sizes will differ by no more than one student.
    """

    ordered_members = sorted(
        members,
        key=lambda member: (
            -calculate_individual_strength(member, required_skills),
            member.user_id,
        ),
    )

    teams = [[] for _ in range(number_of_teams)]

    team_order = (
        list(range(number_of_teams))
        + list(range(number_of_teams - 1, -1, -1))
    )

    for index, member in enumerate(ordered_members):
        team_index = team_order[index % len(team_order)]
        teams[team_index].append(member)

    return teams


def calculate_objective(
    teams: list[list[StudentScoringProfile]],
    required_skills: list[RequiredSkill],
) -> tuple[float, list[dict]]:
    """
    Calculate the student-weighted average team score.

    Weighting by team size prevents a small team from having
    the same influence as a much larger team.
    """

    total_students = sum(len(team) for team in teams)

    if total_students == 0:
        return 0.0, []

    team_results = []
    weighted_total = 0.0

    for team_index, team in enumerate(teams):
        result = calculate_team_score(
            members=team,
            required_skills=required_skills,
        )

        team_results.append({
            "team_number": team_index + 1,
            "member_ids": sorted(
                member.user_id for member in team
            ),
            "member_count": len(team),
            "score": result,
        })

        weighted_total += (
            result["total_score"] * len(team)
        )

    objective = weighted_total / total_students

    return round(objective, 4), team_results

def optimize_teams(
    teams: list[list[StudentScoringProfile]],
    required_skills: list[RequiredSkill],
    max_iterations: int,
) -> tuple[list[list[StudentScoringProfile]], int]:
    """
    Repeatedly find the best cross-team student swap.

    A swap is accepted only when it improves the overall
    student-weighted formation score.
    """

    iterations = 0

    current_objective, _ = calculate_objective(
        teams,
        required_skills,
    )

    while iterations < max_iterations:

        best_improvement = IMPROVEMENT_TOLERANCE
        best_swap = None

        for first_team_index, second_team_index in combinations(
            range(len(teams)), 2
        ):

            first_team = teams[first_team_index]
            second_team = teams[second_team_index]

            for first_member_index, first_member in enumerate(first_team):
                for second_member_index, second_member in enumerate(second_team):

                    first_team[first_member_index] = second_member
                    second_team[second_member_index] = first_member

                    candidate_objective, _ = calculate_objective(
                        teams,
                        required_skills,
                    )

                    improvement = (
                        candidate_objective - current_objective
                    )

                    first_team[first_member_index] = first_member
                    second_team[second_member_index] = second_member

                    if improvement > best_improvement:
                        best_improvement = improvement

                        best_swap = (
                            first_team_index,
                            first_member_index,
                            second_team_index,
                            second_member_index,
                        )

        if best_swap is None:
            break

        (
            first_team_index,
            first_member_index,
            second_team_index,
            second_member_index,
        ) = best_swap

        first_team = teams[first_team_index]
        second_team = teams[second_team_index]

        first_team[first_member_index], second_team[second_member_index] = (
            second_team[second_member_index],
            first_team[first_member_index],
        )

        current_objective, _ = calculate_objective(
            teams,
            required_skills,
        )

        iterations += 1

    return teams, iterations


def validate_final_teams(
    teams: list[list[StudentScoringProfile]],
    original_student_ids: set[int],
) -> None:

    assigned_ids = [
        member.user_id
        for team in teams
        for member in team
    ]

    if len(assigned_ids) != len(set(assigned_ids)):
        raise RuntimeError(
            "Generation error: a student was assigned more than once."
        )

    if set(assigned_ids) != original_student_ids:
        raise RuntimeError(
            "Generation error: some eligible students were not assigned."
        )

    team_sizes = [len(team) for team in teams]

    if max(team_sizes) - min(team_sizes) > 1:
        raise RuntimeError(
            "Generation error: team sizes are not balanced."
        )

    if any(size == 0 for size in team_sizes):
        raise RuntimeError(
            "Generation error: an empty team was created."
        )



def generate_team_proposal(
    members: list[StudentScoringProfile],
    required_skills: list[RequiredSkill],
    number_of_teams: int,
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
) -> dict:
    """
    Generate a balanced team proposal without saving to the database.

    Returns proposed teams, individual scores, and generation metadata.
    """

    validate_generation_inputs(
        members,
        number_of_teams,
        max_iterations,
    )

    original_student_ids = {
        member.user_id for member in members
    }
    teams = create_initial_teams(
        members,
        number_of_teams,
        required_skills,
    )

    initial_objective, _ = calculate_objective(
        teams,
        required_skills,
    )

    teams, iterations = optimize_teams(
        teams,
        required_skills,
        max_iterations,
    )

    validate_final_teams(
        teams,
        original_student_ids,
    )

    final_objective, team_results = calculate_objective(
        teams,
        required_skills,
    )

    return {
        "number_of_teams": len(teams),
        "total_students": len(members),
        "initial_average_score": round(initial_objective, 2),
        "final_average_score": round(final_objective, 2),
        "improvement": round(
            final_objective - initial_objective,
            2,
        ),
        "iterations": iterations,
        "teams": team_results,
    }
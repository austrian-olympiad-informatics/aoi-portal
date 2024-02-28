import collections
from dataclasses import dataclass, replace
from typing import Dict, List, Optional, Tuple, cast

from sqlalchemy import func  # type: ignore
from sqlalchemy.orm import joinedload  # type: ignore

from aoiportal.cmsmirror.db import (  # type: ignore
    Contest,
    Dataset,
    Participation,
    Submission,
    SubmissionResult,
    SubtaskScore,
    Task,
    session,
)


@dataclass(frozen=True)
class TaskResult:
    score: float
    subtask_scores: Optional[List[float]]
    num_submissions: int


@dataclass(frozen=True)
class ParticipationResult:
    hidden: bool
    score: float
    task_scores: Dict[int, TaskResult]
    rank: Optional[int] = None


@dataclass(frozen=True)
class TaskData:
    name: str
    title: str
    max_score: float
    subtask_max_scores: Optional[List[int]]
    score_precision: int


@dataclass(frozen=True)
class ContestData:
    tasks: Dict[int, TaskData]
    results: Dict[int, ParticipationResult]
    score_precision: int


def _calc_ranks(contest_data: ContestData) -> None:
    parts = [
        (part_id, part_res)
        for part_id, part_res in contest_data.results.items()
        if not part_res.hidden
    ]
    parts.sort(key=lambda x: (-x[1].score, x[0]))
    rank = None
    for i, (part_id, part_res) in enumerate(parts):
        if i == 0 or part_res.score < parts[i - 1][1].score:
            rank = i + 1
        contest_data.results[part_id] = replace(part_res, rank=rank)
    for part_id in contest_data.results:
        if contest_data.results[part_id].hidden:
            contest_data.results[part_id] = replace(
                contest_data.results[part_id], rank=len(parts) + 1
            )


def get_contest_scores(contest_id: int) -> ContestData:
    contest: Optional[Contest] = (
        session.query(Contest)  # type: ignore
        .filter(Contest.id == contest_id)
        .options(
            joinedload(Contest.tasks),
            joinedload(Contest.participations),
        )
        .first()
    )
    if contest is None:
        raise ValueError(f"Contest {contest_id} not found")

    num_subs_by_part_task: List[Tuple[int, int, int]] = (
        session.query(  # type: ignore
            Submission.participation_id,
            Submission.task_id,
            func.count(Submission.id),
        )
        .join(Submission.participation)
        .join(Submission.task)
        .filter(Submission.official)
        .filter(Participation.contest_id == contest.id)
        .filter(Task.contest_id == contest.id)
        .group_by(Submission.participation_id, Submission.task_id)
        .having(func.count(Submission.id) > 0)
        .all()
    )
    num_subs_by_part_task_dict: Dict[Tuple[int, int], int] = {
        (part_id, task_id): num_subs
        for part_id, task_id, num_subs in num_subs_by_part_task
    }
    task_infos: Dict[int, TaskData] = {}
    results: Dict[int, ParticipationResult] = {}
    for part in contest.participations:
        part = cast(Participation, part)
        results[part.id] = ParticipationResult(
            hidden=part.hidden,
            score=0.0,
            task_scores={},
        )

    tasks: List[Task] = (
        session.query(Task)  # type: ignore
        .filter(Task.contest == contest)
        .options(
            joinedload(Task.active_dataset),
        )
        .all()
    )

    rows = (
        session.query(Task.id, Participation.id, func.max(SubmissionResult.score))  # type: ignore
        .join(SubmissionResult.submission)
        .join(Submission.participation)
        .join(Submission.task)
        .filter(Task.contest == contest)
        .filter(Task.score_mode == "max")
        .filter(Submission.official)
        .filter(SubmissionResult.dataset_id == Task.active_dataset_id)
        .group_by(Task.id, Participation.id)
        .having(func.max(SubmissionResult.score) > 0)
        .all()
    )
    max_task_part_scores: Dict[int, Dict[int, float]] = collections.defaultdict(dict)
    for tid, pid, score in rows:
        max_task_part_scores[tid][pid] = score

    rows = (
        session.query(  # type: ignore
            Task.id,
            Participation.id,
            SubtaskScore.subtask_idx,
            func.max(SubtaskScore.score),
        )
        .join(SubtaskScore.submission_result)
        .join(SubmissionResult.submission)
        .join(Submission.participation)
        .join(Submission.task)
        .filter(Task.contest == contest)
        .filter(Task.score_mode == "max_subtask")
        .filter(Submission.official)
        .filter(SubmissionResult.dataset_id == Task.active_dataset_id)
        .group_by(Task.id, Participation.id, SubtaskScore.subtask_idx)
        .having(func.max(SubtaskScore.score) > 0)
        .all()
    )
    max_subtask_task_part_subtask_max_scores: Dict[int, Dict[int, Dict[int, float]]] = (
        collections.defaultdict(dict)
    )
    for tid, pid, stidx, score in rows:
        max_subtask_task_part_subtask_max_scores[tid].setdefault(pid, {})[stidx] = score

    for task in tasks:
        dataset: Dataset = task.active_dataset
        if dataset.score_type == "Sum":
            max_score = dataset.score_type_parameters * len(dataset.testcases)
            max_scores = [max_score]
            has_subtasks = False
        elif dataset.score_type in ["GroupMin", "GroupMul", "GroupThreshold"]:
            max_scores = [p for p, _ in dataset.score_type_parameters]
            max_score = sum(max_scores, 0.0)
            has_subtasks = True
        else:
            raise ValueError(f"Unknown score type {dataset.score_type}")

        if task.score_mode == "max":
            by_pid = max_task_part_scores[task.id]
            for part in contest.participations:
                part = cast(Participation, part)
                score = round(by_pid.get(part.id, 0.0), task.score_precision)
                results[part.id].task_scores[task.id] = TaskResult(
                    score=score,
                    subtask_scores=None,
                    num_submissions=num_subs_by_part_task_dict.get(
                        (part.id, task.id), 0
                    ),
                )

        elif task.score_mode == "max_subtask":
            by_pid2 = max_subtask_task_part_subtask_max_scores[task.id]
            for part in contest.participations:
                part = cast(Participation, part)
                st_max_scores = by_pid2.get(part.id, {})
                subtask_scores = [
                    st_max_scores.get(i, 0.0) for i in range(1, len(max_scores) + 1)
                ]
                score = round(sum(subtask_scores), task.score_precision)
                pres = results[part.id]
                results[part.id].task_scores[task.id] = TaskResult(
                    score=score,
                    subtask_scores=subtask_scores,
                    num_submissions=num_subs_by_part_task_dict.get(
                        (part.id, task.id), 0
                    ),
                )
        else:
            raise ValueError(f"Unknown score mode {task.score_mode}")
        score = round(score, task.score_precision)
        task_infos[task.id] = TaskData(
            name=task.name,
            title=task.title,
            max_score=max_score,
            subtask_max_scores=max_scores if has_subtasks else None,
            score_precision=task.score_precision,
        )

    for part in contest.participations:
        part = cast(Participation, part)
        pres = results[part.id]
        results[part.id] = replace(
            pres,
            score=round(
                sum((tsc.score for tsc in pres.task_scores.values()), 0.0),
                contest.score_precision,
            ),
        )

    res = ContestData(
        tasks=task_infos,
        results=results,
        score_precision=contest.score_precision,
    )
    _calc_ranks(res)
    return res

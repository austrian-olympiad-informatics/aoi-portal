from typing import Dict, List, Tuple, Optional, cast
import datetime
from dataclasses import dataclass, replace
import collections

from sqlalchemy.orm import joinedload
from sqlalchemy import func

from aoiportal.cmsmirror.db import (  # type: ignore
    Participation,
    Submission,
    SubmissionResult,
    Task,
    Contest,
    Dataset,
    session,
    SubtaskScore,
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
        session.query(Contest)
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
        session.query(
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

    for task in contest.tasks:
        task = cast(Task, task)
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
            part_scores = (
                session.query(Participation.id, func.max(SubmissionResult.score))
                .join(SubmissionResult.submission)
                .join(Submission.participation)
                .filter(Submission.task == task)
                .filter(Submission.official)
                .filter(SubmissionResult.dataset == task.active_dataset)
                .group_by(Participation.id)
                .all()
            )
            part_scores: Dict[int, float] = dict(part_scores)
            for part in contest.participations:
                part = cast(Participation, part)
                score = round(part_scores.get(part.id, 0.0), task.score_precision)
                results[part.id].task_scores[task.id] = TaskResult(
                    score=score, subtask_scores=None,
                    num_submissions=num_subs_by_part_task_dict.get((part.id, task.id), 0),
                )

        elif task.score_mode == "max_subtask":
            part_subtask_max_scores = (
                session.query(Participation.id, SubtaskScore.subtask_idx, func.max(SubtaskScore.score))
                .join(SubtaskScore.submission_result)
                .join(SubmissionResult.submission)
                .join(Submission.participation)
                .filter(Submission.task == task)
                .filter(Submission.official)
                .filter(SubmissionResult.dataset == task.active_dataset)
                .group_by(Participation.id, SubtaskScore.subtask_idx)
                .all()
            )
            by_pid = collections.defaultdict(dict)
            for pid, stidx, stscore in part_subtask_max_scores:
                by_pid[pid][stidx] = stscore
            for part in contest.participations:
                part = cast(Participation, part)
                st_max_scores = by_pid.get(part.id, {})
                subtask_scores = [st_max_scores.get(i, 0.0) for i in range(1, len(max_scores)+1)]
                score = round(sum(subtask_scores), task.score_precision)
                pres = results[part.id]
                results[part.id].task_scores[task.id] = TaskResult(
                    score=score,
                    subtask_scores=subtask_scores,
                    num_submissions=num_subs_by_part_task_dict.get((part.id, task.id), 0),
                )
        else:
            raise ValueError(f"Unknown score mode {task.score_mode}")
        score = round(score, task.score_precision)
        task_infos[task.id] = TaskData(
            name=task.name, title=task.title, max_score=max_score,
            subtask_max_scores=max_scores if has_subtasks else None,
            score_precision=task.score_precision,
        )

    for part in contest.participations:
        part = cast(Participation, part)
        pres = results[part.id]
        results[part.id] = replace(
            pres, 
            score=round(sum((tsc.score for tsc in pres.task_scores.values()), 0.0), contest.score_precision)
        )
    
    res =  ContestData(
        tasks=task_infos,
        results=results,
        score_precision=contest.score_precision,
    )
    _calc_ranks(res)
    return res

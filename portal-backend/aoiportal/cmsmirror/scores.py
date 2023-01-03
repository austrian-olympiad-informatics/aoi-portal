from typing import Dict, List, Tuple, Optional
import datetime
from dataclasses import dataclass, replace
import collections

from sqlalchemy.orm import Load, joinedload, selectinload
from sqlalchemy import func

from aoiportal.cmsmirror.util import (  # type: ignore
    MaxAgeCache,
)
from aoiportal.cmsmirror.db import (  # type: ignore
    Participation,
    Submission,
    SubmissionResult,
    Task,
    Contest,
    Dataset,
    session,
)
from aoiportal.cmsmirror.util import (  # type: ignore
    score_calculation_single,
    MaxAgeCache,
    ScoreInputSingle,
)


@dataclass(frozen=True)
class SubtaskResult:
    fraction: float
    max_score: float
    score: float


@dataclass(frozen=True)
class TaskResult:
    score: float
    subtasks: Optional[List[SubtaskResult]]
    num_submissions: int


@dataclass
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
    score_precision: int


@dataclass(frozen=True)
class ContestData:
    tasks: Dict[int, TaskData]
    results: Dict[int, ParticipationResult]
    score_precision: int


CONTEST_SCORES_CACHE: MaxAgeCache[int, ContestData] = MaxAgeCache(
    datetime.timedelta(minutes=5)
)


def _load_rows(
    contest_id: int, filter_part_id: Optional[int] = None
) -> List[Tuple[SubmissionResult, Submission]]:
    q = (
        session.query(SubmissionResult, Submission)
        .join(SubmissionResult.submission)
        .join(Submission.participation)
        .join(Submission.task)
        .filter(Submission.official)
        .filter(SubmissionResult.dataset_id == Task.active_dataset_id)
        .filter(Task.contest_id == contest_id)
        .filter(SubmissionResult.score > 0)
        .options(
            Load(SubmissionResult).load_only(
                SubmissionResult.submission_id,
                SubmissionResult.dataset_id,
                SubmissionResult.compilation_outcome,
                SubmissionResult.score,
                SubmissionResult.score_details,
                SubmissionResult.compilation_outcome,
                SubmissionResult.evaluation_outcome,
            ),
            joinedload(SubmissionResult.submission),
            Load(Submission).load_only(
                Submission.id,
                Submission.uuid,
                Submission.timestamp,
                Submission.language,
                Submission.official,
            ),
            selectinload(Submission.task),
            Load(Task).load_only(
                Task.id,
                Task.name,
                Task.title,
                Task.score_precision,
                Task.score_mode,
            ),
            joinedload(Submission.participation),
            Load(Participation).load_only(
                Participation.id,
                Participation.hidden,
            ),
        )
        .order_by(Submission.timestamp.desc())
    )
    if filter_part_id is not None:
        q = q.filter(Participation.id == filter_part_id)
    return q.all()


def _build_part_result(
    prows: List[Tuple[SubmissionResult, Submission]],
    num_subs_by_part_task_dict: Dict[Tuple[int, int], int],
    contest: Contest,
    part: Participation,
) -> ParticipationResult:
    score_input_by_task: Dict[int, List[ScoreInputSingle]] = collections.defaultdict(
        list
    )
    for subres, sub in prows:
        score_input_by_task[sub.task.id].append(
            ScoreInputSingle(subres.score, subres.score_details)
        )
    task_scores: Dict[int, TaskResult] = {}
    score = 0
    for task in contest.tasks:
        calc = score_calculation_single(score_input_by_task[task.id], task.score_mode)
        task_scores[task.id] = TaskResult(
            score=calc.score,
            subtasks=[
                SubtaskResult(
                    fraction=subtask.fraction,
                    max_score=subtask.max_score,
                    score=subtask.score,
                )
                for subtask in calc.subtasks
            ]
            if calc.subtasks
            else None,
            num_submissions=num_subs_by_part_task_dict.get((part.id, task.id), 0),
        )
        score += round(calc.score, task.score_precision)
    score = round(score, contest.score_precision)
    return ParticipationResult(
        hidden=part.hidden,
        score=score,
        task_scores=task_scores,
    )


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


def invalidate_part_score(part_id: int) -> None:
    part: Optional[Participation] = (
        session.query(Participation).filter(Participation.id == part_id).first()
    )
    if part is None:
        raise ValueError(f"Participation {part_id} not found")
    contest = part.contest
    cached = CONTEST_SCORES_CACHE.get(contest.id)
    if cached is None:
        return
    rows = _load_rows(contest.id, filter_part_id=part_id)
    num_subs_by_task: List[Tuple[int, int]] = (
        session.query(
            Submission.task_id,
            func.count(Submission.id),
        )
        .join(Submission.participation)
        .filter(Submission.official)
        .filter(Participation.id == part_id)
        .group_by(Submission.task_id)
        .all()
    )
    num_subs_by_part_task_dict: Dict[Tuple[int, int], int] = {
        (part_id, task_id): num_subs for task_id, num_subs in num_subs_by_task
    }

    part_res = _build_part_result(
        prows=rows,
        num_subs_by_part_task_dict=num_subs_by_part_task_dict,
        contest=contest,
        part=part,
    )
    cached.results[part_id] = part_res
    _calc_ranks(cached)


def get_contest_scores(contest_id: int) -> ContestData:
    cached = CONTEST_SCORES_CACHE.get(contest_id)
    if cached is not None:
        return cached
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
    tasks: List[Task] = contest.tasks
    rows = _load_rows(contest_id)
    num_subs_by_part_task: List[Tuple[int, int, int]] = (
        session.query(
            Submission.participation_id,
            Submission.task_id,
            func.count(Submission.id),
        )
        .join(Submission.participation)
        .filter(Submission.official)
        .filter(Participation.contest_id == contest_id)
        .group_by(Submission.participation_id, Submission.task_id)
        .all()
    )
    num_subs_by_part_task_dict: Dict[Tuple[int, int], int] = {
        (part_id, task_id): num_subs
        for part_id, task_id, num_subs in num_subs_by_part_task
    }

    participations: List[Participation] = contest.participations

    rows_by_part: Dict[
        int, List[Tuple[SubmissionResult, Submission]]
    ] = collections.defaultdict(list)
    for subres, sub in rows:
        rows_by_part[sub.participation_id].append((subres, sub))

    part_results: Dict[int, ParticipationResult] = {}

    for part in participations:
        part_results[part.id] = _build_part_result(
            prows=rows_by_part[part.id],
            num_subs_by_part_task_dict=num_subs_by_part_task_dict,
            contest=contest,
            part=part,
        )

    tasks_data: Dict[int, TaskData] = {}
    for task in tasks:
        ds: Dataset = task.active_dataset
        if ds.score_type == "Sum":
            max_score = ds.score_type_parameters * len(ds.testcases)
        else:
            max_score = sum(p for p, _ in ds.score_type_parameters)
        tasks_data[task.id] = TaskData(
            name=task.name,
            title=task.title,
            max_score=max_score,
            score_precision=task.score_precision,
        )

    contest_data = ContestData(
        tasks=tasks_data,
        results=part_results,
        score_precision=contest.score_precision,
    )
    _calc_ranks(contest_data)
    CONTEST_SCORES_CACHE.put(contest_id, contest_data)
    return contest_data

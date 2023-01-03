from typing import Dict, List, Tuple, Optional
import datetime
from dataclasses import dataclass
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
    ScoreInput,
    score_calculation,
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
    datetime.timedelta(seconds=5)
)


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
    rows: List[Tuple[SubmissionResult, Submission]] = (
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
        .all()
    )
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
        prows = rows_by_part[part.id]
        score_input_by_task: Dict[
            int, List[ScoreInputSingle]
        ] = collections.defaultdict(list)
        for subres, sub in prows:
            score_input_by_task[sub.task.id].append(
                ScoreInputSingle(subres.score, subres.score_details)
            )
        task_scores: Dict[int, TaskResult] = {}
        score = 0
        for task in tasks:
            calc = score_calculation_single(
                score_input_by_task[task.id], task.score_mode
            )
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
        part_results[part.id] = ParticipationResult(
            hidden=part.hidden,
            score=score,
            task_scores=task_scores,
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
    
    part_to_score = {
        part_id: round(sum((x.score for x in part_result.task_scores.values()), 0.0), contest.score_precision)
        for part_id, part_result in part_results.items()
        if not part_result.hidden
    }
    part_to_score[None] = 0.0
    sorted_scores = sorted(part_to_score.values(), reverse=True)
    for part in participations:
        my_score = part_to_score.get(part.id, 0.0)
        global_rank = sorted_scores.index(my_score) + 1
        part_results[part.id].rank = global_rank

    contest_data = ContestData(
        tasks=tasks_data,
        results=part_results,
        score_precision=contest.score_precision,
    )
    CONTEST_SCORES_CACHE.put(contest_id, contest_data)
    return contest_data

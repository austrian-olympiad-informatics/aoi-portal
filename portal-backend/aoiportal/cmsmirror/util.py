import collections
import hashlib
import io
import json
import socket
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from uuid import uuid4

from aoiportal.cmsmirror.db import FSObject, LargeObject, session  # type: ignore


@dataclass
class Cache:
    data: Dict[str, bytes] = field(default_factory=dict)
    max_size: int = 128
    max_entry_len: int = 0


STATIC_FILES_CACHE = Cache()
USER_CACHE = Cache(max_entry_len=1 * 1024 * 1024)


def get_digest_cache(cache: Cache, digest: str) -> Optional[bytes]:
    val = cache.data.pop(digest, None)
    if val is None:
        return None
    # move to back
    cache.data[digest] = val
    return val


def put_digest_cache(cache: Cache, digest: str, data: bytes) -> None:
    while len(cache.data) >= cache.max_size:
        key = next(iter(cache.data.keys()))
        cache.data.pop(key, None)
    cache.data[digest] = data


def calc_digest(data: bytes) -> str:
    h = hashlib.new("sha1")
    h.update(data)
    return h.hexdigest()


def open_digest(digest: str, cache: Optional[Cache] = None) -> io.BytesIO:
    if cache is not None:
        cached = get_digest_cache(cache, digest)
        if cached is not None:
            return io.BytesIO(cached)
    fso = session.query(FSObject).filter(FSObject.digest == digest).first()
    if fso is None:
        raise KeyError("File not found.")
    lo = fso.get_lobject(mode="rb")
    if cache is not None:
        if cache.max_entry_len != 0:
            lo.seek(0, io.SEEK_END)
            sz = lo.tell()
            lo.seek(0, io.SEEK_SET)
            if sz > cache.max_entry_len:
                return lo

        data = lo.read()
        put_digest_cache(cache, digest, data)
        lo.close()
        return io.BytesIO(data)

    return lo


def create_file(content: bytes, description: str) -> str:
    digest = calc_digest(content)
    fso = session.query(FSObject).filter(FSObject.digest == digest).first()
    if fso is not None:
        return digest
    lo = LargeObject(0, mode="wb")
    lo.write(content)
    lo.close()

    fso = FSObject(description=description)
    fso.digest = digest
    fso.loid = lo.loid
    session.add(fso)
    return digest


def _send_rpc_evaluation_service(method: str, data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 25000))
    payload = json.dumps(
        {
            "__id": uuid4().hex,
            "__method": method,
            "__data": data,
        }
    )
    sock.sendall(payload.encode("ascii") + b"\r\n")
    sock.close()


def send_sub_to_evaluation_service(subid: int):
    _send_rpc_evaluation_service("new_submission", {"submission_id": subid})


def send_user_eval_to_evaluation_service(uevalid: int):
    _send_rpc_evaluation_service("new_user_eval", {"user_eval_id": uevalid})


@dataclass(frozen=True)
class ScoreInput:
    task_id: int
    part_id: int
    score_mode: str
    score: float
    score_details: dict


@dataclass(frozen=True)
class SubtaskResult:
    fraction: float
    max_score: float
    score: float


NULL_SUBTASK_RESULT = SubtaskResult(fraction=0.0, max_score=0.0, score=0.0)


@dataclass(frozen=True)
class ScoreTaskPart:
    score: float
    subtasks: Optional[List[SubtaskResult]] = None


def score_calculation(rows: List[ScoreInput]) -> Dict[Tuple[int, int], ScoreTaskPart]:
    task_score_mode = {}
    by_task_part = collections.defaultdict(list)

    for row in rows:
        task_score_mode[row.task_id] = row.score_mode
        by_task_part[(row.task_id, row.part_id)].append((row.score, row.score_details))

    result = {}

    for k, v in by_task_part.items():
        task_id, _ = k
        score_mode = task_score_mode[task_id]
        if score_mode == "max":
            result[k] = ScoreTaskPart(score=max(s for s, _ in v))
        elif score_mode == "max_subtask":
            subtasks: Dict[int, SubtaskResult] = {}
            for _, details in v:
                if not details or "max_score" not in details[0]:
                    continue
                for st in details:
                    sti = st["idx"]
                    prev = subtasks.get(sti, NULL_SUBTASK_RESULT)
                    subtasks[sti] = SubtaskResult(
                        fraction=max(prev.fraction, st["score_fraction"]),
                        max_score=max(prev.max_score, st["max_score"]),
                        score=max(prev.score, st["score_fraction"] * st["max_score"]),
                    )
            result[k] = ScoreTaskPart(
                score=sum(v.score for v in subtasks.values()),
                subtasks=[subtasks[k] for k in sorted(subtasks.keys())],
            )
        else:
            raise ValueError(f"Unsupported score mode {score_mode}")

    return result

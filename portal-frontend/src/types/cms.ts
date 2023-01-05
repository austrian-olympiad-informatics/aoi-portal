export interface Announcement {
  timestamp: string;
  subject: string;
  text: string;
  task: string | null;
}

export interface Message {
  timestamp: string;
  subject: string;
  text: string;
  task: string | null;
}

export interface Question {
  timestamp: string;
  subject: string;
  text: string;
  reply: null | {
    timestamp: string;
    subject: string;
    text: string;
  };
  task: string | null;
}
export interface ContestBase {
  name: string;
  description: string;
  start: string;
  stop: string;
  analysis: null | {
    start: string;
    stop: string;
  };
  announcements: Announcement[];
  messages: Message[];
  questions: Question[];
}

export interface TaskShort {
  name: string;
  title: string;
}

export interface ActiveContest extends ContestBase {
  is_active: true;
  tasks: TaskShort[];
  languages: string[];
}

export interface InactiveContest extends ContestBase {
  is_active: false;
}

export type Contest = ActiveContest | InactiveContest;

export type TaskType =
  | "batch"
  | "communication"
  | "ojuz"
  | "output_only"
  | "two_steps";

export interface ScoringSum {
  type: "sum";
  score_per_testcase: number;
  num_testcases: number;
}
export interface ScoringGroup {
  type: "group_min" | "group_mul" | "group_threshold";
  subtasks: number[];
}

export interface SubmissionResultCompilingShort {
  status: "compiling";
  meme_digest: string | null;
}
export interface SubmissionResultCompilationFailedShort {
  status: "compilation_failed";
  meme_digest: string | null;
}
export interface SubmissionResultEvaluatingShort {
  status: "evaluating";
  meme_digest: string | null;
}
export interface SubmissionResultScoringShort {
  status: "scoring";
  meme_digest: string | null;
}
export interface SubmissionResultScoredShort {
  status: "scored";
  score: number;
  subtasks?: {
    max_score: number;
    fraction: number;
  }[];
  meme_digest: string | null;
}

export interface SubmissionShort {
  uuid: string;
  timestamp: string;
  language: string;
  files: string[];
  official: boolean;
  result:
    | SubmissionResultCompilingShort
    | SubmissionResultCompilationFailedShort
    | SubmissionResultEvaluatingShort
    | SubmissionResultScoringShort
    | SubmissionResultScoredShort;
}

export interface Task {
  name: string;
  title: string;
  contest: {
    name: string;
    description: string;
  };
  feedback_level: string;
  statements: {
    language: string;
    digest: string;
  }[];
  statement_html_digest: string | null;
  default_input_digest: string | null;
  attachments: {
    filename: string;
    digest: string;
  }[];
  time_limit: number | null;
  memory_limit: number | null;
  task_type: TaskType;
  scoring: ScoringSum | ScoringGroup;
  submissions: SubmissionShort[];
  score: number;
  max_score: number;
  score_precision: number;
  score_mode: "max" | "max_subtask" | "max_tokened_last";
  score_subtasks: null | {
    fraction: number;
    max_score: number;
    score: number;
  }[];
  submission_format: string[];
  languages: string[];
  language_templates: {
    filename: string;
    digest: string;
  }[];
}

export interface SubmissionResultCompiling {
  status: "compiling";
  meme_digest: string | null;
}
export interface SubmissionResultWithCompilationResult {
  compilation_text: string[];
  compilation_stdout: string;
  compilation_stderr: string;
  compilation_time: number;
  compilation_wall_clock_time: number;
  compilation_memory: number;
}
export interface SubmissionResultCompilationFailed
  extends SubmissionResultWithCompilationResult {
  status: "compilation_failed";
  meme_digest: string | null;
}
export interface SubmissionResultEvaluating
  extends SubmissionResultWithCompilationResult {
  status: "evaluating";
  meme_digest: string | null;
}
export interface SubmissionResultScoring
  extends SubmissionResultWithCompilationResult {
  status: "scoring";
  meme_digest: string | null;
}
export interface SubmissionResultScoredSum
  extends SubmissionResultWithCompilationResult {
  status: "scored";
  testcases: {
    text: string[];
    time: number;
    memory: number;
    outcome: string;
  }[];
  meme_digest: string | null;
}
export interface SubmissionResultScoredGroups
  extends SubmissionResultWithCompilationResult {
  status: "scored";
  subtasks: {
    max_score: number;
    fraction: number;
    testcases: {
      text: string[];
      time: number;
      memory: number;
      outcome: string;
    }[];
  }[];
  meme_digest: string | null;
}
export type SubmissionResultScored =
  | SubmissionResultScoredSum
  | SubmissionResultScoredGroups;

export interface Submission {
  uuid: string;
  timestamp: string;
  language: string;
  files: {
    filename: string;
    digest: string;
  }[];
  official: boolean;
  result:
    | SubmissionResultCompiling
    | SubmissionResultCompilationFailed
    | SubmissionResultEvaluating
    | SubmissionResultScoring
    | SubmissionResultScored;
}

export interface QuestionParams {
  subject: string;
  text: string;
}

export interface SubmitParams {
  language: string;
  files: {
    filename: string;
    content: string;
  }[];
}
export interface SubmitResult {
  uuid: string;
  submission: SubmissionShort;
}

export interface UserEvalSubmitParams {
  language: string;
  files: {
    filename: string;
    content: string;
  }[];
  input: string;
}
export interface UserEvalSubmitResult {
  uuid: string;
}

export interface UserEvalResultCompiling {
  status: "compiling";
}
export interface UserEvalResultWithCompilationResult {
  compilation_text: string[];
  compilation_stdout: string;
  compilation_stderr: string;
  compilation_time: number;
  compilation_wall_clock_time: number;
  compilation_memory: number;
}
export interface UserEvalResultCompilationFailed
  extends UserEvalResultWithCompilationResult {
  status: "compilation_failed";
}
export interface UserEvalResultEvaluating
  extends UserEvalResultWithCompilationResult {
  status: "evaluating";
}
export interface UserEvalResultEvaluated
  extends UserEvalResultWithCompilationResult {
  status: "evaluated";
  execution_time: number;
  execution_wall_clock_time: number;
  execution_memory: number;
  evaluation_outcome: string;
  output?: string;
  evaluation_text: string[];
}
export type UserEvalResult =
  | UserEvalResultCompiling
  | UserEvalResultCompilationFailed
  | UserEvalResultEvaluating
  | UserEvalResultEvaluated;

export interface UserEval {
  uuid: string;
  timestamp: string;
  language: string;
  files: string[];
  result: UserEvalResult;
}

export interface CheckNotificationsParams {
  last_notification?: string;
}

export interface CheckNotificationsResult {
  new_announcements: Announcement[];
  new_messages: Message[];
  new_replies: Question[];
}

export interface ContestTaskScore {
  task: string;
  score: number;
  subtask_scores: number[] | null;
  subtask_max_scores: number[] | null;
  max_score: number;
  score_precision: number;
}
export interface ContestTaskScores {
  score: number;
  max_score: number;
  score_precision: number;
  tasks: ContestTaskScore[];
  global_rank?: number;
  points_to_next_rank?: number;
}

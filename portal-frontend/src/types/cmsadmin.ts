export interface AdminTaskShort {
  id: number;
  name: string;
  title: string;
}
export interface AdminUserShort {
  id: number;
  first_name: string;
  last_name: string;
  username: string;
}
export interface AdminParticipationShort {
  id: number;
  user: AdminUserShort;
  hidden: boolean;
}
export interface AdminContestShort {
  id: number;
  name: string;
  description: string;
}

export interface AdminContest {
  id: number;
  name: string;
  description: string;
  start: string;
  stop: string;
  analysis: {
    start: string;
    stop: string;
  } | null;
  tasks: AdminTaskShort[];
  score_precision: number;
  languages: string[];
  allow_frontendv2: boolean;
}

export type AdminContests = AdminContest[];

export interface AdminAnnouncement {
  id: number;
  timestamp: string;
  subject: string;
  text: string;
  task: AdminTaskShort | null;
}

export type AdminAnnouncements = AdminAnnouncement[];

export interface AdminQuestion {
  id: number;
  timestamp: string;
  subject: string;
  text: string;
  task: AdminTaskShort | null;
  ignored: boolean;
  reply: {
    timestamp: string;
    subject: string;
    text: string;
  } | null;
  participation: AdminParticipationShort;
}

export interface AdminMessage {
  id: number;
  timestamp: string;
  subject: string;
  text: string;
  task: AdminTaskShort | null;
  ignored: boolean;
  reply: {
    timestamp: string;
    subject: string;
    text: string;
  } | null;
  participation: AdminParticipationShort;
}

export interface AdminSubmissionResultCompilingShort {
  status: "compiling";
  meme_digest: string | null;
}
export interface AdminSubmissionResultCompilationFailedShort {
  status: "compilation_failed";
  meme_digest: string | null;
}
export interface AdminSubmissionResultEvaluatingShort {
  status: "evaluating";
  meme_digest: string | null;
}
export interface AdminSubmissionResultScoringShort {
  status: "scoring";
  meme_digest: string | null;
}
export interface AdminSubmissionResultScoredShort {
  status: "scored";
  meme_digest: string | null;
  score: number;
  score_precision: number;
  subtasks?: {
    max_score: number;
    fraction: number;
  }[];
}
export type AdminSubmissionResultShort =
  | AdminSubmissionResultCompilingShort
  | AdminSubmissionResultCompilationFailedShort
  | AdminSubmissionResultEvaluatingShort
  | AdminSubmissionResultScoringShort
  | AdminSubmissionResultScoredShort;

export interface AdminSubmissionBase {
  id: number;
  uuid: string;
  timestamp: string;
  language: string;
  official: boolean;
  participation: AdminParticipationShort;
  task: AdminTaskShort;
  contest: AdminContestShort;
  comment: string;
  max_score: number;
}

export interface AdminSubmissionShort extends AdminSubmissionBase {
  result: AdminSubmissionResultShort;
}

export interface AdminSubmissionResultCompilingDetailed {
  status: "compiling";
  meme_digest: string | null;
}
export interface AdminExecutable {
  id: number;
  filename: string;
  digest: string;
}
export interface AdminSubmissionResultWithCompilation {
  compilation_text: string;
  compilation_stdout: string;
  compilation_stderr: string;
  compilation_time: number;
  compilation_wall_clock_time: number;
  compilation_memory: number;
  compilation_tries: number;
  compilation_shard: number;
  compilation_sandbox: string;
  executables: AdminExecutable[];
}
export interface AdminSubmissionResultCompilationFailedDetailed
  extends AdminSubmissionResultWithCompilation {
  status: "compilation_failed";
  meme_digest: string | null;
}
export interface AdminSubmissionResultEvaluatingDetailed
  extends AdminSubmissionResultWithCompilation {
  status: "evaluating";
  meme_digest: string | null;
}
export interface AdminSubmissionResultWithEvaluation
  extends AdminSubmissionResultWithCompilation {
  evaluation_tries: number;
  evaluations: {
    id: number;
    testcase: {
      id: number;
      codename: string;
      public: boolean;
      input_digest: string;
      output_digest: string;
    };
    outcome: string;
    text: string;
    execution_time: number;
    execution_wall_clock_time: number;
    execution_memory: number;
    evaluation_shard: number;
    evaluation_sandbox: string;
  }[];
}
export interface AdminSubmissionResultScoringDetailed
  extends AdminSubmissionResultWithCompilation {
  status: "scoring";
  meme_digest: string | null;
}
export interface AdminSubmissionResultScoredDetailed
  extends AdminSubmissionResultWithCompilation {
  status: "scored";
  meme_digest: string | null;
  score: number;
  score_precision: number;
  testcases?: {
    text: string;
    time: number;
    memory: number;
    outcome: string;
  }[];
  subtasks?: {
    max_score: number;
    fraction: number;
    testcases: {
      text: string;
      time: number;
      memory: number;
      outcome: string;
    }[];
  }[];
}
export type AdminSubmissionResultDetailed =
  | AdminSubmissionResultCompilingDetailed
  | AdminSubmissionResultCompilationFailedDetailed
  | AdminSubmissionResultEvaluatingDetailed
  | AdminSubmissionResultScoringDetailed
  | AdminSubmissionResultScoredDetailed;

export interface AdminSubmissionDetailed extends AdminSubmissionBase {
  result: AdminSubmissionResultDetailed;
  files: {
    filename: string;
    digest: string;
  }[];
}

export interface PaginatedResult<T> {
  page: number;
  per_page: number;
  total: number;
  items: T[];
}

export type AdminSubmissionsPaginated = PaginatedResult<AdminSubmissionShort>;

export interface AdminSubmissionsParams {
  contest_name: string | null;
  task_id: number | null;
  user_id: number | null;
}

export interface AdminTask {
  id: number;
  name: string;
  title: string;
  contest: AdminContestShort | null;
}
export interface AdminManager {
  id: number;
  filename: string;
  digest: string;
}
export interface AdminTestcase {
  id: number;
  codename: string;
  public: boolean;
  input_digest: string;
  output_digest: string;
}
export interface AdminLanguageTemplate {
  id: number;
  filename: string;
  digest: string;
}
export interface AdminTestManager {
  id: number;
  filename: string;
  digest: string;
}
export interface AdminDataset {
  id: number;
  time_limit: number | null;
  memory_limit: number | null;
  task_type: string;
  task_type_parameters: any[];
  score_type: string;
  score_type_parameters: any[];
  managers: AdminManager[];
  testcases: AdminTestcase[];
  language_templates: AdminLanguageTemplate[];
  test_managers: AdminTestManager[];
}
export interface AdminStatement {
  id: number;
  language: string;
  digest: string;
}
export interface AdminAttachment {
  id: number;
  filename: string;
  digest: string;
}
export interface AdminTaskDetailed extends AdminTask {
  statements: AdminStatement[];
  attachments: AdminAttachment[];
  submission_format: string[];
  score_precision: number;
  score_mode: string;
  active_dataset: AdminDataset;
}
export type AdminContestTasks = AdminTask[];

export type AdminContestParticipations = AdminParticipationShort[];
export type AdminParticipation = AdminParticipationShort;

export interface AdminUser {
  id: number;
  first_name: string;
  last_name: string;
  username: string;
  participations: {
    id: number;
    contest: AdminContestShort;
  }[];
}
export type AdminUsers = AdminUser[];

export interface AdminAllTask {
  id: number;
  name: string;
  title: string;
  contest: AdminContestShort | null;
}
export type AdminAllTasks = AdminAllTask[];

export interface AdminMeme {
  id: number;
  filename: string;
  digest: string;
  min_score: number;
  max_score: number;
  factor: number;
  task: AdminTaskShort | null;
}
export type AdminMemes = AdminMeme[];

export interface AdminUserEvalResultCompilingShort {
  status: "compiling";
}
export interface AdminUserEvalResultCompilationFailedShort {
  status: "compilation_failed";
}
export interface AdminUserEvalResultEvaluatingShort {
  status: "evaluating";
}
export interface AdminUserEvalResultEvaluatedShort {
  status: "evaluated";
}
export type AdminUserEvalResultShort =
  | AdminUserEvalResultCompilingShort
  | AdminUserEvalResultCompilationFailedShort
  | AdminUserEvalResultEvaluatingShort
  | AdminUserEvalResultEvaluatedShort;

export interface AdminUserEvalBase {
  id: number;
  uuid: string;
  timestamp: string;
  language: string;
  participation: AdminParticipationShort;
  contest: AdminContestShort;
  task: AdminTaskShort;
}
export interface AdminUserEvalShort extends AdminUserEvalBase {
  result: AdminUserEvalResultShort;
}
export type AdminUserEvalsPaginated = PaginatedResult<AdminUserEvalShort>;

export interface AdminUserEvalResultCompilingDetailed {
  status: "compiling";
}
export interface AdminUserEvalResultWithCompilation {
  compilation_text: string;
  compilation_stdout: string;
  compilation_stderr: string;
  compilation_time: number;
  compilation_wall_clock_time: number;
  compilation_memory: number;
  compilation_tries: number;
  compilation_shard: number;
  compilation_sandbox: string;
  executables: AdminExecutable[];
}
export interface AdminUserEvalResultCompilationFailedDetailed
  extends AdminUserEvalResultWithCompilation {
  status: "compilation_failed";
}
export interface AdminUserEvalResultEvaluatingDetailed
  extends AdminUserEvalResultWithCompilation {
  status: "evaluating";
}
export interface AdminUserEvalResultEvaluatedDetailed
  extends AdminUserEvalResultWithCompilation {
  status: "evaluated";
  evaluation_tries: number;
  execution_time: number;
  execution_wall_clock_time: number;
  execution_memory: number;
  evaluation_shard: number;
  evaluation_sandbox: string;
  output_digest: string;
}
export type AdminUserEvalResultDetailed =
  | AdminUserEvalResultCompilingDetailed
  | AdminUserEvalResultCompilationFailedDetailed
  | AdminUserEvalResultEvaluatingDetailed
  | AdminUserEvalResultEvaluatedDetailed;

export interface AdminUserEvalDetailed extends AdminUserEvalBase {
  input_digest: string;
  result: AdminUserEvalResultDetailed;
  files: {
    filename: string;
    digest: string;
  }[];
}

export interface AdminContestRanking {
  tasks: {
    id: number;
    name: string;
    title: string;
    max_score: number;
    subtask_max_scores: number[] | null,
    score_precision: number;
  }[];
  score_precision: number,
  results: {
    id: number;
    hidden: boolean;
    score: number;
    rank: number;
    task_scores: {
      id: number,
      score: number;
      subtask_scores: number[] | null;
      num_submissions: number;
    }[];
  }[];
}


export interface AdminParticipationScore {
  tasks: {
    id: number;
    name: string;
    title: string;
    max_score: number;
    subtask_max_scores: number[] | null,
    score_precision: number;
  }[];
  score_precision: number,
  score: number;
  rank: number;
  task_scores: {
    id: number,
    score: number;
    subtask_scores: number[] | null;
    num_submissions: number;
  }[];
  hidden: boolean;
}

export interface AdminParticipationUpdateParams {
  hidden?: boolean;
}

// API functions for fetching applications data

export interface Application {
  application_id: string;
  application_type: string;
  status: string;
  underwriter_status: string;
  underwriter_review: string | null;
  overall_document_check_status: string;
  document_result: Array<{
    reason: string;
    result: boolean;
    optional: boolean;
    document_type: string;
    document_category: string;
  }>;
  system_status: string;
  policy_check: string;
  policy_check_result: Array<{
    validation_result: string;
    comment: string;
    doc_type: string;
    policy_name: string;
  }>;
  documents?: Array<{
    evaluations: Record<string, unknown>;
    url: string;
  }>;
  created_at: string;
  updated_at: string;
  created_by: string;
  updated_by: string;
}

export interface ApplicationsResponse {
  applications: Application[];
  total: number;
}

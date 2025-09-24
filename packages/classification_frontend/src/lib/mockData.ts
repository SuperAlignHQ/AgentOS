export const applications = [
  {
    application_id: "JFP84J9J9T",
    application_type: "A1",
    status: "approved",
    underwriter_status: "approved",
    underwriter_review: "this is fine",
    overall_document_check_status: "approved",
    system_status: "Approved",
    policy_check: "approved",
    fraud_check: "approved",
    documents: [
      {
        evaluations: {
          field_one: "third value",
          field_two: "fourth value"
        },
        url: "/public/test.pdf"
      },
      {
        evaluations: {
          field_one: "first value",
          field_two: "second value"
        },
        url: "/public/test.pdf"
      }
    ],
    document_result: [
      {
        review: "Payslip is valid",
        status: "passed",
        document_type: "payslip",
        document_category: "income",
      },
      {
        review: "Bank statement is valid",
        status: "failed",
        document_type: "bank_statement",
        document_category: "income",
      },
      {
        review: "Passport is valid",
        status: "passed",
        document_type: "passport",
        document_category: "id_proof",
      },
    ],
    created_at: "2025-08-27T17:51:05.904924Z",
    updated_at: "2025-08-27T17:51:05.904975Z",
    created_by: "Jashan",
    updated_by: "Jashan",
  },
  {
    application_id: "J39JIWJ39J",
    application_type: "A1",
    status: "declined",
    overall_document_check_status: "approved",
    system_status: "Approved",
    underwriter_status: "pending",
    underwriter_review: "",
    policy_check: "approved",
    fraud_check: "approved",
    documents: [
      {
        evaluations: {
          field_one: "value one",
          field_two: "value two",
          field_three: "value three"
        },
        url: "/public/test.pdf"
      }
    ],
    document_result: [
      {
        reason: "passport is missing from the application",
        result: false,
        optional: true,
        document_type: "passport",
        document_category: "id_proof",
      },
      {
        reason: "payslip is present",
        result: true,
        optional: false,
        document_type: "payslip",
        document_category: "income",
      },
      {
        reason: "bank_statement is missing from the application",
        result: false,
        optional: false,
        document_type: "bank_statement",
        document_category: "income",
      },
    ],
    created_at: "2025-09-12T11:06:58.139158Z",
    updated_at: "2025-09-12T11:06:58.139251Z",
    created_by: "Jashan",
    updated_by: "Jashan",
  },
  {
    application_id: "AJOEFIO4JU",
    application_type: "A1",
    status: "approved",
    Overall_document_check_status: "approved",
    system_status: "Approved",
    underwriter_status: "pending",
    underwriter_review: "",
    policy_check: "approved",
    fraud_check: "approved",
    document_result: [
      {
        reason: "Payslip is valid",
        result: true,
        optional: true,
        document_type: "passport",
        document_category: "id_proof",
      },
      {
        reason: "Payslip is valid",
        result: true,
        optional: false,
        document_type: "payslip",
        document_category: "income",
      },
      {
        reason: "Payslip is valid",
        result: true,
        optional: false,
        document_type: "bank_statement",
        document_category: "income",
      },
    ],
    created_at: "2025-09-05T20:15:45.002110Z",
    updated_at: "2025-09-05T20:15:45.002236Z",
    created_by: "Jashan",
    updated_by: "Jashan",
  },
  {
    application_id: "DSJHKF98U4",
    application_type: "A1",
    status: "approved",
    Overall_document_check_status: "approved",
    system_status: "Approved",
    underwriter_status: "pending",
    underwriter_review: "",
    policy_check: "approved",
    fraud_check: "approved",
    document_result: [
      {
        reason: "passport is missing from the application",
        result: false,
        optional: true,
        document_type: "passport",
        document_category: "id_proof",
      },
      {
        reason: "payslip is present",
        result: true,
        optional: false,
        document_type: "payslip",
        document_category: "income",
      },
      {
        reason: "bank_statement is present",
        result: true,
        optional: false,
        document_type: "bank_statement",
        document_category: "income",
      },
    ],
    created_at: "2025-09-11T05:57:24.912323Z",
    updated_at: "2025-09-11T05:57:24.912386Z",
    created_by: "Jashan",
    updated_by: "Jashan",
  },
  {
    application_id: "JI0U4F08J4",
    application_type: "A1",
    status: "needs_review",
    Overall_document_check_status: "approved",
    system_status: "Approved",
    underwriter_status: "pending",
    underwriter_review: null,
    policy_check: "approved",
    fraud_check: "approved",
    document_result: [],
    created_at: "2025-08-27T16:38:56.734164Z",
    updated_at: "2025-08-27T16:38:56.734318Z",
    created_by: "Jashan",
    updated_by: "Jashan",
  },
];

// Mock data for document check
export const documentCheckData = [
  {
    category: "Income",
    documents: "Contract of employment",
    validation: "Fail",
    result:
      "P60 is older than 12 months. Minimum 3 months of Payslips required.",
    isFail: true,
  },
  {
    category: "Expenditure",
    documents: "Bank statement",
    validation: "Pass",
    result: "All required documents are present",
    isFail: false,
  },
  {
    category: "ID Proof",
    documents: "Marriage certificate",
    validation: "Pass",
    result: "All required documents are present",
    isFail: false,
  },
];

// Mock data for policy check
export const policyCheckData = [
  {
    reasonCode: "OMR-20250724-1234",
    policyName: "Remortgage",
    documents: "Contract of employment",
    validation: "Fail",
    review:
      "P60 is older than 12 months. Minimum 3 months of Payslips required.",
    isFail: true,
  },
  {
    reasonCode: "OMR-20250724-1235",
    policyName: "Remortgage",
    documents: "Bank statement",
    validation: "Pass",
    review: "All required documents are present",
    isFail: false,
  },
];

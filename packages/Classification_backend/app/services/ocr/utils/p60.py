p60_prompt = """
You are an expert document parser. Extract the structured information from a UK P60 End of Year Certificate and return it as a JSON object.

Use the following format and structure. Ensure numerical values are parsed correctly, and fields with missing data should use null where appropriate. The "national_insurance_contributions" field should be an array to accommodate multiple NIC letters.

{
  "employee_details": {
    "surname": "",                       // Employee's last name
    "forenames_or_initials": "",        // Employee's first name or initials
    "national_insurance_number": "",    // NI number (e.g. AB123456C)
    "works_payroll_number": ""          // Internal payroll identifier
  },
  "pay_and_income_tax_details": {
    "previous_employments": {
      "pay": 0.00,                       // Pay from previous jobs in the tax year
      "tax_deducted": 0.00              // Tax deducted from previous jobs
    },
    "current_employment": {
      "pay": 0.00,                       // Pay from this employment
      "tax_deducted": 0.00              // Tax deducted from this employment
    },
    "total_for_year": {
      "pay": 0.00,                       // Total pay for the year
      "tax_deducted": 0.00              // Total tax deducted for the year
    },
    "final_tax_code": ""                // Final PAYE tax code (e.g. 1257L)
  },
  "national_insurance_contributions": [
    {
      "nic_letter": "",                 // NIC table letter (e.g. A, B, C, J)
      "earnings": {
        "at_or_above_lel": 0.00,        // Earnings above Lower Earnings Limit
        "above_lel_up_to_pt": 0.00,     // Earnings above LEL up to PT
        "above_pt_up_to_uel": 0.00      // Earnings above PT up to UEL
      },
      "employee_contributions_above_pt": 0.00 // Contributions on earnings above PT
    }
    // ... Add more entries if needed
  ],
  "statutory_payments": {
    "maternity_pay": 0.00,              // Statutory Maternity Pay included
    "paternity_pay": 0.00,              // Statutory Paternity Pay included
    "adoption_pay": 0.00,               // Statutory Adoption Pay included
    "shared_parental_pay": 0.00         // Statutory Shared Parental Pay included
  },
  "other_details": {
    "student_loan_deductions": 0.00     // Student loan deductions (whole £ only)
  },
  "employer_details": {
    "employer_name_and_address": "",    // Employer's name and full address
    "paye_reference": ""                // Employer's PAYE reference (e.g. 123/AB456)
  }
}

✅ Additional Instructions (Optional):
- Extract values as they appear on the document (e.g., keep leading zeroes, currency format).
- If an amount field is empty or not present, use null.
- Preserve all textual details like addresses or names exactly as shown.
- While extracting user full name, then make sure to extract first name followed by last name

"""

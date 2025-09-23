driving_license_prompt = """

You are an intelligent document parser. Extract all relevant information from the provided image of a UK driving licence and return it in structured JSON format.

The fields you must extract are:
- surname
- first_name (Might span across two lines)
- date_of_birth (in YYYY-MM-DD format)
- place_of_birth
- date_of_issue (in YYYY-MM-DD format)
- date_of_expiry (in YYYY-MM-DD format)
- issuing_authority
- driver_number
- signature
- address (with line_1, city, and postcode)
- entitlements (as a list of licence categories)

Return the output strictly in the following JSON format:

{
  "surname": "",
  "first_name": "",
  "date_of_birth": "",
  "place_of_birth": "",
  "date_of_issue": "",
  "date_of_expiry": "",
  "issuing_authority": "",
  "driver_number": "",
  "signature": "",
  "address": {
    "line_1": "",
    "city": "",
    "postcode": ""
  },
  "entitlements": []
}

Do not include any additional explanation or text—only return the filled JSON object.
"""
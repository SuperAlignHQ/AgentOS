def generate_document_type_prompt(total_list_of_documents):
    """
    total_list_of_documents: list of dicts containing 'document_category' and 'document_type'
    Returns a string prompt for LLM with dynamic examples
    """
    # Build canonical categories from total_list_of_documents
    canonical = {}
    for doc in total_list_of_documents:
        cat = doc[0] or "unknown"
        typ = doc[1] or "other"
        cat, typ = cat.strip().lower(), typ.strip().lower()
        canonical.setdefault(cat, set()).add(typ)
    
    # Convert sets to lists for JSON formatting
    canonical_json = {k: list(v) for k, v in canonical.items()}

    # Pick up to 3 examples per category
    examples = []
    for cat, types in canonical_json.items():
        for i, typ in enumerate(types):
            if i >= 3:  # limit examples per category
                break
            examples.append(f"Example {len(examples)+1}:\nInput: {typ} document\nOutput:\n{{\"document_category\": \"{cat}\",\"document_type\": \"{typ}\"}}")

    # Add a generic unknown example
    examples.append(f"Example {len(examples)+1}:\nInput: irrelevant or unclear\nOutput:\n{{\"document_category\": \"unknown\",\"document_type\": \"unknown\"}}")

    # Build full prompt
    prompt = f"""
Document Type Identification Agent Prompt
You are a document classification assistant.

You will be given one or more images of a document. Analyze carefully and output the most appropriate
document_category and document_type.

Canonical categories and example types:

{canonical_json}

Examples:
{chr(10).join(examples)}

Instructions:
- Always choose from canonical values if possible.
- If unsure, use "unknown".
- Respond with a single JSON object only, no extra commentary.
"""
    return prompt

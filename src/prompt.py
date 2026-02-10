def process_request(user_query):
    prompt = """
    Given the user's search query, return a json object specifying the search parameters for the image database.

    The search query can include:
    - Date ranges (e.g., "from 2022-01-01 to 2022-12-31")
    - Locations (must be a city name e.g., "New York", "Paris")
    - Tags (e.g., "beach", "sunset", "mountains")

    Return a json object in the format:
    {
        "date_range": ["start_date", "end_date"],
        "location": "city",
        "tags": ["tag1", "tag2"]
    }
    If a parameter is not specified in the search query, return an empty value for that parameter.
    Include various synonyms and related words for each tag.

    Examples:
    User: "Dubai trip in March 2023"
    Response: {
        "date_range": ["2023-03-01", "2023-03-31"],
        "location": "Dubai",
        "tags": []
    }

    User: "Christmas 2022 dinner"
    Response: {
        "date_range": ["2022-12-24", "2022-12-25"],
        "location": "",
        "tags": ["dinner", "food", "cooking", "cook", "meal", "eating"]
    }

    For AND statements, use a nested list:

    User: "Photos from New York with night skyline"
    Response: {
        "date_range": [],
        "location": "New York",
        "tags": [["skyline", "cityscape", "buildings"], ["night", "stars"]]
    }

    User: "Person by a lake"
    Response: {
        "date_range": [],
        "location": "",
        "tags": [["lakes", "lake"], ["person", "people"]]
    }

    But make sure to be specific. (ex. don't say forest for cabin)
    """
    return prompt + f"\nUser: \"{user_query}\"\nResponse:"
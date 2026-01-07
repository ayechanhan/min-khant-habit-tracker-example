def check_habit_exists(habits, name):
    """Check if a habit exists by name.

    Args:
        habits (list): List of habit dictionaries.
        name (str): Name of the habit to check.
    """
    return any(habit for habit in habits if habit["name"] == name)

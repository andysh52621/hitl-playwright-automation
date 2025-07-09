import inspect


def get_method_name(remove_prefix: str = "test_") -> str:
    """
    Returns the current method name in readable 'Title Case' format.

    Example:
    test_create_batch_tasks --> 'Create Batch Tasks'
    """
    name = inspect.currentframe().f_back.f_code.co_name
    if remove_prefix and name.startswith(remove_prefix):
        name = name[len(remove_prefix):]
    return name.replace("_", " ").title()

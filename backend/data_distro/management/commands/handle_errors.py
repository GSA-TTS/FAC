"""Functions that the public data loader uses to handle errors"""
import logging

logger = logging.getLogger(__name__)


def handle_exceptions(table, file_path, instance_dict, error_trace, exceptions_list):
    """Add detailed explanations to the logs and keep track of each type of error"""
    logger.warn(
        f"""
        ---------------------PROBLEM---------------------
        {table}, {file_path}
        ----
        {instance_dict}
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        {error_trace}
        -------------------------------------------------
        """
    )
    problem_text = f"Error loading {file_path}: \n \
        {error_trace}"

    if problem_text not in exceptions_list:
        exceptions_list.append(problem_text)

    return exceptions_list


def log_results(exceptions_list):
    """This is helpful for debugging"""
    exceptions_count = len(exceptions_list)
    if exceptions_count > 0:
        message = """###############################

            """
        for err in exceptions_list:
            message += f"""
            {err}
            """

        message += f"""###############################
            {exceptions_count} errors:
            ###############################"""

        logger.warning(message)
    else:
        logger.info("Successful upload")

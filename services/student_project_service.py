from models.data_manager import DataManager


def get_projects(reference_id):

    projects = DataManager.get(
        "projects"
    )

    if projects is None or projects.empty:
        return projects

    if "StudentID" not in projects.columns:
        return projects.iloc[0:0]

    return projects[
        projects["StudentID"].astype(str)
        == str(reference_id)
    ]
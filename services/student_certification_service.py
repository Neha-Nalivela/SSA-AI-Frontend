from models.data_manager import DataManager


def get_certifications(reference_id):

    certifications = DataManager.get(
        "certifications"
    )

    if certifications is None or certifications.empty:
        return certifications

    if "StudentID" not in certifications.columns:
        return certifications.iloc[0:0]

    return certifications[
        certifications["StudentID"].astype(str)
        == str(reference_id)
    ]
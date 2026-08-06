from services.excel_service import get_users

def login(email, password):

    users = get_users()

    print(users.head())          # Debug
    print(email, password)       # Debug

    user = users[
        (users["Email"] == email) &
        (users["Password"] == password) &
        (users["Status"] == "Active")
    ]

    print(user)                  # Debug

    if user.empty:
        return None

    return user.iloc[0]
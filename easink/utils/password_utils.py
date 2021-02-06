def password_check(passwd):
    if len(passwd) < 6:
        return "Le mot de passe doit contenir au moins 6 caractères."

    if len(passwd) > 20:
        return "Le mot de passe doit faire au maximum 20 caractères"

    if not any(char.isdigit() for char in passwd):
        return "Le mot de passe doit contenir au moins un chiffre."

    if not any(char.isupper() for char in passwd):
        return "Le mot de passe doit contenir au moins une majuscule."

    return None
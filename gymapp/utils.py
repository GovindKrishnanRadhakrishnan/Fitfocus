from decimal import Decimal, InvalidOperation


def calculate_bmi(weight_kg, height_cm):
    """BMI = weight (kg) / (height in metres)^2. Height is stored in centimetres."""
    try:
        weight = Decimal(str(weight_kg))
        height = Decimal(str(height_cm))
    except (InvalidOperation, TypeError, ValueError):
        return None

    if weight <= 0 or height <= 0:
        return None

    height_m = height / Decimal('100')
    bmi = weight / (height_m ** 2)
    return float(bmi.quantize(Decimal('0.1')))


def bmi_category(bmi):
    if bmi is None:
        return 'Unavailable'
    if bmi < 18.5:
        return 'Underweight'
    if bmi < 25:
        return 'Normal'
    if bmi < 30:
        return 'Overweight'
    return 'Obese'


def dashboard_url_for(user):
    if not getattr(user, 'is_authenticated', False):
        return 'login'
    if user.role == user.Role.ADMIN:
        return 'admin_dashboard'
    if user.role == user.Role.TRAINER:
        return 'trainer_dashboard'
    if user.role == user.Role.MEMBER:
        return 'member_dashboard'
    return 'login'

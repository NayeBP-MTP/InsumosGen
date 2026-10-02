"""
Helper script to generate realistic Mexican names and RFCs
"""
import random
from datetime import datetime, timedelta
import unicodedata

FIRST_NAMES_MALE = [
    "Juan", "José", "Carlos", "Luis", "Miguel", "Pedro", "Jorge", "Francisco",
    "Antonio", "Alejandro", "Fernando", "Ricardo", "Roberto", "Manuel", "Javier",
    "Raúl", "Sergio", "Alberto", "Eduardo", "Arturo", "Héctor", "Óscar", "Andrés"
]

FIRST_NAMES_FEMALE = [
    "María", "Ana", "Carmen", "Laura", "Rosa", "Patricia", "Guadalupe", "Lucía",
    "Elena", "Sofía", "Isabel", "Gabriela", "Claudia", "Beatriz", "Adriana",
    "Mónica", "Verónica", "Diana", "Sandra", "Silvia", "Martha", "Teresa"
]

PATERNAL_SURNAMES = [
    "García", "Rodríguez", "Martínez", "Hernández", "López", "González", "Pérez",
    "Sánchez", "Ramírez", "Torres", "Flores", "Rivera", "Gómez", "Díaz", "Cruz",
    "Morales", "Reyes", "Jiménez", "Gutiérrez", "Ruiz", "Mendoza", "Castillo",
    "Ortiz", "Vargas", "Romero", "Álvarez", "Medina", "Ramos", "Vega", "Aguilar"
]

MATERNAL_SURNAMES = [
    "Fernández", "Moreno", "Vázquez", "Castro", "Delgado", "Rojas", "Herrera",
    "Domínguez", "Guerrero", "Méndez", "Campos", "Cortés", "Navarro", "Salazar",
    "Contreras", "Estrada", "Figueroa", "Sandoval", "Ríos", "Cabrera", "Maldonado",
    "Pacheco", "León", "Peña", "Soto", "Acosta", "Valdez", "Lara", "Cervantes"
]

HOMOCLAVE_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def remove_accents(text):
    """Remove accents from Spanish characters"""
    nfd = unicodedata.normalize('NFD', text)
    return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')


def generate_name(gender=None):
    """
    Generate a random Mexican name
    
    Args:
        gender: 'M' for male, 'F' for female, None for random
    
    Returns:
        dict with 'full_name', 'first_name', 'paternal', 'maternal'
    """
    if gender is None:
        gender = random.choice(['M', 'F'])
    
    first_name = random.choice(FIRST_NAMES_MALE if gender == 'M' else FIRST_NAMES_FEMALE)
    paternal = random.choice(PATERNAL_SURNAMES)
    maternal = random.choice(MATERNAL_SURNAMES)
    
    full_name = f"{first_name} {paternal} {maternal}"
    
    return {
        'full_name': full_name,
        'first_name': first_name,
        'paternal': paternal,
        'maternal': maternal,
        'gender': gender
    }


def generate_email(name_dict):
    """
    Generate email from name dictionary
    
    Format: [firstname].[lastname]@pruebasprovident.mx
    """
    first = remove_accents(name_dict['first_name']).lower()
    last = remove_accents(name_dict['paternal']).lower()
    
    return f"{first}.{last}@pruebasprovident.mx"


def generate_rfc(name_dict, birth_date=None):
    """
    Generate RFC (Registro Federal de Contribuyentes)
    
    Format: [4 letters][6 digits YYMMDD][3 char homoclave]
    
    Rules:
    1. First letter of paternal surname
    2. First vowel (after first letter) of paternal surname
    3. First letter of maternal surname
    4. First letter of first name
    5. Birth date YYMMDD
    6. Random 3-char homoclave
    """
    if birth_date is None:
        # Generate random birth date between 1970 and 2000
        start_date = datetime(1970, 1, 1)
        end_date = datetime(2000, 12, 31)
        days_between = (end_date - start_date).days
        random_days = random.randint(0, days_between)
        birth_date = start_date + timedelta(days=random_days)
    
    # Remove accents for RFC
    paternal = remove_accents(name_dict['paternal']).upper()
    maternal = remove_accents(name_dict['maternal']).upper()
    first_name = remove_accents(name_dict['first_name']).upper()
    
    # First letter of paternal surname
    letter1 = paternal[0]
    
    # First vowel after first letter of paternal surname
    vowels = 'AEIOU'
    letter2 = next((char for char in paternal[1:] if char in vowels), 'X')
    
    # First letter of maternal surname
    letter3 = maternal[0]
    
    # First letter of first name
    letter4 = first_name[0]
    
    # Birth date YYMMDD
    date_part = birth_date.strftime('%y%m%d')
    
    # Random homoclave (3 characters)
    homoclave = ''.join(random.choices(HOMOCLAVE_CHARS, k=3))
    
    rfc = f"{letter1}{letter2}{letter3}{letter4}{date_part}{homoclave}"
    
    return rfc


def generate_representative_id(branch_number, existing_ids=None):
    """
    Generate a unique Representative_Id
    
    Format: [BBBB][000][SSSSSS] (13 digits)
    - BBBB: 4-digit branch number
    - 000: Always three zeros
    - SSSSSS: Random 6-digit suffix
    
    Args:
        branch_number: 4-digit branch number (e.g., 2075)
        existing_ids: Set of already used IDs to avoid duplicates
    
    Returns:
        13-digit Representative_Id as integer
    """
    if existing_ids is None:
        existing_ids = set()
    
    while True:
        # Generate random 6-digit suffix
        suffix = random.randint(1, 999999)
        rep_id = int(f"{branch_number}000{suffix:06d}")
        
        if rep_id not in existing_ids:
            existing_ids.add(rep_id)
            return rep_id


def generate_representatives(branch_number, count=1):
    """
    Generate multiple representatives with all required data
    
    Args:
        branch_number: 4-digit branch number
        count: Number of representatives to generate
    
    Returns:
        List of dictionaries with representative data
    """
    representatives = []
    existing_ids = set()
    
    for _ in range(count):
        name_data = generate_name()
        rep_id = generate_representative_id(branch_number, existing_ids)
        email = generate_email(name_data)
        rfc = generate_rfc(name_data)
        
        rep = {
            'representative_id': rep_id,
            'display_name': name_data['full_name'],
            'email': email,
            'rfc': rfc,
            'phone': '2481266346',
            'tipo_representante': 2,
            'maintained_by_db_id': branch_number,
            'gender': name_data['gender']
        }
        
        representatives.append(rep)
    
    return representatives


if __name__ == "__main__":
    # Example usage
    print("Generating 3 representatives for Izcalli (2075):\n")
    
    reps = generate_representatives(2075, 3)
    
    for i, rep in enumerate(reps, 1):
        print(f"Representative {i}:")
        print(f"  ID: {rep['representative_id']}")
        print(f"  Name: {rep['display_name']}")
        print(f"  Email: {rep['email']}")
        print(f"  RFC: {rep['rfc']}")
        print(f"  Phone: {rep['phone']}")
        print()

import random
import re
import unicodedata
from dataclasses import dataclass
from typing import Optional

from services.db import SqlServerRepository
from utils.agency_id_allocator import AgencyIdAllocator, AgencySectionAllocator
from utils.mexican_names import MexicanNames



def _sin_acentos(texto: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn"
    )


@dataclass
class PersonaEstructura:
    """Datos de una persona (estrella, DM o AM) dentro de AgencyStructure."""
    representative_id: int
    nombre_completo: str
    email: str
    telefono: str
    rfc: str
    tipo_representante: int  # 1=DM, 2=Estrellas, 3=AM (ver representative-types.md)


class ChallengerRepository(SqlServerRepository):
    """
    Acceso a Challenger_uat para el flujo "Nueva estructura de agencia":
    AgencyStructure, tblRepresentative_Table_AWS, P_ESTRELLAS_MENSUAL_CATEGORIAS.
    Ver config/Context/NUEVA_ESTRUCTURA_AGENCIA.md para el diseño completo.
    La conexión (host Challenger) la resuelve SqlServerRepository desde el almacén de credenciales.
    """

    def __init__(self):
        super().__init__("Challenger_uat")

    # ---- Consultas en vivo para los consecutivos de DM/AM ----

    def get_next_dm_number(self, dm_prefix: str) -> int:
        """
        `dm_prefix` es el texto que antecede al número en el código de DM de esa
        sucursal (ej. "IzcalliDM", "TijuanaBRM" — cada sucursal respeta su propio
        formato histórico). Busca el máximo número ya usado con ese prefijo en
        AgencyStructure.Dm y devuelve el siguiente.
        """
        with self._get_connection() as conn:
            filas = conn.execute(
                "SELECT [Dm] FROM [dbo].[AgencyStructure] WHERE [Dm] LIKE ?",
                (f"{dm_prefix}%",),
            ).fetchall()

        maximo = 0
        for (dm,) in filas:
            match = re.match(r"^(\d+)", dm[len(dm_prefix):])
            if match:
                maximo = max(maximo, int(match.group(1)))
        return maximo + 1

    def get_next_am_number(self, sucursal_nombre: str) -> int:
        """
        Busca el máximo número en los textos "AM<número> <sucursal>" existentes en
        AgencyStructure.Am para esa sucursal y devuelve el siguiente. Ignora
        formatos no numéricos (ej. "AM-BL-5700-Tijuana").
        """
        with self._get_connection() as conn:
            filas = conn.execute(
                "SELECT [Am] FROM [dbo].[AgencyStructure] WHERE [Am] LIKE ?",
                (f"%{sucursal_nombre}%",),
            ).fetchall()

        maximo = 0
        for (am,) in filas:
            if not am:
                continue
            match = re.match(r"^AM(\d+)", am.strip(), re.IGNORECASE)
            if match:
                maximo = max(maximo, int(match.group(1)))
        return maximo + 1

    def representative_id_exists(self, representative_id: int) -> bool:
        with self._get_connection() as conn:
            fila = conn.execute(
                "SELECT 1 FROM [dbo].[tblRepresentative_Table_AWS] WHERE [Representative_Id] = ?",
                (representative_id,),
            ).fetchone()
        return fila is not None

    def get_dm_am_combos(self, branch: int) -> list:
        """
        Combos (DM, AM) ya existentes para esa sucursal, para ofrecerlos como
        "reutilizar" en vez de crear un DM/AM nuevo. Uno por cada (Dm, Am) distinto
        encontrado en AgencyStructure para Agency_Id que empiezan con `branch`.
        """
        with self._get_connection() as conn:
            filas = conn.execute(
                """SELECT DISTINCT [Dm], [DmFocusId], [DmName], [Section], [Am], [AMFocusId], [AMName]
                   FROM [dbo].[AgencyStructure]
                   WHERE [AgencyId] LIKE ?""",
                (f"{branch}%",),
            ).fetchall()

        return [
            {
                "dm_code": dm, "dm_id": int(dm_focus_id), "dm_name": dm_name,
                "section": section,
                "am_text": am, "am_id": int(am_focus_id), "am_name": am_name,
            }
            for dm, dm_focus_id, dm_name, section, am, am_focus_id, am_name in filas
            if dm and am and dm_focus_id and am_focus_id
        ]

    # ---- Inserts ----

    def insert_agency_structure(
        self, agency_id: int, star_id: int, star_name: str,
        dm_code: str, dm_id: int, dm_name: str, section: str,
        am_text: str, am_id: int, am_name: str,
    ) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO [dbo].[AgencyStructure] VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (agency_id, star_id, star_name, dm_code, dm_id, dm_name, section, am_text, am_id, am_name),
            )
            conn.commit()

    def insert_representative(self, persona: PersonaEstructura, maintained_by_db_id: int) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO [dbo].[tblRepresentative_Table_AWS]
                   ([Representative_Id], [Email_Address], [Display_Name], [Mobile_Tel_Num],
                    [tipo_Representante], [Maintained_By_Db_Id], [RFC])
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (persona.representative_id, persona.email, persona.nombre_completo,
                 persona.telefono, persona.tipo_representante, maintained_by_db_id, persona.rfc),
            )
            conn.commit()

    def insert_monthly_category(
        self, representative_name: str, branch_location: str, agency_id: int,
        representative_id: int, dm_letter: str, month_calc: str, category: str,
        payment_month: str, avg_collected_cust: float, sales_volume: int,
        net_increase: int, avg_payment_coll: float, gds_category: str,
    ) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO [dbo].[P_ESTRELLAS_MENSUAL_CATEGORIAS]
                   ([Representative_name],[Branch],[Agency_Id],[Representative_Id],[DM_Letter],
                    [Month_Calc],[Category],[Payment_Month],[Avg_Collected_Cust],[Sales_Volume],
                    [NetIncrease],[Avg_payment_coll],[GdsCategory])
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (representative_name, branch_location, agency_id, representative_id, dm_letter,
                 month_calc, category, payment_month, avg_collected_cust, sales_volume,
                 net_increase, avg_payment_coll, gds_category),
            )
            conn.commit()

    def delete_agency_structure(self, agency_id: int) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM [dbo].[P_ESTRELLAS_MENSUAL_CATEGORIAS] WHERE [Agency_Id] = ?",
                (agency_id,),
            )
            cursor.execute(
                "DELETE FROM [dbo].[AgencyStructure] WHERE [AgencyId] = ?", (agency_id,)
            )
            conn.commit()

    def delete_representative(self, representative_id: int) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM [dbo].[tblRepresentative_Table_AWS] WHERE [Representative_Id] = ?",
                (representative_id,),
            )
            conn.commit()


class BotDbAgencyRepository(SqlServerRepository):
    """
    Acceso a botDB para el flujo "Nueva estructura de agencia":
    Agency_Representative_AWS y tblRepresentative_Table_AWS. Usa el host Pesos_Offer
    (PESOS_OFFER del almacén de credenciales), igual que services/offer_repository.py.
    """

    def __init__(self):
        super().__init__("botDB")

    def insert_agency_representative(self, agency_id: int, representative_id: int, branch: int) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO [dbo].[Agency_Representative_AWS] VALUES (?, ?, ?)",
                (agency_id, representative_id, branch),
            )
            conn.commit()

    def insert_representative(self, persona: PersonaEstructura, maintained_by_db_id: int) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO [dbo].[tblRepresentative_Table_AWS]
                   ([Representative_Id], [Email_Address], [Display_Name], [Mobile_Tel_Num],
                    [tipo_Representante], [Maintained_By_Db_Id], [RFC])
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (persona.representative_id, persona.email, persona.nombre_completo,
                 persona.telefono, persona.tipo_representante, maintained_by_db_id, persona.rfc),
            )
            conn.commit()

    def delete_agency_representative(self, agency_id: int) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM [dbo].[Agency_Representative_AWS] WHERE [Agency_Id] = ?", (agency_id,)
            )
            conn.commit()

    def delete_representative(self, representative_id: int) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM [dbo].[tblRepresentative_Table_AWS] WHERE [Representative_Id] = ?",
                (representative_id,),
            )
            conn.commit()


def generar_persona(branch: int, tipo_representante: int, challenger: ChallengerRepository) -> PersonaEstructura:
    """
    Genera una persona (estrella/DM/AM) con nombre y RFC realistas (ficticios, vía
    utils/mexican_names.py) y un Representative_Id único (esquema legado
    BBBB+000+sufijo aleatorio), verificado contra Challenger_uat para evitar
    colisiones con datos ya existentes.
    """
    datos = MexicanNames.generar()
    fecha_nacimiento = f"{random.randint(1, 28):02d}/{random.randint(1, 12):02d}/{random.randint(1970, 2000)}"
    rfc = MexicanNames.rfc(datos, fecha_nacimiento)

    for _ in range(50):
        sufijo = random.randint(1, 999999)
        representative_id = int(f"{branch:04d}000{sufijo:06d}")
        if not challenger.representative_id_exists(representative_id):
            break
    else:
        raise RuntimeError(f"No se pudo generar un Representative_Id único para branch={branch}")

    primer_nombre = _sin_acentos(datos["nombre"].split()[0]).lower()
    primer_apellido = _sin_acentos(datos["apellido_paterno"]).lower()
    email = f"{primer_nombre}.{primer_apellido}@pruebasprovident.mx"

    return PersonaEstructura(
        representative_id=representative_id,
        nombre_completo=datos["nombre_completo"].title(),
        email=email,
        telefono="2481266346",
        rfc=rfc,
        tipo_representante=tipo_representante,
    )


@dataclass
class DmInfo:
    dm_code: str
    dm_id: int
    dm_name: str
    section: str


@dataclass
class AmInfo:
    am_text: str
    am_id: int
    am_name: str


def generar_dm_nuevo(sucursal: dict, challenger: ChallengerRepository):
    """
    Calcula (sin insertar) los datos de un DM nuevo para la sucursal: número
    siguiente al máximo real en Challenger_uat (ver
    ChallengerRepository.get_next_dm_number), letra = siguiente sección libre de la
    herramienta (ver utils/agency_id_allocator.py), nombre/RFC/Representative_Id
    autogenerados (verificados únicos contra Challenger_uat, pero NO insertados).

    Devuelve (DmInfo, PersonaEstructura) — usa insertar_persona() para darlo de
    alta en Challenger_uat y botDB antes de referenciarlo en una AgencyStructure.
    """
    numero = challenger.get_next_dm_number(sucursal["dm_prefix"])
    seccion = AgencySectionAllocator.get_next_section_letter(sucursal["branch"])
    dm_code = f"{sucursal['dm_prefix']}{numero}{seccion}"

    persona = generar_persona(sucursal["branch"], tipo_representante=1, challenger=challenger)
    dm_info = DmInfo(dm_code=dm_code, dm_id=persona.representative_id, dm_name=persona.nombre_completo, section=seccion)
    return dm_info, persona


def generar_am_nuevo(sucursal: dict, challenger: ChallengerRepository):
    """
    Calcula (sin insertar) los datos de un AM nuevo para la sucursal: número
    siguiente al máximo real en Challenger_uat (ver
    ChallengerRepository.get_next_am_number), nombre/RFC/Representative_Id
    autogenerados (verificados únicos, pero NO insertados).

    Devuelve (AmInfo, PersonaEstructura) — usa insertar_persona() para darlo de
    alta en Challenger_uat y botDB antes de referenciarlo en una AgencyStructure.
    """
    numero = challenger.get_next_am_number(sucursal["am_match"])
    am_text = f"AM{numero} {sucursal['nombre']}"

    persona = generar_persona(sucursal["branch"], tipo_representante=3, challenger=challenger)
    am_info = AmInfo(am_text=am_text, am_id=persona.representative_id, am_name=persona.nombre_completo)
    return am_info, persona


def insertar_persona(
    persona: PersonaEstructura, maintained_by_db_id: int,
    challenger: ChallengerRepository, botdb: BotDbAgencyRepository,
) -> None:
    """Inserta un DM/AM (o cualquier persona ya generada) en ambas bases."""
    challenger.insert_representative(persona, maintained_by_db_id=maintained_by_db_id)
    botdb.insert_representative(persona, maintained_by_db_id=maintained_by_db_id)


MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]
CATEGORIAS = ["MINI", "GRAN", "MEGA", "ULTRA"]


def crear_agencia(
    sucursal: dict, dm_info: DmInfo, am_info: AmInfo,
    challenger: ChallengerRepository, botdb: BotDbAgencyRepository,
    hoy=None,
) -> dict:
    """
    Da de alta una agencia (estrella) nueva bajo el DM/AM dados (reutilizados o
    recién creados por el caller) en Challenger_uat y botDB. No crea el DM/AM: eso
    lo hace `generar_dm_nuevo`/`generar_am_nuevo` una sola vez por lote, antes de
    llamar aquí por cada estrella del lote.
    """
    import datetime
    hoy = hoy or datetime.date.today()

    agency_id = AgencyIdAllocator.get_unique_agency_id(sucursal["branch"], hoy)
    estrella = generar_persona(sucursal["branch"], tipo_representante=2, challenger=challenger)

    challenger.insert_agency_structure(
        agency_id=agency_id, star_id=estrella.representative_id, star_name=estrella.nombre_completo,
        dm_code=dm_info.dm_code, dm_id=dm_info.dm_id, dm_name=dm_info.dm_name, section=dm_info.section,
        am_text=am_info.am_text, am_id=am_info.am_id, am_name=am_info.am_name,
    )
    challenger.insert_representative(estrella, maintained_by_db_id=sucursal["branch"])
    challenger.insert_monthly_category(
        representative_name=estrella.nombre_completo,
        branch_location=sucursal["ubicacion"],
        agency_id=agency_id,
        representative_id=estrella.representative_id,
        dm_letter=dm_info.section,
        month_calc=MESES[hoy.month - 1],
        category=random.choice(CATEGORIAS),
        payment_month=MESES[hoy.month % 12],
        avg_collected_cust=round(random.uniform(0.70, 0.95), 4),
        sales_volume=random.randint(10, 30),
        net_increase=random.randint(1, 4),
        avg_payment_coll=round(random.uniform(0.05, 0.12), 2),
        gds_category=random.choice(CATEGORIAS),
    )

    botdb.insert_agency_representative(agency_id, estrella.representative_id, sucursal["branch"])
    botdb.insert_representative(estrella, maintained_by_db_id=sucursal["branch"])

    return {
        "agency_id": agency_id,
        "star_id": estrella.representative_id,
        "star_name": estrella.nombre_completo,
        "star_email": estrella.email,
        "dm_code": dm_info.dm_code,
        "am_text": am_info.am_text,
        "section": dm_info.section,
    }


def eliminar_agencia(
    agency_id: int, star_id: int, challenger: ChallengerRepository, botdb: BotDbAgencyRepository,
) -> None:
    """Revierte lo insertado por crear_agencia() para una estrella (no toca DM/AM)."""
    challenger.delete_agency_structure(agency_id)
    challenger.delete_representative(star_id)
    botdb.delete_agency_representative(agency_id)
    botdb.delete_representative(star_id)


def eliminar_dm_am(
    dm_id: Optional[int], am_id: Optional[int],
    challenger: ChallengerRepository, botdb: BotDbAgencyRepository,
) -> None:
    """Revierte lo insertado por generar_dm_nuevo()/generar_am_nuevo(). Usar solo si
    todo el lote se está revirtiendo (un DM/AM puede quedar referenciado por varias
    agencias del mismo lote)."""
    for rep_id in (dm_id, am_id):
        if rep_id:
            challenger.delete_representative(rep_id)
            botdb.delete_representative(rep_id)


if __name__ == "__main__":
    repo = ChallengerRepository()
    print("Conexión a Challenger_uat:", "OK" if repo.test_connection() else "FALLÓ")
    print("Siguiente número DM Izcalli:", repo.get_next_dm_number("IzcalliDM"))
    print("Siguiente número AM Izcalli:", repo.get_next_am_number("Izcalli"))

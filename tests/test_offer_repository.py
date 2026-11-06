"""Pruebas unitarias (sin red ni BD) de OfferRepository sobre la clase base SqlServerRepository."""
from services.offer_repository import OfferData, OfferRepository


def _oferta() -> OfferData:
    return OfferData(
        idOferta=26110001, nombreCliente="JUAN PEREZ LOPEZ", porcentajeCalidadCliente=100.0,
        montoOferta=9900.0, tipoDeOferta="AD", agenciaCliente=2075000000335,
        seccionCliente="A", amOferta="AM1", branchOferta=335, descOferta="AGREGAR",
        semana=202645, Customer_Id=2075000000001, Agreement_Num=1,
        FechaNacimiento="1990-01-01 00:00:00.000", RFC="PELJ900101ABC",
    )


def test_usa_la_base_botdb_en_pesos_offer():
    repo = OfferRepository()
    assert (repo.base, repo.host) == ("botDB", "PESOS_OFFER")


def test_insert_offer_en_dry_run_registra_el_insert_sin_conectar():
    repo = OfferRepository(dry_run=True)
    oferta = _oferta()
    repo.insert_offer(oferta)

    (sql, params), = repo.dry_run_log
    assert sql.startswith("INSERT INTO [dbo].[Ofertas] (")
    assert sql.count("?") == len(params)
    assert params[0] == oferta.idOferta
    assert "[idOferta]" in sql and "[FechaActualizacion]" in sql


def test_delete_offer_en_dry_run():
    repo = OfferRepository(dry_run=True)
    repo.delete_offer(26110001)
    assert repo.dry_run_log == [("DELETE FROM [dbo].[Ofertas] WHERE [idOferta] = ?", (26110001,))]

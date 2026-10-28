"""Tablas transformadas, exportación y reportes con indicadores (HU-05 y HU-06)."""

import io
from decimal import Decimal

import pandas as pd
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.esquemas import ReporteEntrada
from app.modelos import Indicador, RegistroVenta, Reporte, TablaTransformada, Usuario
from app.seguridad import es_administrador
from app.servicios import auditoria


def tabla_de(bd: Session, usuario: Usuario, tabla_id: int) -> TablaTransformada:
    consulta = select(TablaTransformada).where(TablaTransformada.id == tabla_id)
    if not es_administrador(usuario):  # el administrador tiene acceso global
        consulta = consulta.where(TablaTransformada.usuario_id == usuario.id)
    tabla = bd.scalar(consulta)
    if tabla is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tabla no encontrada.")
    return tabla


def listar(bd: Session, usuario: Usuario) -> list:
    return list(
        bd.scalars(
            select(TablaTransformada)
            .where(TablaTransformada.usuario_id == usuario.id)
            .order_by(TablaTransformada.creada_en.desc())
        )
    )


def eliminar(bd: Session, usuario: Usuario, tabla_id: int) -> None:
    tabla = tabla_de(bd, usuario, tabla_id)
    if tabla.usuario_id != usuario.id:  # solo pasa cuando lo hace el administrador
        auditoria.registrar(bd, "admin_elimina_tabla", usuario.id, f"tabla {tabla.id}: {tabla.nombre}")
    for rep in bd.scalars(select(Reporte).where(Reporte.tabla_id == tabla.id)):
        bd.delete(rep)
    bd.flush()  # los reportes (e indicadores) se borran antes que la tabla por la llave foránea (D-09)
    bd.delete(tabla)
    bd.commit()


def exportar_excel(bd: Session, usuario: Usuario, tabla_id: int) -> tuple[str, bytes]:
    tabla = tabla_de(bd, usuario, tabla_id)
    filas = [
        {"fecha": r.fecha, "valor": float(r.valor), **r.datos}
        for r in bd.scalars(
            select(RegistroVenta).where(RegistroVenta.tabla_id == tabla.id).order_by(RegistroVenta.fecha)
        )
    ]
    salida = io.BytesIO()
    pd.DataFrame(filas).to_excel(salida, index=False, sheet_name="datos")
    return f"{tabla.nombre}.xlsx", salida.getvalue()


FORMULAS = {
    "ventas_totales": "SUM(valor)",
    "promedio_por_periodo": "SUM(valor) / número de periodos",
    "crecimiento_ultimo_periodo": "(último − penúltimo) / penúltimo × 100",
}


def _serie(bd: Session, tabla: TablaTransformada, datos: ReporteEntrada) -> list:
    """Suma las ventas por día, mes o año dentro del rango pedido."""
    unidad = {"dia": "day", "mes": "month", "anio": "year"}[datos.agrupacion]
    periodo = func.date_trunc(unidad, RegistroVenta.fecha).label("periodo")
    consulta = select(periodo, func.sum(RegistroVenta.valor).label("total")).where(RegistroVenta.tabla_id == tabla.id)
    if datos.fecha_inicio:
        consulta = consulta.where(RegistroVenta.fecha >= datos.fecha_inicio)
    if datos.fecha_fin:
        consulta = consulta.where(RegistroVenta.fecha <= datos.fecha_fin)
    formato = {"dia": "%Y-%m-%d", "mes": "%Y-%m", "anio": "%Y"}[datos.agrupacion]
    return [
        {"periodo": p.strftime(formato), "total": float(t)}
        for p, t in bd.execute(consulta.group_by(periodo).order_by(periodo)).all()
    ]


def _indicadores(totales: list) -> dict:
    total = sum(totales)
    crecimiento = None
    if len(totales) >= 2 and totales[-2]:
        crecimiento = (totales[-1] - totales[-2]) / totales[-2] * 100
    return {
        "ventas_totales": total,
        "promedio_por_periodo": total / len(totales) if totales else 0,
        "crecimiento_ultimo_periodo": crecimiento,
        "periodos": len(totales),
    }


def generar(bd: Session, usuario: Usuario, datos: ReporteEntrada) -> dict:
    tabla = tabla_de(bd, usuario, datos.tabla_id)
    if datos.fecha_inicio and datos.fecha_fin and datos.fecha_fin < datos.fecha_inicio:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "La fecha final no puede ser menor que la inicial.")
    serie = _serie(bd, tabla, datos)
    indicadores = _indicadores([s["total"] for s in serie])
    reporte = Reporte(
        tabla_id=tabla.id,
        usuario_id=usuario.id,
        tipo=datos.tipo,
        fecha_inicio=datos.fecha_inicio,
        fecha_fin=datos.fecha_fin,
        agrupacion=datos.agrupacion,
    )
    reporte.indicadores = [
        Indicador(nombre=k, valor=Decimal(str(round(v, 4))), formula=FORMULAS[k])
        for k, v in indicadores.items()
        if k in FORMULAS and v is not None
    ]
    bd.add(reporte)
    bd.commit()
    return {
        "id": reporte.id,
        "tipo": reporte.tipo,
        "agrupacion": reporte.agrupacion,
        "serie": serie,
        "indicadores": indicadores,
    }

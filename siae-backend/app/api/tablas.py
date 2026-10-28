"""Rutas de tablas transformadas y reportes."""
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db import obtener_sesion
from app.esquemas import ReporteEntrada, ReporteSalida, TablaSalida
from app.modelos import Usuario
from app.seguridad import usuario_actual
from app.servicios import reportes as srv

ruta = APIRouter(tags=["Tablas y reportes"])


@ruta.get("/tablas", response_model=list[TablaSalida], summary="Listar mis tablas transformadas")
def listar(usuario: Usuario = Depends(usuario_actual), bd: Session = Depends(obtener_sesion)):
    return [{"id": t.id, "nombre": t.nombre, "filas": t.filas, "columnas": t.columnas} for t in srv.listar(bd, usuario)]


@ruta.get("/tablas/{tabla_id}/excel", summary="Exportar una tabla a Excel")
def exportar(tabla_id: int, usuario: Usuario = Depends(usuario_actual), bd: Session = Depends(obtener_sesion)):
    nombre, contenido = srv.exportar_excel(bd, usuario, tabla_id)
    return Response(contenido, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": f'attachment; filename="{nombre}"'})


@ruta.delete("/tablas/{tabla_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar una tabla")
def eliminar(tabla_id: int, usuario: Usuario = Depends(usuario_actual), bd: Session = Depends(obtener_sesion)):
    srv.eliminar(bd, usuario, tabla_id)


@ruta.post("/reportes", response_model=ReporteSalida, status_code=status.HTTP_201_CREATED, summary="Generar un reporte con indicadores")
def generar(datos: ReporteEntrada, usuario: Usuario = Depends(usuario_actual), bd: Session = Depends(obtener_sesion)):
    return srv.generar(bd, usuario, datos)

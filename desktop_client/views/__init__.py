"""
Vistas modulares de pestañas para la interfaz gráfica de Hotel KeyFlow.
"""
from .tab_habitaciones import TabHabitacionesView
from .tab_usuarios import TabUsuariosView
from .tab_recepcion import TabRecepcionView
from .tab_folios import TabFoliosView
from .tab_pos import TabPOSView
from .tab_mantenimiento import TabMantenimientoView
from .tab_reportes import TabReportesView

__all__ = [
    "TabHabitacionesView",
    "TabUsuariosView",
    "TabRecepcionView",
    "TabFoliosView",
    "TabPOSView",
    "TabMantenimientoView",
    "TabReportesView",
]

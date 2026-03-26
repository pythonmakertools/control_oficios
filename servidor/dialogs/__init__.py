# servidor/dialogs/__init__.py
from .oficios_dialog import DialogoOficio
from .asignar_dialog import DialogoAsignarOficios  # ✅ Nombre correcto
from .reasignar_dialog import DialogoReasignar
from .estado_dialog import DialogoCambiarEstado
from .acuse_dialog import DialogoRegistrarAcuse
from .detalle_dialog import DialogoDetalle
from .usuario_dialog import DialogoUsuario
from .reasignar_usuario_dialog import DialogoReasignarUsuario
from .carga_dialog import DialogoCargaArchivos
from .asignar_rapido_dialog import DialogoAsignarRapido

__all__ = [
    'DialogoOficio',
    'DialogoAsignarOficios',  # ✅ Nombre correcto
    'DialogoReasignar',
    'DialogoCambiarEstado',
    'DialogoRegistrarAcuse',
    'DialogoDetalle',
    'DialogoUsuario',
    'DialogoReasignarUsuario',
    'DialogoCargaArchivos',
    'DialogoAsignarRapido'
]
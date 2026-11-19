# Yermo

Plataforma de cursos en video y escritos hecha con Django. Guía paso a paso de la base de datos y del despliegue en Render:
https://claude.ai/artifact/NZp1JPj7kMfnxH7A6jKSHb

| Carpeta | Contenido |
| --- | --- |
| `accounts/` | Usuarios, registro, login por usuario o correo |
| `courses/` | Cursos con videos y escritos, lecciones, suscripciones y avance |
| `blog/` | Blog con mensajes, fotos y cursos etiquetados |
| `surveys/` | Encuesta de satisfacción |
| `metrics/` | Panel de administradores: usuarios, flujo, eliminación de cuentas y resultados de la encuesta |
| `templates/`, `static/` | Diseño de la web |
| `config/` | Configuración de Django |

| Comando | Para qué sirve |
| --- | --- |
| `python manage.py makemigrations` y `python manage.py migrate` | Crean o actualizan las tablas |
| `python manage.py cargar_cursos_escritos` | Crea los 10 cursos escritos que trae Yermo, si faltan |
| `python manage.py cargar_cursos cursos.json` | Crea tus cursos desde un archivo como `cursos.ejemplo.json` |
| `python manage.py test` | Ejecuta las pruebas |

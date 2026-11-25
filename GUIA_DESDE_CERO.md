# OBSERVATORIO DIC · Guía desde cero hasta compartir la aplicación

**Objetivo:** buscador público de jurisprudencia del Tribunal Constitucional del Perú, con dos cuentas de investigación autorizadas a editar. El código es una **versión piloto** para desplegar; no está alojado ni conectado a tus cuentas.

## Antes de empezar

Solo necesitas un navegador, acceso a correo electrónico y tres cuentas: GitHub, Supabase y Streamlit Community Cloud. **No necesitas instalar Python en la Mac para desplegar la aplicación mediante GitHub web.** La IA es opcional y usa una cuenta de OpenAI API con facturación independiente.

### Paso 0: descarga y prepara los archivos

1. Descarga el ZIP `Observatorio_DIC_WEB_COMPARTIDO_v1.zip` y descomprímelo.
2. Comprueba que contiene `app.py`, `ingest.py`, `requirements.txt`, `sql/01_esquema_supabase.sql`, `.gitignore` y esta guía.
3. No coloques contraseñas reales dentro de ningún archivo que vayas a publicar.

### Paso 1: crea el proyecto de base de datos en Supabase

1. Abre https://supabase.com/dashboard y crea una cuenta.
2. Pulsa **New project** y asigna como nombre `Observatorio DIC TC`.
3. Elige la organización, región disponible y una contraseña de base de datos segura. Guárdala en un gestor de contraseñas. **Esa contraseña no se pega en la aplicación.**
4. Cuando se cree el proyecto, abre **SQL Editor**.
5. En tu computadora, abre `sql/01_esquema_supabase.sql`, copia todo su contenido y pégalo en el SQL Editor. Pulsa **Run**.
6. Verifica en **Table Editor** la existencia de las tablas `researchers`, `cases`, `case_notes`, `case_sources` y `case_history`.

Las políticas **Row Level Security (RLS)** del SQL impiden que el público escriba datos, que usuarios externos consulten borradores y que los investigadores modifiquen su propia lista de autorizados. El SQL impone un máximo de dos investigadores.

### Paso 2: crea exactamente los dos investigadores

1. Ve a **Authentication → Users**.
2. Usa **Add user / Create new user** (el nombre puede variar) para crear las dos cuentas con correo y contraseña temporal segura. Confirma sus emails mediante el mecanismo del panel. Si la interfaz solo ofrece **Send invitation**, sigue la invitación y verifica que cada cuenta pueda establecer una contraseña compatible con el inicio de sesión de la aplicación.
3. Copia el **UUID / User ID** de cada cuenta, no la contraseña.
4. Regresa a **SQL Editor**, crea una nueva consulta, reemplaza los dos UUID por los reales y ejecuta:

```sql
insert into public.researchers (user_id, display_name) values
  ('UUID_REAL_DEL_INVESTIGADOR_1', 'Investigador 1'),
  ('UUID_REAL_DEL_INVESTIGADOR_2', 'Investigador 2');
```

5. En **Authentication → Sign In / Providers**, busca **Allow new users to sign up** y desactívalo para impedir altas públicas. Mantén habilitado el inicio de sesión con correo y contraseña.
6. Nunca compartas las contraseñas de ambos investigadores. Cada uno debe ingresar con su propia cuenta y cambiar su contraseña desde el panel lateral de la app.

Si el SQL responde que el UUID es inválido, comprueba que has copiado el ID de usuario completo con guiones. Si el proyecto ya tiene dos miembros, la tabla rechaza un tercero.

### Paso 3: obtén las dos credenciales permitidas de Supabase

1. En Supabase abre **Project Settings → API Keys** (o **Connect**, dependiendo de la interfaz).
2. Copia `Project URL`, cuyo formato suele ser `https://xxxx.supabase.co`.
3. Copia la **Publishable key**, que comienza por `sb_publishable_`.
4. **No copies** claves `sb_secret_`, `service_role`, ni la contraseña de la base de datos. Esta aplicación no las necesita.

La publishable key por sí sola **no permite editar**. Los permisos reales dependen de las políticas RLS y de la sesión autenticada.

### Paso 4: crea el repositorio en GitHub

1. Entra a https://github.com/new y crea un repositorio llamado `observatorio-dic-tc`.
2. Selecciona visibilidad **Public** para que Streamlit pueda publicar el portal fácilmente. Que el código sea público no significa que las notas internas estén expuestas: las guarda Supabase con RLS.
3. Abre tu repositorio, pulsa **Add file → Upload files**. Arrastra los archivos descomprimidos, incluyendo la carpeta `sql`.
4. Comprueba que `app.py`, `ingest.py` y `requirements.txt` están en el **nivel principal** del repositorio, no dentro de una subcarpeta adicional.
5. Pulsa **Commit changes**. No cargues un archivo `.streamlit/secrets.toml` con credenciales. El archivo `secrets.toml.example` es solo un modelo sin datos reales.

**Importante:** no subas únicamente el ZIP a GitHub. Streamlit necesita acceder a `app.py` y `requirements.txt` como archivos independientes.

### Paso 5: publica la web en Streamlit

1. Ingresa a https://share.streamlit.io/ e inicia sesión con GitHub.
2. Selecciona **Create app → Deploy a public app from GitHub** (la redacción puede variar).
3. Escoge tu repositorio `observatorio-dic-tc`, la rama `main` y como **Main file path** escribe `app.py`.
4. Si puedes elegir versión de Python, utiliza **3.12**.
5. En **Advanced settings → Secrets**, pega lo siguiente sustituyendo ambos valores:

```toml
SUPABASE_URL = "https://TU_PROYECTO.supabase.co"
SUPABASE_PUBLISHABLE_KEY = "sb_publishable_TU_CLAVE_REAL"
```

6. Pulsa **Save** y después **Deploy**.
7. Cuando la app abra, copia la dirección que te asigne Streamlit, por ejemplo `https://tu-nombre.streamlit.app` (**ejemplo, no una dirección existente**).
8. En **App settings → Sharing**, comprueba que **Who can view this app** está configurado como **This app is public and searchable**.

### Paso 6: comprueba que la web es realmente pública

1. Abre el enlace en una ventana privada o en un teléfono sin iniciar sesión.
2. Debe aparecer **Consulta pública** y el acceso de investigadores, pero ninguna ficha privada.
3. Si no has aprobado ninguna ficha, el buscador mostrará que todavía no existen registros publicados. Eso es correcto.
4. El visitante no debe poder agregar expedientes, revisar notas ni publicar.

### Paso 7: realiza el primer registro

1. Ingresa con la cuenta del investigador 1 desde el menú lateral.
2. En **Área de investigación → Agregar expediente**, registra este documento real:
   - Expediente: `03269-2023-PA/TC`.
   - Título: `Plaguicidas e inocuidad alimentaria`.
   - Año de publicación: `2026`.
   - Fuente: `https://www.tc.gob.pe/jurisprudencia/2026/03269-2023-AA.html`.
   - Materia: `MSF / inocuidad alimentaria`.
3. Pulsa **Guardar expediente privado** y vuelve a abrir **Revisar y publicar**.
4. Opcionalmente, pulsa **Recuperar extracto**. El programa verifica el enlace oficial, `robots.txt`, respeta una espera mínima de 30 segundos entre solicitudes y conserva hasta 40.000 caracteres para análisis interno. **Ese extracto puede no ser el documento íntegro**.
5. Lee la sentencia original y redacta un resumen académico de tu autoría. No publiques el resultado automático sin verificar.
6. Selecciona `Directa` o `Indirecta`, según tu justificación; marca `Validado`, activa **Publicar** y guarda.
7. Abre una ventana privada del navegador y comprueba que aparece esa ficha, pero no las notas internas.

### Paso 8: prueba el acceso simultáneo con otra persona

1. Investigador 1: entra desde tu Mac y agrega una nota privada.
2. Investigador 2: entra desde otro dispositivo con su propia cuenta y abre el mismo expediente.
3. El investigador 2 debe ver la nota tras actualizar la vista, sin descargar ni intercambiar archivos.
4. Ambos pueden modificar la ficha; cada modificación deja una entrada en el historial de cambios. **No existe edición simultánea en tiempo real estilo Google Docs:** si ambos editan el mismo registro a la vez, la última actualización puede prevalecer. Coordinen la edición de una ficha a la vez.
5. Prueba con una tercera cuenta no autorizada: no debe ingresar al panel, incluso si tiene credenciales válidas de Supabase.

### Paso 9: importa un catálogo oficial histórico

1. Abre https://www.datosabiertos.gob.pe/dataset/expedientes-publicados-por-el-tribunal-constitucional-tc.
2. Descarga el archivo oficial CSV o Excel que esté disponible, junto con su diccionario de datos. Comprueba su fecha de actualización y alcance.
3. Dentro de la web abre **Área de investigación → Importar catálogo**.
4. Sube el archivo y asigna manualmente las columnas para expediente, título, año de publicación y URL (si existe).
5. Importa lotes de hasta **100 filas**. Puedes avanzar cambiando el número de fila inicial. El sistema ignora expedientes duplicados sin alterar fichas revisadas.
6. Todas las filas importadas son **borradores privados**. Un registro de metadatos NO significa que se haya recuperado el texto íntegro de la sentencia.
7. Las URLs sin verificar se dejan vacías. No fabriques rutas basándote exclusivamente en el código del expediente.

**Limitación de la V1:** no garantiza haber localizado **todos** los expedientes relevantes para Derecho Internacional Comercial. La clasificación de términos es exploratoria; los investigadores deben definir criterios de inclusión/exclusión y revisar falsos positivos/negativos. Para un censo sistemático en volumen alto, conviene un proceso aparte de ingesta en lotes con monitoreo y canal institucional de datos.

### Paso 10 (opcional): activa la IA

1. Registra una cuenta en https://platform.openai.com/ y consulta costos y límites de la API.
2. Crea una clave privada de API en esa plataforma.
3. En la consola de Streamlit abre **App settings → Secrets** y añade:

```toml
OPENAI_API_KEY = "sk-TU_CLAVE"
OPENAI_MODEL = "gpt-4.1-mini"
```

4. Guarda cambios y reinicia la aplicación si se requiere.
5. Inicia sesión como investigador, ve a **Asistente IA**, selecciona un expediente con texto recuperado y escribe una pregunta jurídica.
6. Verifica en la sentencia original el fundamento y la ratio decidendi. La IA no constituye fuente primaria ni garantía de exactitud.

**No agregues estas claves a GitHub ni las envíes por chat.** La consulta de IA es privada en esta versión para controlar costos y limitar el envío de contenido a servicios externos.

### Paso 11: mantenimiento y control de calidad

- Antes de publicar, exige fuente oficial, lectura humana, justificación DIC y resumen validado.
- Una vez al mes, exporta o respalda la base de datos desde Supabase según las funciones disponibles en tu plan.
- Cada nuevo expediente debe incluir su procedencia y estado de revisión.
- Los enlaces del TC pueden cambiar o dejar de estar disponibles: revisa enlaces rotos periódicamente.
- Respeta `robots.txt`; al preparar esta versión el TC indicaba `Crawl-delay: 30`.
- Cuida los datos personales contenidos en expedientes y evita almacenar información confidencial adicional.
- Cualquier cambio en el código se sube a GitHub y Streamlit puede volver a desplegar la versión actualizada.

## Comprobaciones de seguridad obligatorias

| Prueba | Resultado correcto |
|---|---|
| Visitante sin cuenta abre URL | Solo fichas publicadas |
| Visitante intenta editar | No tiene permiso de escritura |
| Usuario autenticado pero no inscrito en `researchers` | Sin acceso de investigación |
| Investigador 1 publica un expediente validado | Visible para cualquier visitante |
| Investigador 2 deja nota interna | Solo ambos investigadores la ven |
| Expediente sin URL oficial intenta publicarse | El sistema rechaza la publicación |
| Se intenta registrar un tercer investigador | La base de datos lo rechaza |

## Problemas comunes

**«La aplicación todavía no está configurada»:** falta SUPABASE_URL o SUPABASE_PUBLISHABLE_KEY en los Secrets de Streamlit.

**«No se pudo iniciar sesión»:** revisar el email, la contraseña, que el usuario esté confirmado y que su UUID esté en `researchers`.

**El panel privado está vacío:** agregar la primera ficha en `Agregar expediente`; un proyecto nuevo no contiene sentencias precargadas.

**Error RLS al grabar:** verificar que se ejecutó todo el SQL y que el usuario autenticado está en `researchers`. No desactives RLS como solución.

**No aparece una ficha en el portal público:** debe cumplir los cuatro requisitos: `Validado`, `Directa/Indirecta`, resumen suficiente y URL oficial; luego marcar `Publicar`.

**Error al extraer un PDF:** algunos archivos son imágenes escaneadas y pueden requerir OCR/revisión manual. No se intenta eludir bloqueos de acceso.

**Una persona sobrescribió a otra:** la edición no es colaborativa en tiempo real; para cada expediente asigna responsable y revisa el historial.

## Qué falta antes de considerarlo un sistema de investigación exhaustivo

1. Ejecutar pruebas de integración contra un proyecto real de Supabase; aquí no hay credenciales del usuario.
2. Validar el esquema del conjunto de Datos Abiertos, y su cobertura temporal de forma empírica.
3. Agregar un programador de ingesta controlada, monitoreo de errores y recuperación paginada para grandes volúmenes.
4. Crear índice textual global con búsqueda en fundamentos y recuperación semántica para análisis en todo el corpus.
5. Definir protocolo académico de anotación y muestreo para evaluar precisión y exhaustividad.

**Estado de entrega:** código y archivos listos para que el usuario los despliegue; el despliegue efectivo, la autenticación real y el scraping remoto **no se han probado con sus cuentas**.

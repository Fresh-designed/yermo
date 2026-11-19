"""Contenido de los cursos escritos que crea `python manage.py cargar_cursos_escritos`.

Cada curso usa el formato de `courses/loader.py`. En el texto de una lección, los párrafos
se separan con una línea en blanco, «## » abre un subtítulo, y «- » o «1. » al inicio de
una línea crean una lista.
"""

WRITTEN_COURSES = [
    {
        "titulo": "Tips de dibujo: fundamentos del trazo",
        "tipo": "escrito",
        "descripcion": "Suelta la mano, construye con formas simples y aprende a medir a ojo antes de añadir detalle.",
        "lecciones": [
            {
                "titulo": "Calienta la mano y suelta el trazo",
                "texto": """
Un trazo seguro sale del brazo, no de los dedos. Antes de dibujar, dedica cinco minutos a calentar: verás la diferencia desde la primera línea.

## Cómo calentar
- Llena media hoja con líneas rectas paralelas, cada una de un solo movimiento.
- Dibuja círculos y elipses de varios tamaños sin levantar el lápiz.
- Une dos puntos separados con una recta: ensaya el gesto en el aire y luego trázala.

Sujeta el lápiz un poco más atrás de lo habitual y mueve el hombro y el codo. Los dedos quedan para los detalles pequeños.

## Evita el trazo peludo
Muchas líneas cortas y encimadas ensucian el dibujo. Es mejor una línea larga e imperfecta que diez cortas e inseguras. Si una línea no te convence, repítela al lado en lugar de remarcarla.

## Ejercicio
Dibuja un rectángulo y llénalo con 20 elipses que toquen sus bordes.
""",
            },
            {
                "titulo": "Construye con formas simples",
                "texto": """
Cualquier objeto complejo se puede reducir a cuatro volúmenes: esfera, cubo, cilindro y cono. Si dibujas primero esas formas, resuelves la proporción y la perspectiva antes de gastar tiempo en detalles.

## El orden que funciona
1. Bloquea el objeto con formas grandes y un trazo muy suave.
2. Divide cada forma en partes medianas.
3. Añade el detalle al final, cuando lo demás ya está en su sitio.

Una taza es un cilindro con medio aro pegado. Una mano es una caja para la palma y cinco cilindros articulados. Un árbol es un cilindro con varias esferas encima.

## Dibuja a través
Traza también las líneas que no se ven, como la elipse completa de la base de un vaso. Así compruebas que el volumen tiene sentido.

## Ejercicio
Elige tres objetos de tu escritorio y dibuja cada uno usando solo los cuatro volúmenes básicos.
""",
            },
            {
                "titulo": "Mide proporciones a ojo",
                "texto": """
La mayoría de los errores de un dibujo son de proporción, no de técnica. Medir antes de detallar ahorra borrar después.

## Tres formas de medir
- El lápiz como regla: estira el brazo por completo, cierra un ojo y marca con el pulgar la altura de una parte. Compárala con las demás.
- Plomadas: imagina líneas verticales y horizontales, y observa qué puntos quedan alineados entre sí.
- Espacio negativo: dibuja la forma del hueco que hay entre los objetos. Engaña menos que la forma del objeto.

## Compara, no adivines
Busca una unidad de medida dentro del propio modelo, por ejemplo el ancho de una botella, y pregúntate cuántas veces cabe en su altura.

## Ejercicio
Dibuja una silla fijándote solo en los huecos entre las patas y el respaldo.
""",
            },
        ],
    },
    {
        "titulo": "Tips de dibujo: luz y sombra",
        "tipo": "escrito",
        "descripcion": "Da volumen a tus dibujos con una fuente de luz clara, cinco valores y un buen control de los bordes.",
        "lecciones": [
            {
                "titulo": "Elige una sola fuente de luz",
                "texto": """
El volumen se entiende cuando la luz viene de un lugar claro. Si iluminas el modelo desde todas partes, las sombras se contradicen y el dibujo se aplana.

## Antes de sombrear
1. Decide de dónde viene la luz y márcalo con una flecha pequeña en una esquina de la hoja.
2. Separa el dibujo en dos familias: lo que recibe luz y lo que queda en sombra.
3. Rellena toda la familia de sombra con un tono plano y uniforme.

Solo con ese paso, el objeto ya parece tener volumen. El detalle de la sombra viene después.

## Un truco útil
Entrecierra los ojos al mirar el modelo. Los detalles desaparecen y quedan las manchas grandes de luz y de sombra.

## Ejercicio
Ilumina un huevo con una lámpara de escritorio y dibújalo usando únicamente dos tonos.
""",
            },
            {
                "titulo": "Los cinco valores de una forma",
                "texto": """
Sobre una forma redondeada, la luz produce cinco zonas. Reconocerlas te permite sombrear cualquier objeto sin copiar manchas al azar.

- Luz plena: la zona que mira directo hacia la fuente de luz.
- Medio tono: donde la superficie empieza a girar y a alejarse de la luz.
- Sombra propia: la franja más oscura del objeto, justo donde la luz ya no llega.
- Luz reflejada: un rebote suave del entorno dentro de la sombra.
- Sombra proyectada: la que el objeto arroja sobre la mesa o sobre otros objetos.

## El error más común
Aclarar demasiado la luz reflejada. Pertenece a la familia de sombra, así que debe ser más oscura que cualquier medio tono.

## Ejercicio
Dibuja una esfera y escribe al margen el nombre de cada una de las cinco zonas.
""",
            },
            {
                "titulo": "Bordes duros y bordes suaves",
                "texto": """
El borde entre dos tonos dice tanto como los tonos mismos. Un dibujo con todos los bordes iguales se ve recortado o borroso.

## Qué borde usar
- Duro: en las aristas, como la esquina de una caja, y en las sombras proyectadas cerca del objeto.
- Suave: donde una forma redonda gira poco a poco, como una mejilla o una esfera.
- Perdido: donde dos zonas tienen casi el mismo tono y el contorno desaparece.

Una sombra proyectada es más nítida junto al objeto y se difumina al alejarse de él.

## Dirige la mirada
El ojo va primero al borde más duro y al mayor contraste. Reserva ambos para el punto que más te interesa y suaviza el resto.

## Ejercicio
Dibuja un cubo y una esfera juntos. Usa bordes duros en el cubo y suaves en la esfera.
""",
            },
        ],
    },
    {
        "titulo": "Tips de dibujo: figura humana y gesto",
        "tipo": "escrito",
        "descripcion": "Captura el movimiento con la línea de acción y apóyate en proporciones sencillas para la figura, las manos y los pies.",
        "lecciones": [
            {
                "titulo": "Empieza por la línea de acción",
                "texto": """
Antes que la anatomía está el gesto: la sensación de movimiento de toda la figura. Se resume en una sola curva, la línea de acción, que va de la cabeza a los pies.

## Cómo practicar el gesto
1. Usa poses de entre 30 segundos y 2 minutos. El límite te obliga a ver lo esencial.
2. Traza primero la línea de acción, de un solo movimiento.
3. Añade la cabeza, la caja torácica y la pelvis como tres masas simples.
4. Indica cada brazo y cada pierna con una sola línea.

Prefiere las curvas en forma de C y de S. Una figura hecha de rectas se ve rígida.

## Exagera un poco
Si la pose se inclina, inclínala más. El gesto exagerado se lee mejor y siempre se puede moderar después.

## Ejercicio
Haz diez gestos de un minuto a partir de fotografías de deportistas o bailarines.
""",
            },
            {
                "titulo": "Proporciones medidas en cabezas",
                "texto": """
La cabeza es la unidad de medida más cómoda para la figura. Un adulto promedio mide entre siete y media y ocho cabezas de alto.

## Puntos de referencia
- La entrepierna queda cerca de la mitad de la altura total.
- Con el brazo relajado, el codo cae a la altura de la cintura.
- La muñeca llega a la altura de la entrepierna, y la punta de los dedos, a medio muslo.
- Los hombros miden entre dos y dos cabezas y media de ancho.

Son promedios para empezar, no reglas fijas. Cada persona varía, y los niños tienen la cabeza proporcionalmente más grande.

## Revisa el conjunto
Marca primero la altura total y la mitad. Después reparte las demás medidas dentro de ese marco.

## Ejercicio
Dibuja una figura de pie dentro de una columna de ocho cabezas y marca cada punto de referencia.
""",
            },
            {
                "titulo": "Manos y pies sin miedo",
                "texto": """
Las manos y los pies intimidan porque tienen muchas piezas pequeñas. La solución es la de siempre: empezar por las formas grandes.

## La mano
1. Dibuja la palma como una caja, algo más ancha por el lado de los dedos.
2. Añade el pulgar como una cuña que sale de un costado de la palma.
3. Traza los cuatro dedos como un solo bloque, igual que una manopla, y sepáralos después.

La mano abierta mide más o menos lo mismo que la cara, del mentón al nacimiento del pelo. Los nudillos forman un arco, no una recta.

## El pie
Piensa en una cuña: alta en el talón y baja hacia los dedos. El pie mide aproximadamente lo mismo que el antebrazo, del codo a la muñeca.

## Ejercicio
Dibuja tu mano libre en cinco posiciones distintas, empezando siempre por la caja de la palma.
""",
            },
        ],
    },
    {
        "titulo": "Blender 3D: primeros pasos en la interfaz",
        "tipo": "escrito",
        "descripcion": "Aprende a moverte por el visor, a transformar objetos y a mantener ordenada tu escena en Blender.",
        "lecciones": [
            {
                "titulo": "Muévete por el visor 3D",
                "texto": """
Lo primero en Blender es aprender a mirar la escena desde cualquier ángulo. Con tres movimientos del mouse ya puedes recorrerla.

## Navegación básica
- Orbitar: mantén presionado el botón central del mouse y arrastra.
- Desplazar: Shift + botón central.
- Acercar y alejar: gira la rueda del mouse.

## Vistas exactas
El teclado numérico cambia a vistas alineadas: 1 es la vista frontal, 3 la lateral derecha y 7 la superior. El 0 muestra lo que ve la cámara y el 5 alterna entre perspectiva y vista ortogonal.

Si pierdes de vista un objeto, selecciónalo y presiona el punto del teclado numérico para centrarlo.

## Sin teclado numérico
En Edit > Preferences > Input puedes activar «Emulate Numpad» para usar los números de la fila superior.

## Ejercicio
Abre la escena inicial y observa el cubo desde las vistas frontal, lateral, superior y de cámara.
""",
            },
            {
                "titulo": "Objetos, modos y transformaciones",
                "texto": """
Blender trabaja con modos. En Object Mode mueves objetos completos; en Edit Mode cambias su forma vértice a vértice. La tecla Tab alterna entre los dos.

## Las tres transformaciones
- G mueve.
- R rota.
- S escala.

Después de presionar una de ellas, la tecla X, Y o Z limita el movimiento a ese eje. También puedes escribir un valor exacto: G, Z, 2 y Enter suben el objeto dos metros.

Confirma con clic izquierdo o Enter, y cancela con clic derecho o Esc.

## Añadir y borrar
Shift + A abre el menú para añadir objetos nuevos. Con X eliminas lo que esté seleccionado.

## Ejercicio
Añade una esfera, súbela dos metros en Z y escálala a la mitad con S, 0.5 y Enter.
""",
            },
            {
                "titulo": "Guarda y organiza tu escena",
                "texto": """
Un archivo ordenado ahorra horas cuando el proyecto crece. Conviene adquirir el hábito desde la primera escena.

## Guardar
- Ctrl + S guarda el archivo .blend.
- Ctrl + Shift + S guarda una copia con otro nombre. Úsalo antes de un cambio arriesgado.
- Cada vez que guardas, Blender conserva la versión anterior como un archivo .blend1.

## Nombres y colecciones
- F2 cambia el nombre del objeto seleccionado. «Mesa» se encuentra más rápido que «Cube.014».
- M mueve el objeto a una colección. Las colecciones funcionan como carpetas en el Outliner, el panel de arriba a la derecha.
- El ícono del ojo oculta una colección completa mientras trabajas en otra cosa.

## Aplica la escala
Si escalaste un objeto en Object Mode, usa Ctrl + A > Scale. Así los modificadores y las texturas se comportan como esperas.

## Ejercicio
Crea las colecciones «Muebles» y «Luces» y reparte en ellas los objetos de tu escena.
""",
            },
        ],
    },
    {
        "titulo": "Blender 3D: modelado de un objeto sencillo",
        "tipo": "escrito",
        "descripcion": "Modela una taza paso a paso con primitivas, extrusiones, biseles y modificadores.",
        "lecciones": [
            {
                "titulo": "Bloquea la forma con primitivas",
                "texto": """
Modelar se parece a esculpir: primero la silueta general y al final el detalle. Para una taza, el punto de partida es un cilindro.

## Paso a paso
1. Borra el cubo inicial con X y añade un cilindro con Shift + A > Mesh > Cylinder.
2. En el panel que aparece abajo a la izquierda, baja «Vertices» a 16. Con menos geometría es más fácil editar.
3. Escala el cilindro con S hasta que tenga la proporción de una taza.

## Pocas caras al principio
Una malla ligera se corrige rápido. La suavidad se añade después con un modificador, no con miles de vértices colocados a mano.

## Usa referencias
Ten una foto de la taza a la vista y compara la silueta desde la vista frontal, con el 1 del teclado numérico.

## Ejercicio
Bloquea una taza, un plato y una cuchara usando solo cilindros y cubos escalados.
""",
            },
            {
                "titulo": "Extruir, insertar y cortar bucles",
                "texto": """
Con tres herramientas de Edit Mode se resuelve la mayor parte del modelado. Entra con Tab y elige si seleccionas vértices, aristas o caras con las teclas 1, 2 y 3 de la fila superior.

## Las tres herramientas
- Extruir (E): saca geometría nueva desde lo seleccionado.
- Insertar (I): crea una cara más pequeña dentro de la cara seleccionada.
- Corte en bucle (Ctrl + R): añade un anillo de aristas alrededor de la malla.

## Vaciar la taza
1. Selecciona la cara superior del cilindro.
2. Presiona I y mueve el mouse para marcar el grosor de la pared.
3. Presiona E y baja la nueva cara para formar el hueco.

## Suaviza las aristas
Selecciona el borde superior y usa Ctrl + B para biselarlo. Gira la rueda del mouse para añadir segmentos.

## Ejercicio
Vacía tu taza y añade dos cortes en bucle en el costado, donde irá el asa.
""",
            },
            {
                "titulo": "Modificadores que ahorran trabajo",
                "texto": """
Los modificadores cambian el objeto sin destruir la malla original. Puedes ajustarlos o quitarlos cuando quieras en la pestaña de la llave inglesa, dentro del panel de propiedades.

## Tres imprescindibles
- Subdivision Surface: suaviza la malla. Con el objeto seleccionado, Ctrl + 2 lo añade con dos niveles.
- Mirror: refleja la mitad del modelo, así trabajas un solo lado.
- Bevel: redondea todas las aristas a la vez.

## Controla el suavizado
Al subdividir, las esquinas se redondean demasiado. Añade un corte en bucle con Ctrl + R cerca de un borde para mantenerlo definido.

Con clic derecho > Shade Smooth desaparece el aspecto facetado de la superficie.

## Ejercicio
Añade Subdivision Surface a tu taza y coloca un corte en bucle cerca de la base para que apoye plana.
""",
            },
        ],
    },
    {
        "titulo": "Blender 3D: materiales, luz y render",
        "tipo": "escrito",
        "descripcion": "Dale color a tu modelo, ilumínalo con tres luces y obtén tu primera imagen final.",
        "lecciones": [
            {
                "titulo": "Materiales con Principled BSDF",
                "texto": """
Un material define cómo responde una superficie a la luz. En Blender, casi todo se resuelve con un solo nodo: Principled BSDF.

## Crea tu primer material
1. Selecciona el objeto y abre la pestaña de materiales, la del ícono de esfera, en el panel de propiedades.
2. Presiona New.
3. Cambia Base Color para elegir el color.

## Los tres controles clave
- Base Color: el color de la superficie.
- Metallic: 0 para plástico, madera o cerámica, y 1 para metal. Casi nunca se usan valores intermedios.
- Roughness: cerca de 0, la superficie brilla como un espejo; cerca de 1, queda mate.

Para ver el resultado, mantén presionada la Z en el visor y elige Material Preview.

## Ejercicio
Crea tres materiales para tu taza: cerámica brillante, cerámica mate y metal pulido.
""",
            },
            {
                "titulo": "Iluminación de tres puntos",
                "texto": """
El esquema de tres puntos viene de la fotografía y funciona con casi cualquier objeto. Usa tres luces, cada una con una tarea.

- Luz principal: la más intensa. Colócala a unos 45 grados del objeto y algo más alta que él.
- Luz de relleno: del lado opuesto y mucho más débil. Aclara las sombras sin borrarlas.
- Contraluz: detrás del objeto, apuntando hacia la cámara. Dibuja un filo de luz que lo separa del fondo.

## En Blender
Añade cada luz con Shift + A > Light > Area. En sus propiedades, Power controla la intensidad y Size la suavidad: una luz más grande da sombras más suaves.

## Empieza por una
Enciende primero solo la luz principal. Cuando te guste la sombra, añade las otras dos.

## Ejercicio
Ilumina tu taza con tres luces de área y compara el resultado al ocultar cada una.
""",
            },
            {
                "titulo": "Cámara y render final",
                "texto": """
El render es la imagen terminada. Antes de lanzarlo hay que decidir el encuadre y el motor de render.

## Coloca la cámara
1. Navega en el visor hasta encontrar un ángulo que te guste.
2. Presiona Ctrl + Alt + 0 del teclado numérico: la cámara salta a esa vista.
3. Usa el 0 del teclado numérico para volver a mirar a través de ella.

## Elige el motor
- Eevee: casi instantáneo, ideal para pruebas y animación.
- Cycles: simula la luz con más realismo, pero tarda más.

Se cambian en la pestaña Render del panel de propiedades. En Cycles, activa Denoise para limpiar el ruido de la imagen.

## Lanza el render
F12 genera la imagen. En la ventana que se abre, usa Image > Save As para guardarla como PNG.

## Ejercicio
Renderiza tu taza con Eevee y con Cycles, y compara las sombras y los reflejos.
""",
            },
        ],
    },
    {
        "titulo": "Diseño web: jerarquía visual y tipografía",
        "tipo": "escrito",
        "descripcion": "Ordena una página para que se entienda de un vistazo: jerarquía, tipografías y espacio.",
        "lecciones": [
            {
                "titulo": "Decide qué se lee primero",
                "texto": """
Una página se escanea antes de leerse. La jerarquía visual es el orden en que el ojo recorre los elementos, y te toca a ti decidirlo.

## Herramientas para crear jerarquía
- Tamaño: lo más grande se lee primero.
- Peso y color: una negrita o un color intenso destacan sobre un gris.
- Posición: lo que está arriba y a la izquierda se ve antes, en los idiomas que se leen de izquierda a derecha.
- Espacio: un elemento rodeado de aire parece más importante.

## Una sola acción principal
Cada pantalla debería tener un único botón protagonista. Si todo destaca, nada destaca.

## La prueba del desenfoque
Aléjate de la pantalla o desenfoca una captura. Lo que todavía se distingue es tu jerarquía real.

## Ejercicio
Toma la portada de un sitio que uses y numera sus elementos según el orden en que los miras.
""",
            },
            {
                "titulo": "Elige y combina tipografías",
                "texto": """
El texto ocupa la mayor parte de casi cualquier página. Con pocas decisiones bien tomadas, se vuelve cómodo de leer.

## Reglas prácticas
- Usa dos familias como máximo: una para títulos y otra para el texto.
- El texto de lectura no debería bajar de 16 px.
- Un interlineado de alrededor de 1.5 da aire a los párrafos.
- Limita cada línea a entre 45 y 75 caracteres. Las líneas muy largas cansan.

## Crea una escala
Define unos pocos tamaños y repítelos siempre, por ejemplo 16, 20, 25 y 31 px. Cada uno multiplica al anterior por 1.25.

## Contrasta con intención
Combina familias claramente distintas, como una con serifa y otra sin ella. Dos tipografías casi iguales parecen un error.

## Ejercicio
Define una escala de cuatro tamaños y aplícala al título, al subtítulo, al texto y a las notas de una página.
""",
            },
            {
                "titulo": "Espaciado y alineación",
                "texto": """
El espacio en blanco no es espacio desperdiciado: agrupa, separa y da orden. Muchos diseños mejoran solo con ajustar los márgenes.

## Proximidad
Lo que está cerca se entiende como relacionado. Un título debe quedar más cerca de su párrafo que del párrafo anterior.

## Un sistema de espacios
Elige una unidad base, como 8 px, y usa solo sus múltiplos: 8, 16, 24, 32 y 48. El resultado se ve coherente sin medir cada caso.

## Alineación
- Alinea los elementos a unas pocas líneas verticales imaginarias.
- El texto largo se lee mejor alineado a la izquierda.
- Centra solo los textos cortos, como un título o una frase destacada.

## Ejercicio
Rehaz una tarjeta de producto usando únicamente espacios de 8, 16 y 24 px.
""",
            },
        ],
    },
    {
        "titulo": "Diseño web: color y diseño adaptable",
        "tipo": "escrito",
        "descripcion": "Arma una paleta sencilla, comprueba su contraste y diseña páginas que funcionen en cualquier pantalla.",
        "lecciones": [
            {
                "titulo": "Una paleta que funcione",
                "texto": """
Una buena paleta web tiene pocos colores y un papel claro para cada uno. Más colores no hacen una página más atractiva: la hacen más confusa.

## La regla 60-30-10
- 60 %: un color dominante y neutro, casi siempre el fondo.
- 30 %: un color secundario para paneles, tarjetas y secciones.
- 10 %: un color de acento para botones y enlaces.

## Construye la paleta
1. Elige el color de acento según el tono de la marca.
2. Genera de cuatro a seis grises para fondos, bordes y textos.
3. Reserva colores fijos para los estados: verde para éxito, rojo para error y amarillo para aviso.

## Cuida el acento
Si el color de acento aparece en todas partes, deja de señalar lo importante.

## Ejercicio
Diseña una paleta con un acento, cinco grises y tres colores de estado, y pruébala en un formulario.
""",
            },
            {
                "titulo": "Contraste y accesibilidad",
                "texto": """
Un texto que no se distingue del fondo no cumple su función. El contraste se puede medir, así que no hace falta adivinar.

## Los mínimos de las pautas WCAG
- 4.5:1 para el texto normal.
- 3:1 para el texto grande: desde unos 24 px, o desde unos 19 px si va en negrita.
- 3:1 para los íconos y los bordes de los controles.

Las herramientas para desarrolladores del navegador muestran la relación de contraste al inspeccionar un texto.

## No dependas solo del color
Cerca de uno de cada doce hombres confunde algunos colores. Acompaña el color con un ícono o un texto: un error se marca en rojo y, además, con un mensaje.

## El foco importa
Quien navega con el teclado necesita ver qué elemento está activo. No quites el contorno de foco sin reemplazarlo por otro visible.

## Ejercicio
Mide el contraste de los textos de tu página y corrige los que no lleguen a 4.5:1.
""",
            },
            {
                "titulo": "Diseña primero para móvil",
                "texto": """
Buena parte de las visitas llega desde un teléfono. Si diseñas primero la pantalla pequeña, te obligas a decidir qué es realmente importante.

## Principios
- Empieza con una sola columna y añade columnas cuando sobre espacio.
- Usa medidas flexibles, como porcentajes y rem, en lugar de anchos fijos en píxeles.
- Deja que las imágenes se adapten con la regla max-width: 100%.
- Da a los botones y enlaces un área táctil de al menos 44 px de alto.

## Puntos de quiebre
No diseñes para un modelo de teléfono en particular. Ensancha la ventana poco a poco y añade un punto de quiebre cuando el contenido empiece a verse mal.

## Prueba de verdad
El modo adaptable del navegador ayuda, pero revisa también la página en un teléfono real y con una sola mano.

## Ejercicio
Diseña una página de curso a 360 px de ancho y adáptala después a 768 y a 1280 px.
""",
            },
        ],
    },
    {
        "titulo": "Composición artística: encuadre y puntos de interés",
        "tipo": "escrito",
        "descripcion": "Decide dónde mira el espectador con la regla de tercios, las líneas guía y el espacio negativo.",
        "lecciones": [
            {
                "titulo": "La regla de tercios y sus límites",
                "texto": """
Divide la imagen con dos líneas horizontales y dos verticales, como un tablero de tres en raya. Los cuatro cruces son puntos fuertes: lo que coloques ahí atrae la mirada con naturalidad.

## Cómo aplicarla
- Sitúa el sujeto principal sobre un cruce, no en el centro exacto.
- Alinea el horizonte con la línea superior o con la inferior, según quieras dar peso a la tierra o al cielo.
- Deja más espacio hacia donde mira o se mueve el sujeto.

## Cuándo romperla
Un sujeto centrado transmite calma, solemnidad o simetría. Funciona muy bien en retratos frontales y en arquitectura.

La regla es un punto de partida, no una obligación. Lo importante es que la posición del sujeto sea una decisión.

## Ejercicio
Haz tres bocetos pequeños de la misma escena: con el sujeto centrado, a la izquierda y a la derecha.
""",
            },
            {
                "titulo": "Líneas que guían la mirada",
                "texto": """
El ojo sigue las líneas casi sin darse cuenta. Un camino, un río, una barandilla o un brazo extendido pueden llevar al espectador hasta el punto de interés.

## Tipos de líneas
- Diagonales: dan energía y sensación de movimiento.
- Curvas en S: recorren la imagen con suavidad.
- Convergentes: crean profundidad, como las vías de un tren.
- Implícitas: la dirección de una mirada o de un gesto también funciona como línea.

## Cuida los bordes
Una línea fuerte que sale por una esquina se lleva la mirada fuera del cuadro. Cierra la composición con un elemento que la devuelva hacia dentro.

## Ejercicio
Elige una pintura que te guste y calca sobre ella las líneas principales. Observa hacia dónde apuntan.
""",
            },
            {
                "titulo": "El espacio negativo",
                "texto": """
El espacio negativo es el área vacía que rodea al sujeto. No es un sobrante: le da forma, aire e importancia.

## Para qué sirve
- Aísla al sujeto y lo vuelve protagonista.
- Transmite calma, silencio o soledad.
- Deja lugar para un título, si la imagen es un cartel o una portada.

## Revisa la silueta
Rellena el sujeto de negro y mira solo su contorno. Si se entiende qué es y qué hace, la pose y el encuadre funcionan.

## Evita las tangentes
Cuando el borde de un objeto apenas roza otro objeto o el margen del cuadro, se crea una tensión incómoda. Sepáralos con claridad o haz que se superpongan.

## Ejercicio
Dibuja un mismo objeto ocupando el 80 % del cuadro y después solo el 10 %. Compara lo que transmite cada versión.
""",
            },
        ],
    },
    {
        "titulo": "Composición artística: equilibrio, ritmo y color",
        "tipo": "escrito",
        "descripcion": "Reparte el peso visual, crea ritmo con repeticiones y planifica el color a partir del valor.",
        "lecciones": [
            {
                "titulo": "Equilibrio simétrico y asimétrico",
                "texto": """
Cada elemento de una imagen tiene un peso visual. Pesan más los elementos grandes, oscuros, saturados, detallados o aislados. Componer es repartir ese peso.

## Dos maneras de equilibrar
- Simétrico: los dos lados se reflejan. Transmite orden, estabilidad y formalidad.
- Asimétrico: pesos distintos que se compensan, como un elemento grande cerca del centro y uno pequeño lejos de él. Resulta más dinámico.

## La prueba del espejo
Voltea la imagen horizontalmente o mírala en un espejo. Al verla como si fuera nueva, los desequilibrios saltan a la vista.

## Ejercicio
Coloca tres rectángulos de distinto tamaño dentro de un cuadro hasta que se sientan equilibrados sin ser simétricos.
""",
            },
            {
                "titulo": "Ritmo y repetición",
                "texto": """
Repetir un elemento crea ritmo, igual que en la música. El ojo salta de una repetición a la siguiente y recorre toda la imagen.

## Tipos de ritmo
- Regular: el mismo elemento a intervalos iguales, como una fila de columnas. Transmite orden.
- Alterno: dos elementos que se turnan.
- Progresivo: el elemento cambia poco a poco de tamaño, de color o de separación. Sugiere profundidad o movimiento.

## Rompe el patrón
Una sola excepción dentro de una repetición se convierte en el punto focal: la única ventana encendida, la única flor roja.

## No lo recargues
Demasiada repetición sin variación aburre. Agrupa los elementos y deja zonas de descanso entre los grupos.

## Ejercicio
Dibuja una fila de árboles con ritmo progresivo y haz que uno solo rompa el patrón.
""",
            },
            {
                "titulo": "Valor antes que color",
                "texto": """
El valor es qué tan claro u oscuro es un tono. Sostiene la imagen más que el color: si los valores funcionan, casi cualquier paleta sirve.

## Planifica en tres valores
Antes de pintar, haz un boceto pequeño con solo tres tonos: claro, medio y oscuro. Si la escena se entiende así, la composición es sólida.

## Armonías de color
- Complementarios: colores opuestos en el círculo cromático, como azul y naranja. Dan el máximo contraste.
- Análogos: colores vecinos, como amarillo, naranja y rojo. Dan unidad.
- Tríada: tres colores a la misma distancia entre sí. Es vibrante y más difícil de equilibrar.

## Un color manda
Deja que un color domine, que otro lo acompañe y que el tercero aparezca solo como acento.

## Ejercicio
Pinta la misma composición dos veces: una con colores análogos y otra con complementarios.
""",
            },
        ],
    },
]

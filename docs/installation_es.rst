= 0. Preliminares

El presente documento de instalación se desarrolla en un entorno Debian Jessie, por lo que los comandos a ingresar en consola corresponden a la sintaxis de este sistema operativo.

Este proyecto utiliza las siguientes librerías de terceros, por lo que se recomienda proceder con su instalación antes de continuar con este instructivo:

* FreeLing 4.0 [http://nlp.lsi.upc.edu/freeling/node/1]
* kenlm [https://kheafield.com/code/kenlm/]
* foma [https://fomafst.github.io/]

Téngase por favor en cuenta que la instalación de tales librerías está por fuera del alcance de este documento. Asegúrese entonces que las respectivas instalaciones sean satisfactorias.

== 0.1 Estimar un modelo de lenguaje de n-gramas de la Wikipedia en español
En esta sección se describirá el proceso de estimación de un modelo de lenguaje utilizando el corpus de la Wikipedia en español. El proceso entonces va desde la descarga de un backup del mencionado recurso lingüístico (ojalá el más reciente), hasta la estimación de un modelo de trigramas. A continuación el paso a paso:

1. Instalar ruby. Esto se consigue ingresanfo el siguiente comando en consola: "sudo apt-get install ruby".

Nótese que, según la documentación de CorpusPedia [http://gramatica.usc.es/pln/tools/CorpusPedia.html] (que utilizaremos para crear un corpus de la Wikipedia, al que luego preprocesaremos) la versión requerida de 'ruby' es la "1.9.1". Sin embargo, esta versión no está más disponible en los repositorios de la distribución Debian Jessie, por lo que utilizaremos la "2.1.5".

2. Descargar un backup de la Wikipedia en español. Para ello, ingrese a la dirección electrónica [https://dumps.wikimedia.org/eswiki/], escoja una fecha (ojalá la más reciente) y descarge la versión "page-articles"-"eswiki-YYYYMMDD-pages-articles.xml.bz2" de la Wikipedia. Tenga en cuenta que descargará varias gigas de información, por lo que la descarga tomará varios minutos. Finalmente, disponga el archivo descargado en la ruta "/normalesp/datasets/eswiki/src/" y descomprímalo.

3. Crear un corpus de la Wikipedia en español. Ubíquese en la ruta "/normalesp/datasets/eswiki/CorpusPedia_alfa/" e ingrese el siguiente comando: "ruby corpuspedia.rb -c -lang:es". Este proceso, que tal vez tomará varios minutos e incluso horas, generará como resultado el archivo ""/normalesp/datasets/eswiki/corpus/eswiki-corpus.txt". Tenga en cuenta que este no es el corpus definitivo que se utilizará para la estimación del modelo de lenguaje, pero sí corresponde a su base.

Debido a que CorpusPedia genera algunos directorios y archivos que no son utilizados en la estimación del modelo de lenguaje, se puede proceder a eliminarlos. Estos son:

* "/normalesp/datasets/eswiki/comparable/".
* "/normalesp/datasets/eswiki/data/".
* "/normalesp/datasets/eswiki/log/".
* "/normalesp/datasets/eswiki/ontology/".

Igualmente, puede eliminarse el corpus original descomprimido ("/normalesp/datasets/eswiki/src/eswiki-YYYYMMDD-pages-articles.xml").

4. Ejecutar el programa "/normalesp/datasets/eswiki/parsers/filter_out_tags.py". Este programa genera como resultado el archivo "/normalesp/datasets/eswiki/corpus/eswiki-corpus_preproc-step-0.txt", el cual se utilizará como entrada en el siguiente paso; es por esto que, el archivo "/normalesp/datasets/eswiki/corpus/eswiki-corpus.txt" debería ser eliminado, pues no será más utilizado.

NOTA: este proceso tardará varios minutos.

5. Ejecutar el programa "/normalesp/datasets/eswiki/parsers/parse_wikitext.py". Este programa genera como resultado el archivo "/normalesp/datasets/eswiki/corpus/eswiki-plaintext-corpus.txt", el cual se utilizará como entrada en el siguiente paso; es por esto que, el archivo "/normalesp/datasets/eswiki/corpus/eswiki-corpus_preproc-step-0.txt" debería ser eliminado, pues no será más utilizado.

NOTA: este proceso tardará varias horas.

6. Analizar morfológicamente el corpus de la Wikipedia y realiza etiquetado "Part-of-Speech". Para llevar a cabo este proceso se utilizará la librería FreeLing, la cual se instanciará en modo servidor a fin de procesar las solicitudes de clientes evitando su reinicio entre cada una de estas.

Antes de instanciar FreeLing, el usuario debería revisar que las rutas y archivos de configuración relacionados en "/normalesp/datasets/eswiki/parsers/analyzer.cfg" están bien definidos.

Se procede entonces a instanciar Freeling en modo servidor, así: "analyzer -f /normalesp/datasets/eswiki/parsers/analyzer.cfg --server --port 50005 &". A continuación, ejecute el programa "/normalesp/datasets/eswiki/parsers/morpho_analysis.py".

Una vez finalizada la ejecución del programa Python, se generará el archivo "/normalesp/datasets/eswiki/corpus/eswiki-tagged-plaintext-corpus.txt", el cual se utilizará como entrada en el siguiente paso; por tal motivo, se sugiere eliminar el archivo "/normalesp/datasets/eswiki/corpus/eswiki-plaintext-corpus.txt".

NOTA: este proceso tardará varias horas.

7. Ejecutar el programa "/normalesp/datasets/eswiki/parsers/build_corpus.py". Este programa genera la versión final del corpus de la Wikipedia en español que se utilizará para estimar el modelo de lenguaje, a saber: "/normalesp/datasets/eswiki/corpus/eswiki-corpus.txt". Por lo anterior, se sugiere eliminar el archivo "/normalesp/datasets/eswiki/corpus/eswiki-tagged-plaintext-corpus.txt".

8. Estimar el modelo de lenguaje del corpus de la Wikipedia en español. Para estimar un modelo de lenguaje de trigramas (3-gramas) del corpus de la Wikipedia en español, se utilizará la herramienta kenlm. Este proceso toma como entrada el corpus resultante del paso anterior, y genera un archivo en formato "arpa". A continuación se relaciona el comando para estimar el modelo de lenguaje, agregando que el archivo resultante se dispondrá en la ruta "/normalesp/datasets/eswiki/corpora/":

"bin/lmplz -o 3 -S 12G </normalesp/datasets/eswiki/corpus/eswiki-corpus.txt >/normalesp/datasets/eswiki/corpora/eswiki-corpus-3-grams.arpa"

NOTA: el parámetro "-S" sirve para especificar la cantidad de memoria que se utilizará. Como puede observarse, se han especificado 12G; sin embargo, el usuario puede modificar la cantidad de memoria a utilizar según su criterio.

9. Convertir el modelo de lenguaje en un binario. Un formato de archivo binario permite que el modelo de lenguaje se cargue más rápido, a la vez que reduce el tamaño de archivo.

"bin/build_binary /normalesp/datasets/eswiki/corpora/eswiki-corpus-3-grams.arpa /normalesp/datasets/eswiki/corpora/eswiki-corpus-3-grams.bin"

Finalmente, se sugiere eliminar el archivo "/normalesp/datasets/eswiki/corpora/eswiki-corpus-3-grams.arpa", puesto que no se utilizará más.

== 0.2 Compilar transductores de estado finito
El objetivo de esta sección es describir cómo compilar los archivos fuentes de los transductores en binarios, tal que estos últimos puedan ser utilizados por el programa principal de este proyecto. A continuación se relaciona cómo compilar cada uno de los 20 transductores de estado finito.

Antes de continuar, es importante mencionar que las rutas de los directorios donde se disponen los archivos fuentes y los binarios son "/normalesp/datasets/transducers/src/" y "/normalesp/datasets/transducers/bin/", respectivamente. Así mismo, el comando para iniciar foma es "/ruta/a/foma/foma"; foma debería iniciarse desde el directio de los archivos fuentes.

* "es-dicc":
0. Inicie foma.
1. "read text es-dicc.txt".
2. "save stack es-dicc.bin".
3. Mueva el binario resultante al respectivo directorio. Sin embargo, deje una copia del binario en el directorio de archivos fuentes.
4. Finalice la instancia de foma ("exit").

* "pnd-gazetteer":
0. Inicie foma.
1. "read text PND-gazetteer.txt".
2. "save stack PND-Gazetteer.bin".
3. Mueva el binario resultante al respectivo directorio.
4. Finalice la instancia de foma ("exit").

* "normalization_dicc":
0. Inicie foma.
1. "read spaced-text normalisation_dicc.txt".
2. "save stack normalisation_dicc.bin".
3. Finalice la instancia de foma ("exit").
NOTA: este archivo no se dispondrá en el directorio de binarios por tratarse de un temporal.

* "primary_variants":
0. Inicie foma.
1. "source primary_variants.foma".
2. Mueva el binario resultante ("primary_variants.bin") al respectivo directorio.
3. Finalice la instancia de foma ("exit").

* "dictionary_lookup":
0. Inicie foma.
1. "source dictionary_lookup.foma".
2. Mueva el binario resultante ("dictionary_lookup.bin") al respectivo directorio.
3. Finalice la instancia de foma ("exit").

* "phonology":
0. Inicie foma.
1. "source phonology.foma".
2. "save stack phonology.bin".
3. Mueva el binario resultante al respectivo directorio. Sin embargo, deje una copia del binario en el directorio de archivos fuentes.
4. Finalice la instancia de foma ("exit").

* "secondary_variants-dicc":
0. Inicie foma.
1. "source secondary_variants.foma".
2. Mueva el binario resultante ("secondary_variants-Dicc.bin") al respectivo directorio.
3. Finalice la instancia de foma ("exit").
Nota: la compilación de este transductor requiere, por lo menos, 2.5G de memoria RAM. Sin embargo, el binario en memoria ocupará 165.5M de RAM.

* "es-verbal-forms-fonemas":
0. Inicie foma.
1. "source es-verbal-forms-fonemas.foma".
2. "save stack es-verbal-forms-fonemas.bin".
3. Mueva el binario resultante al respectivo directorio.
4. Finalice la instancia de foma ("exit").

* "es-diminutives-fonemas":
0. Inicie foma.
1. "source es-diminutives-fonemas.foma".
2. "save stack es-diminutives-fonemas.bin".
3. Mueva el binario resultante al respectivo directorio.
4. Finalice la instancia de foma ("exit").

* "pnd-gazetteer-fonemas":
0. Inicie foma.
1. "source PND-gazetteer-fonemas.foma".
2. "save stack PND-gazetteer-fonemas.bin".
3. Mueva el binario resultante al respectivo directorio.
4. Finalice la instancia de foma ("exit").

* "pnd-gazetteer-lowercase":
0. Inicie foma.
1. "read text PND-gazetteer-lowercase.txt".
2. "save stack PND-gazetteer-lowercase.bin".
3. Finalice la instancia de foma ("exit").
NOTA: este archivo no se dispondrá en el directorio de binarios por tratarse de un temporal.

* "tertiary_variants-dicc" y "tertiary_variants-pnd":
0. Inicie foma.
1. "source tertiary_variants.foma".
2. Mueva los binarios resultantes ("tertiary_variants-Dicc.bin" y "tertiary_variants-PND.bin") al respectivo directorio.
3. Finalice la instancia de foma ("exit").
Nota: la compilación de este transductor requiere, por lo menos, 9G de memoria RAM. Sin embargo, el binario "tertiary_variants-Dicc.bin", que es el que más memoria RAM requiere en compilación, requerirá 1.3G de RAM.

* "pnd-gazetteer-case":
0. Inicie foma.
1. "read spaced-text PND-gazetteer-CaSe.txt".
2. "save stack PND-gazetteer-CaSe.bin".
3. Mueva el binario resultante al respectivo directorio.
4. Finalice la instancia de foma ("exit").

* "iv-candidates-fonemas":
0. Inicie foma.
1. "source IV-candidates-fonemas.foma".
2. "save stack IV-candidates-fonemas.bin".
3. Mueva el binario resultante al respectivo directorio.
4. Finalice la instancia de foma ("exit").

* "split-words" y "other-changes":
0. Comente las siguientes líneas del archivo "tertiary_variants.foma", poniendo el caracter "#" (sin comillas) al inicio de cada una de estas:
# Variantes terciarias del diccionario estándar:
regex TertiaryBase1Transducer .o. StandardDicc;
save stack tertiary_variants-Dicc.bin

clear

regex TertiaryBase3Transducer .o. PNDGazetteer;
save stack tertiary_variants-PND.bin

Por lo que, una vez comentadas las líneas, el código debería verse así:
# Variantes terciarias del diccionario estándar:
# regex TertiaryBase1Transducer .o. StandardDicc;
# save stack tertiary_variants-Dicc.bin

# clear

# regex TertiaryBase3Transducer .o. PNDGazetteer;
# save stack tertiary_variants-PND.bin
1. Inicie foma.
2. "source split-words.foma".
3. "clear".
4. "regex OtherChanges;".
5. "save stack other-changes.bin".
6. Mueva los binarios resultantes ("split-words.bin" y "other-changes.bin") al respectivo directorio.
7. Finalice la instancia de foma ("exit").
8. Descomente las líneas modificadas en el paso 0. Por lo tanto, el archivo "tertiary_variants.foma" debería verse así:
# Variantes terciarias del diccionario estándar:
regex TertiaryBase1Transducer .o. StandardDicc;
save stack tertiary_variants-Dicc.bin

clear

regex TertiaryBase3Transducer .o. PNDGazetteer;
save stack tertiary_variants-PND.bin

* "length_normalisation" y "length_normalisation-2":
0. Inicie foma.
1. "regex LengtheningNormalisation;".
2. "save stack length_normalisation.bin".
3. "clear".
4. "regex LengtheningNormalisation2;".
5. "save stack length_normalisation-2.bin".
6. Mueva los binarios resultantes ("length_normalisation.bin" y "length_normalisation-2.bin") al respectivo directorio.
7. Finalice la instancia de foma ("exit").

* "remove_enclitic", "accentuate_enclitic" y "remove_mente":
0. Inicie foma.
1. "source affix_check.foma".
2. "regex RemoveEnclitic;".
3. "save stack remove_enclitic.bin".
4. "clear".
5. "regex AccentuateEnclitic;".
6. "save stack accentuate_enclitic.bin".
7. "clear".
8. "regex RemoveMente;".
9. "save stack remove_mente.bin".
10. Mueva los binarios resultantes ("remove_enclitic.bin", "accentuate_enclitic.bin" y "remove_mente.bin") al respectivo directorio.
11. Finalice la instancia de foma ("exit").

En este punto, se han compilado los 20 transductores y los binarios resultantes movido al respectivo directorio. Por lo que, se eliminarán los binarios en el directorio "/normalesp/datasets/transducers/src/", a saber:

* "es-dicc.bin".
* "normalisation_dicc.bin".
* "phonology.bin".
* "PND-gazetteer-lowercase.bin".

0. Preliminares
===============

Este documento de instalación se desarrolla en un entorno ``Debian 8 "jessie"``, por lo que los comandos a ingresar en consola corresponden a la sintaxis de este sistema operativo.

Este proyecto utiliza las siguientes librerías de terceros, por lo que se recomienda proceder con su instalación antes de continuar con este instructivo:

- FreeLing 4.0 [http://nlp.lsi.upc.edu/freeling/node/1].
- kenlm [https://kheafield.com/code/kenlm/].
- foma 0.9.18alpha [https://fomafst.github.io/].

Téngase por favor en cuenta que la instalación de tales librerías está por fuera del alcance de este documento. Asegúrese entonces que las librearías sean instaladas satisfactoriamente.

0.1 Requerimientos del sistema
------------------------------

Instalación
    Para llevar a cabo la instalación, se requieren 12G de memoria RAM disponibles.

Uso
    Se recomienda 4G de memoria RAM disponibles.

0.2 Dependencias de Python
--------------------------

Este proyecto requiere ``Python 2.7``.

La lista completa de módulos Python que se requieren, puede encontrarse en el archivo ``/requirements.txt``.

1. Estimar un modelo de lenguaje de *n*-gramas de la Wikipedia en español
=========================================================================

A lo largo de esta sección se describirá el proceso de estimación de un modelo de lenguaje utilizando el corpus de la Wikipedia en español. Este proceso entonces va desde la descarga de un *backup* del mencionado recurso lingüístico (ojalá el más reciente), hasta la estimación de un modelo de *trigramas*. A continuación el paso a paso:

**1. Instalar** ``ruby``. Esto se consigue ingresando el siguiente comando en consola::

    $ sudo apt-get install ruby

Nótese que según la documentación de ``CorpusPedia`` [http://gramatica.usc.es/pln/tools/CorpusPedia.html], librería que se utilizará para crear un corpus base de la Wikipedia en español, la versión requerida de ``ruby`` es la ``1.9.1``. Sin embargo, esta versión no está más disponible en los repositorios de la distribución ``Debian 8 "jessie"``, por lo que se utilizará la ``2.1.5``.

**2. Descargar un backup de la Wikipedia en español**. Para ello, ingrese a la dirección electrónica ``https://dumps.wikimedia.org/eswiki/``, escoja una fecha (ojalá la más reciente) y descarge el archivo ``eswiki-YYYYMMDD-pages-articles.xml.bz2``. Tenga en cuenta que se descargarán varios *gigabytes* de información, por lo que esta descarga tomará varios minutos. Finalmente, mueva el archivo descargado a la ruta ``/normalesp/datasets/eswiki/src/`` y descomprímalo.

**3. Crear un corpus de la Wikipedia en español.** Cambie el directorio a ``/normalesp/datasets/eswiki/CorpusPedia_alfa/`` e ingrese el siguiente comando: ``ruby corpuspedia.rb -c -lang:es``. Este proceso, que tal vez tomará varios minutos e incluso horas, generará como resultado el archivo ``/normalesp/datasets/eswiki/corpus/eswiki-corpus.txt``. Tenga en cuenta que este no es el corpus definitivo que se utilizará para la estimación del modelo de lenguaje, pero sí corresponde a su base.

Debido a que ``CorpusPedia`` genera algunos directorios y archivos que no se utilizarán en la estimación del modelo de lenguaje, se puede proceder a eliminarlos. Estos son:

- ``/normalesp/datasets/eswiki/comparable/``.
- ``/normalesp/datasets/eswiki/data/``.
- ``/normalesp/datasets/eswiki/log/``.
- ``/normalesp/datasets/eswiki/ontology/``.

Igualmente, puede eliminarse el corpus original descomprimido (``/normalesp/datasets/eswiki/src/eswiki-YYYYMMDD-pages-articles.xml``).

**4. Ejecutar el programa** ``/normalesp/datasets/eswiki/parsers/filter_out_tags.py``. Este programa genera como resultado el archivo ``/normalesp/datasets/eswiki/corpus/eswiki-corpus_preproc-step-0.txt``, el cual se utilizará como entrada en el siguiente paso; es por esto que, el archivo ``/normalesp/datasets/eswiki/corpus/eswiki-corpus.txt`` debería ser eliminado, pues no será más utilizado.

Por favor tenga en cuenta que este proceso tardará varios minutos.

**5. Ejecutar el programa** ``/normalesp/datasets/eswiki/parsers/parse_wikitext.py``. Este programa genera como resultado el archivo ``/normalesp/datasets/eswiki/corpus/eswiki-plaintext-corpus.txt``, el cual se utilizará como entrada en el siguiente paso; es por esto que, el archivo ``/normalesp/datasets/eswiki/corpus/eswiki-corpus_preproc-step-0.txt`` debería ser eliminado, pues no será más utilizado.

Por favor tenga en cuenta que este proceso tardará varias horas.

**6. Analizar morfológicamente el corpus de la Wikipedia y realizar etiquetado "Part-of-Speech".** Para llevar a cabo este proceso se utilizará la librería ``FreeLing``, la cual se instanciará en modo servidor con el fin de procesar las solicitudes sin reiniciar entre cada una de estas.

Antes de instanciar ``FreeLing``, el usuario debería revisar que las rutas y archivos de configuración relacionados en ``/normalesp/datasets/eswiki/parsers/analyzer.cfg`` existen.

Se procede entonces a instanciar ``Freeling`` en modo servidor, así::

    $ analyzer -f /normalesp/datasets/eswiki/parsers/analyzer.cfg --server --port 50005 &

A continuación, se ejecuta el programa ``/normalesp/datasets/eswiki/parsers/morpho_analysis.py``.

Una vez finalizada la ejecución de este programa, se generará el archivo ``/normalesp/datasets/eswiki/corpus/eswiki-tagged-plaintext-corpus.txt``, el cual se utilizará como entrada en el siguiente paso; por tal motivo, se sugiere eliminar el archivo ``/normalesp/datasets/eswiki/corpus/eswiki-plaintext-corpus.txt``.

Por favor tenga en cuenta que este proceso tardará varias horas.

**7. Ejecutar el programa** ``/normalesp/datasets/eswiki/parsers/build_corpus.py``. Este programa genera la versión final del corpus de la Wikipedia en español que se utilizará para estimar el modelo de lenguaje, a saber: ``/normalesp/datasets/eswiki/corpus/eswiki-corpus.txt``. Por lo anterior, se sugiere eliminar el archivo ``/normalesp/datasets/eswiki/corpus/eswiki-tagged-plaintext-corpus.txt``.

**8. Estimar un modelo de lenguaje del corpus de la Wikipedia en español.** Para estimar un modelo de lenguaje de *trigramas* (3-gramas) del corpus de la Wikipedia en español, se utilizará la herramienta ``kenlm``. Este proceso toma como entrada el corpus resultante del paso anterior, y genera un archivo en formato ``arpa``. A continuación se relaciona el comando para estimar el modelo de lenguaje, agregando que el archivo resultante se dispone en la ruta ``/normalesp/datasets/eswiki/corpora/``::

    $ bin/lmplz -o 3 -S 12G </normalesp/datasets/eswiki/corpus/eswiki-corpus.txt >/normalesp/datasets/eswiki/corpora/eswiki-corpus-3-grams.arpa

Tenga en cuenta que el parámetro ``-S`` sirve para especificar la cantidad de memoria que se utilizará. Como puede observarse, se han especificado 12G; sin embargo, el usuario puede modificar la cantidad de memoria a utilizar según su criterio.

**9. Convertir el modelo de lenguaje en un binario.** Un formato de archivo binario permite que el modelo de lenguaje se cargue más rápido, a la vez que reduce el tamaño de archivo.

::

    $ bin/build_binary /normalesp/datasets/eswiki/corpora/eswiki-corpus-3-grams.arpa /normalesp/datasets/eswiki/corpora/eswiki-corpus-3-grams.bin

Finalmente, se sugiere eliminar el archivo ``/normalesp/datasets/eswiki/corpora/eswiki-corpus-3-grams.arpa``, puesto que no se utilizará más.

2. Compilar los transductores de estado finito
==============================================

El objetivo de esta sección es describir cómo compilar los archivos fuentes de los transductores en archivos de formato binario, tal que estos últimos puedan ser utilizados por el programa principal de este proyecto. Con respecto a lo anterior, es importante mencionar que los directorios donde se disponen los archivos fuentes y los binarios son ``/normalesp/datasets/transducers/src/`` y ``/normalesp/datasets/transducers/bin/``, respectivamente. Habiendo dicho esto, a continuación se relaciona cómo compilar cada uno de los transductores de estado finito utilizando ``foma``, librería que se recomienda iniciar desde el directorio de los archivos fuentes.

**1.** ``es-dicc``

::

    $ cd /normalesp/datasets/transducers/src/
    $ /path/to/foma-0.9.18/foma
    read text es-dicc.txt
    save stack es-dicc.bin
    exit
    $ cp es-dicc.bin /normalesp/datasets/transducers/bin/

**2.** ``pnd-gazetteer``

::

    $ cd /normalesp/datasets/transducers/src/
    $ /path/to/foma-0.9.18/foma
    read text PND-gazetteer.txt
    save stack PND-Gazetteer.bin
    exit
    $ mv PND-Gazetteer.bin /normalesp/datasets/transducers/bin/

**3.** ``normalization_dicc``

::

    $ cd /normalesp/datasets/transducers/src/
    $ /path/to/foma-0.9.18/foma
    read spaced-text normalisation_dicc.txt
    save stack normalisation_dicc.bin
    exit

El archivo de formato binario no se moverá al directorio respectivo por tratarse de un temporal.

**4.** ``primary_variants``

::

    $ cd /normalesp/datasets/transducers/src/
    $ /path/to/foma-0.9.18/foma
    source primary_variants.foma
    exit
    $ mv primary_variants.bin /normalesp/datasets/transducers/bin/

**5.** ``dictionary_lookup``

::

    $ cd /normalesp/datasets/transducers/src/
    $ /path/to/foma-0.9.18/foma
    source dictionary_lookup.foma
    exit
    $ mv dictionary_lookup.bin /normalesp/datasets/transducers/bin/

**6.** ``phonology``

::

    $ cd /normalesp/datasets/transducers/src/
    $ /path/to/foma-0.9.18/foma
    source phonology.foma
    save stack phonology.bin
    exit
    $ cp phonology.bin /normalesp/datasets/transducers/bin/

**7.** ``secondary_variants-dicc``

::

    $ cd /normalesp/datasets/transducers/src/
    $ /path/to/foma-0.9.18/foma
    source secondary_variants.foma
    exit
    $ mv secondary_variants-Dicc.bin /normalesp/datasets/transducers/bin/

La compilación de este transductor requiere, por lo menos, 2.5G de memoria RAM. Sin embargo, el binario tan solo ocupará 165.5M de memoria RAM.

**8.** ``es-verbal-forms-fonemas``

::

    $ cd /normalesp/datasets/transducers/src/
    $ /path/to/foma-0.9.18/foma
    source es-verbal-forms-fonemas.foma
    save stack es-verbal-forms-fonemas.bin
    exit
    $ mv es-verbal-forms-fonemas.bin /normalesp/datasets/transducers/bin/

**9.** ``es-diminutives-fonemas``

::

    $ cd /normalesp/datasets/transducers/src/
    $ /path/to/foma-0.9.18/foma
    source es-diminutives-fonemas.foma
    save stack es-diminutives-fonemas.bin
    exit
    $ mv es-diminutives-fonemas.bin /normalesp/datasets/transducers/bin/

**10.** ``pnd-gazetteer-fonemas``

::

    $ cd /normalesp/datasets/transducers/src/
    $ /path/to/foma-0.9.18/foma
    source PND-gazetteer-fonemas.foma
    save stack PND-gazetteer-fonemas.bin
    exit
    $ mv PND-gazetteer-fonemas.bin /normalesp/datasets/transducers/bin/

**11.** ``pnd-gazetteer-lowercase``

::

    $ cd /normalesp/datasets/transducers/src/
    $ /path/to/foma-0.9.18/foma
    read text PND-gazetteer-lowercase.txt
    save stack PND-gazetteer-lowercase.bin
    exit

El archivo de formato binario no se moverá al directorio respectivo por tratarse de un temporal.

**12.** ``tertiary_variants-dicc`` y ``tertiary_variants-pnd``

::

    $ cd /normalesp/datasets/transducers/src/
    $ /path/to/foma-0.9.18/foma
    source tertiary_variants.foma
    exit
    $ mv tertiary_variants-Dicc.bin /normalesp/datasets/transducers/bin/
    $ mv tertiary_variants-PND.bin /normalesp/datasets/transducers/bin/

La compilación del transductor ``tertiary_variants-dicc`` requiere, por lo menos, 9G de memoria RAM. Sin embargo, el binario solo ocupará 1.3G de memoria RAM.

**13.** ``pnd-gazetteer-case``

::

    $ cd /normalesp/datasets/transducers/src/
    $ /path/to/foma-0.9.18/foma
    read spaced-text PND-gazetteer-CaSe.txt
    save stack PND-gazetteer-CaSe.bin
    exit
    $ mv PND-gazetteer-CaSe.bin /normalesp/datasets/transducers/bin/

**14.** ``iv-candidates-fonemas``

::

    $ cd /normalesp/datasets/transducers/src/
    $ /path/to/foma-0.9.18/foma
    source IV-candidates-fonemas.foma
    save stack IV-candidates-fonemas.bin
    exit
    $ mv IV-candidates-fonemas.bin /normalesp/datasets/transducers/bin/

**15.** ``split-words`` y ``other-changes``

Por favor comente las siguientes líneas del archivo ``/normalesp/datasets/transducers/src/tertiary_variants.foma``, agregando el caracter ``#`` al inicio de cada una de estas::

    # Variantes terciarias del diccionario estándar:
    regex TertiaryBase1Transducer .o. StandardDicc;
    save stack tertiary_variants-Dicc.bin

    clear

    regex TertiaryBase3Transducer .o. PNDGazetteer;
    save stack tertiary_variants-PND.bin

Por lo tanto, una vez comentadas las líneas, el código debería verse así::

    # Variantes terciarias del diccionario estándar:
    # regex TertiaryBase1Transducer .o. StandardDicc;
    # save stack tertiary_variants-Dicc.bin

    # clear

    # regex TertiaryBase3Transducer .o. PNDGazetteer;
    # save stack tertiary_variants-PND.bin

Habiendo dicho esto, se proceden a compilar los archivo fuentes.

::

    $ cd /normalesp/datasets/transducers/src/
    $ /path/to/foma-0.9.18/foma
    source split-words.foma
    clear
    regex OtherChanges;
    save stack other-changes.bin
    exit
    $ mv split-words.bin /normalesp/datasets/transducers/bin/
    $ mv other-changes.bin /normalesp/datasets/transducers/bin/

Finalmente, descomente las líneas modificadas del archivo ``/normalesp/datasets/transducers/src/tertiary_variants.foma``. El archivo entonces debería verse así::

    # Variantes terciarias del diccionario estándar:
    regex TertiaryBase1Transducer .o. StandardDicc;
    save stack tertiary_variants-Dicc.bin

    clear

    regex TertiaryBase3Transducer .o. PNDGazetteer;
    save stack tertiary_variants-PND.bin

**16.** ``length_normalisation`` y ``length_normalisation-2``

::

    $ cd /normalesp/datasets/transducers/src/
    $ /path/to/foma-0.9.18/foma
    source lengthening_normalisation.foma
    regex LengtheningNormalisation;
    save stack length_normalisation.bin
    clear
    regex LengtheningNormalisation2;
    save stack length_normalisation-2.bin
    exit
    $ mv length_normalisation.bin /normalesp/datasets/transducers/bin/
    $ mv length_normalisation-2.bin /normalesp/datasets/transducers/bin/

**17.** ``remove_enclitic``, ``accentuate_enclitic`` y ``remove_mente``

::

    $ cd /normalesp/datasets/transducers/src/
    $ /path/to/foma-0.9.18/foma
    source affix_check.foma
    regex RemoveEnclitic;
    save stack remove_enclitic.bin
    clear
    regex AccentuateEnclitic;
    save stack accentuate_enclitic.bin
    clear
    regex RemoveMente;
    save stack remove_mente.bin
    exit
    $ mv remove_enclitic.bin /normalesp/datasets/transducers/bin/
    $ mv accentuate_enclitic.bin /normalesp/datasets/transducers/bin/
    $ mv remove_mente.bin /normalesp/datasets/transducers/bin/

Por último, se procede a eliminar los archivos de formato binario temporales en el directorio ``/normalesp/datasets/transducers/src/``, a saber:

- ``/normalesp/datasets/transducers/src/es-dicc.bin``.
- ``/normalesp/datasets/transducers/src/normalisation_dicc.bin``.
- ``/normalesp/datasets/transducers/src/phonology.bin``.
- ``/normalesp/datasets/transducers/src/PND-gazetteer-lowercase.bin``.

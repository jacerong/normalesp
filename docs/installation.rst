0. Preliminary
==============

The installation this document guides was carried out on a ``Debian 8 "jessie"`` system, reason why the command line instructions correspond to the syntax of this operating system.

This project uses the following third-party libraries / tools, and their installation is suggested before proceeding with this document:

- **FreeLing 4.0** [http://nlp.lsi.upc.edu/freeling/node/1].
- **kenlm** [https://kheafield.com/code/kenlm/].
- **foma** [https://fomafst.github.io/].

How to install such third-party libraries / tools is outside the scope of this document. For this reason, please make sure each installation be successful.

0.1 System Requirements
-----------------------

Installation
    12G of available RAM.

Usage
    4G of available RAM.

0.2 Python Dependencies
-----------------------

This project requires ``Python 2.7``.

The modules as listed in the ``/requirements.txt`` file.

1. Estimating a Language Model from the Spanish Wikipedia Corpus
================================================================

Throughout this section how to estimate a **3-gram** language model from the Spanish Wikipedia corpus is described. This process goes from downloading a backup of the Spanish Wikipedia, which can be the most recent one, to estimating a **3-gram** language model. So, with no more preamble, let's start:

**0. Install** ``ruby``. This is achieved by the following command: ``$ sudo apt-get install ruby``.

According to the ``Corpuspedia`` documentation [http://gramatica.usc.es/pln/tools/CorpusPedia.html], a third-party library that will be used to create the first approximation of the Spanish Wikipedia corpus, the required version of ``ruby`` is the ``1.9.1`` one. However, such a version is not available in the official ``Debian 8 "jessie"`` repository, which is why the ``2.1.5`` one will be used.

**1. Download a backup of the Spanish Wikipedia**. To do that, enter the ``https://dumps.wikimedia.org/eswiki/`` URL, choose a recent date, and download the ``eswiki-YYYYMMDD-pages-articles.xml.bz2`` file. This download will take a while because several Gigabytes are being retrieved. Finally, move the downloaded file to the ``/normalesp/datasets/eswiki/src/`` path, and decompress it.

**2. Create a corpus from the Spanish Wikipedia**. Change directory to ``/normalesp/datasets/eswiki/CorpusPedia_alfa/``, and type the following command: ``ruby corpuspedia.rb -c -lang:es``. This process, which can take several minutes or even hours, will create as a result the ``/normalesp/datasets/eswiki/corpus/eswiki-corpus.txt`` file. This file is just a first approximation of the corpus that will be used to estimate the language model.

Because ``CorpuesPedia`` creates the following directories and files that will not be used to estimate the language model, these can be deleted.

- ``/normalesp/datasets/eswiki/comparable/``.
- ``/normalesp/datasets/eswiki/data/``.
- ``/normalesp/datasets/eswiki/log/``.
- ``/normalesp/datasets/eswiki/ontology/``.

In the same way, the downloaded file and its uncompressed version can be deleted (``/normalesp/datasets/eswiki/src/eswiki-YYYYMMDD-pages-articles.xml``).

**3. Run the** ``/normalesp/datasets/eswiki/parsers/filter_out_tags.py`` **program**. This Python program creates as a result the ``/normalesp/datasets/eswiki/corpus/eswiki-corpus_preproc-step-0.txt`` file, which will be used as input in the next step; because of this, the ``/normalesp/datasets/eswiki/corpus/eswiki-corpus.txt`` file can be deleted, taking into account it will not be used anymore.

*This process may take several minutes to complete*.

**4. Run the** ``/normalesp/datasets/eswiki/parsers/parse_wikitext.py`` **program**. This Python program creates as a result the ``/normalesp/datasets/eswiki/corpus/eswiki-plaintext-corpus.txt`` file, which will be used as input in the next step; because of this, the ``/normalesp/datasets/eswiki/corpus/eswiki-corpus_preproc-step-0.txt`` file can be deleted, taking into account it will not be used anymore.

*This process may take several hours to complete*.

**5. Morphologically analyze the Spanish Wikipedia corpus and perform its Part-of-Speech tagging**. The morphological analysis and the Part-of-Speech tagging will be performed by using the ``FreeLing`` tool.

Before initiating ``FreeLing``, the user should check if the paths and config files defined in the ``/normalesp/datasets/eswiki/parsers/analyzer.cfg`` file do exist.

Type then the following command to initiate ``FreeLing`` in Client/Server mode::

    $ analyzer -f /normalesp/datasets/eswiki/parsers/analyzer.cfg --server --port 50005 &

Next, run the ``/normalesp/datasets/eswiki/parsers/morpho_analysis.py`` program. This Python program creates as a result the ``/normalesp/datasets/eswiki/corpus/eswiki-tagged-plaintext-corpus.txt`` file, which will be used as input in the next step; because of this, the ``/normalesp/datasets/eswiki/corpus/eswiki-plaintext-corpus.txt`` file can be deleted, taking into account it will not be used anymore.

*This process may take several hours to complete*.

**6. Run the** ``/normalesp/datasets/eswiki/parsers/build_corpus.py`` **program**. This Python program creates as a result the ``/normalesp/datasets/eswiki/corpus/eswiki-corpus.txt`` file, which will be used to estimate the language model; because of this, the ``/normalesp/datasets/eswiki/corpus/eswiki-tagged-plaintext-corpus.txt`` file can be deleted, taking into account it will not be used anymore.

**7. Estimate a language model from the Spanish Wikipedia corpus**. The ``kenlm`` tool will be used to estimate a 3-gram language model from the Spanish Wikipedia corpus. This process receives as input the file created in the previous step, and creates as a result a file in ``arpa`` format.  Having said the above, the following command allows to estimate the language model::

    $ bin/lmplz -o 3 -S 12G </normalesp/datasets/eswiki/corpus/eswiki-corpus.txt >/normalesp/datasets/eswiki/corpora/eswiki-corpus-3-grams.arpa

Take into account that the resulting file will be put in the ``/normalesp/datasets/eswiki/corpora/`` path. Moreover, 12G of memory are used to estimate the language model as it is specified through the ``-S`` parameter; however, the user can modify this parameter according to its availability of RAM.

**8. Convert the language model into a binary file**. A binary file allows to load the language model faster, while reducing its file size.

::

    $ bin/build_binary /normalesp/datasets/eswiki/corpora/eswiki-corpus-3-grams.arpa /normalesp/datasets/eswiki/corpora/eswiki-corpus-3-grams.bin

Finally, the ``/normalesp/datasets/eswiki/corpora/eswiki-corpus-3-grams.arpa`` file can be deleted, taking into account it will not be used anymore.

2. Compilation of Finite-State Transducers
==========================================

In this section how to compile source files into finite-state transducers saved as binary files, such that the latter can be used by the main program of this project, is described. Regarding this, the former and the latter are in the ``/normalesp/datasets/transducers/src/`` and ``/normalesp/datasets/transducers/bin/`` directories, respectively. On the other hand, the ``foma`` library will be used for compilation of finite-state transducers; this library should be initiated from the source file directory.

**1.** ``es-dicc``

::

    $ cd /normalesp/datasets/transducers/src/
    $ /path/to/foma-0.9.18/foma
    read text es-dicc.txt
    save stack es-dicc.bin
    exit
    $ mv es-dicc.bin /normalesp/datasets/transducers/bin/

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

The resulting binary file should not moved to the binary file directory because the former is a temporary file.

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

In order to compile this transducer 2.5G of available RAM are required. However, the binary file will require 165.5M of available RAM.

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

The resulting binary file should not moved to the binary file directory because the former is a temporary file.

**12.** ``tertiary_variants-dicc`` and ``tertiary_variants-pnd``

::

    $ cd /normalesp/datasets/transducers/src/
    $ /path/to/foma-0.9.18/foma
    source tertiary_variants.foma
    exit
    $ mv tertiary_variants-Dicc.bin /normalesp/datasets/transducers/bin/
    $ mv tertiary_variants-PND.bin /normalesp/datasets/transducers/bin/

In order to compile the ``tertiary_variants-dicc`` transducer 9G of available RAM are required. However, the binary file will require 1.3G of available RAM.

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

**15.** ``split-words`` and ``other-changes``

First of all, comment out the following lines in the ``/normalesp/datasets/transducers/src/tertiary_variants.foma`` file, adding the ``#`` character to the start of them::

    # Variantes terciarias del diccionario estándar:
    regex TertiaryBase1Transducer .o. StandardDicc;
    save stack tertiary_variants-Dicc.bin

    clear

    regex TertiaryBase3Transducer .o. PNDGazetteer;
    save stack tertiary_variants-PND.bin

Therefore, once the lines have been commented out, they should look like as follow::

    # Variantes terciarias del diccionario estándar:
    # regex TertiaryBase1Transducer .o. StandardDicc;
    # save stack tertiary_variants-Dicc.bin

    # clear

    # regex TertiaryBase3Transducer .o. PNDGazetteer;
    # save stack tertiary_variants-PND.bin

Next, compilation of finite-state transducers is proceeded.

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

Finally, uncomment the modified lines in the ``/normalesp/datasets/transducers/src/tertiary_variants.foma`` file. The latter should look like as follow::

    # Variantes terciarias del diccionario estándar:
    regex TertiaryBase1Transducer .o. StandardDicc;
    save stack tertiary_variants-Dicc.bin

    clear

    regex TertiaryBase3Transducer .o. PNDGazetteer;
    save stack tertiary_variants-PND.bin

**16.** ``length_normalisation`` and ``length_normalisation-2``

::

    $ cd /normalesp/datasets/transducers/src/
    $ /path/to/foma-0.9.18/foma
    regex LengtheningNormalisation;
    save stack length_normalisation.bin
    clear
    regex LengtheningNormalisation2;
    save stack length_normalisation-2.bin
    exit
    $ mv length_normalisation.bin /normalesp/datasets/transducers/bin/
    $ mv length_normalisation-2.bin /normalesp/datasets/transducers/bin/

**17.** ``remove_enclitic``, ``accentuate_enclitic``, and ``remove_mente``

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

As a final point, the following temporary files in the ``/normalesp/datasets/transducers/src/`` directory should be deleted:

- ``/normalesp/datasets/transducers/src/es-dicc.bin``.
- ``/normalesp/datasets/transducers/src/normalisation_dicc.bin``.
- ``/normalesp/datasets/transducers/src/phonology.bin``.
- ``/normalesp/datasets/transducers/src/PND-gazetteer-lowercase.bin``.

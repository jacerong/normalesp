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

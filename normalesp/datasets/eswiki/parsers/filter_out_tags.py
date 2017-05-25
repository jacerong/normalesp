# -*- coding: iso-8859-1 -*-

'''
Filtra etiquetas del corpus que no son requeridas.

La estructura de cada artículo de Wikipedia en el corpus procesado por corpuspedia es:
<article>
    <title></title>
    <category></category>
    <related></related>
    <links></links>
    <translations></translations>
    <plaintext></plaintext>
    <wikitext></wikitext>
</article>

De la estructura se depurarán las siguientes etiquetas:
    related, links, translations y plaintext.
'''

import os, re


CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
CORPUSPEDIA_PATH = '/'.join(CURRENT_PATH.split('/')[:-1])


def write_filtered_corpus(line):
    '''Escribe nuevamente el corpus pero sin las etiquetas innecesarias.'''
    fname = CORPUSPEDIA_PATH + '/corpus/eswiki-corpus_preproc-step-0.txt'
    with open(fname, 'a') as foutput:
        foutput.write(line)

def filter_out_unneeded_tag():
    """Filtra etiquetas no requeridas en la construcción del corpus final."""
    fname = CORPUSPEDIA_PATH + '/corpus/eswiki-corpus.txt'
    with open(fname) as finput:
        for line in finput:
            if not re.match(r"\t<(?:related|links|translations|plaintext)>", line, re.I):
                write_filtered_corpus(line)


if __name__ == '__main__':
    filter_out_unneeded_tag()

# -*- coding: iso-8859-15 -*-

'''Lee el corpus '../corpus/eswiki-tagged-plaintext-corpus.txt' (en estructura xml)
y extrae el contenido de la etiqueta 'tagged_plaintext' (por artículo), para crear
un único archivo de texto plano que sirva para construir el modelo de lenguaje de
n-gramas y los demás recursos previstos.
'''

import os, re


CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
CORPUSPEDIA_PATH = '/'.join(CURRENT_PATH.split('/')[:-1])


def write_in_file(fname, line):
    with open(fname, 'a') as f:
        f.write(line)


def merge_wikipedia_articles():
    fname_input  = CORPUSPEDIA_PATH + '/corpus/eswiki-tagged-plaintext-corpus.txt'
    fname_output = CORPUSPEDIA_PATH + '/corpus/eswiki-corpus.txt'

    plaintext = ''
    is_plaintext_tag_open = False
    with open(fname_input) as finput:
        for line in finput:
            if re.match(r'\t<tagged_plaintext>', line):
                is_plaintext_tag_open = True
                plaintext = line
            elif re.search(r'</tagged_plaintext>\n$', line):
                plaintext += line
                is_plaintext_tag_open = False
                if isinstance(plaintext, str):
                    plaintext = plaintext.decode('utf-8')
                # remover etiqueta y escribir contenido del artículo
                plaintext = re.sub(
                    r'^\t<tagged_plaintext>(.+)</tagged_plaintext>\n$',
                    r'\1', plaintext, flags=re.I|re.M|re.S)
                # unir contracciones gramaticales separadas por Freeling
                plaintext = re.sub(
                    r'(?:(?<!\w)de) (?:el(?!\w))', 'del',
                    plaintext, flags=re.U|re.M)
                plaintext = re.sub(
                    r'(?:(?<!\w)a) (?:el(?!\w))', 'al',
                    plaintext, flags=re.U|re.M)
                # escribir en fichero de corpus
                write_in_file(fname_output, plaintext.encode('utf-8') + '\n')
            elif is_plaintext_tag_open:
                plaintext += line


if __name__ == '__main__':
    merge_wikipedia_articles()

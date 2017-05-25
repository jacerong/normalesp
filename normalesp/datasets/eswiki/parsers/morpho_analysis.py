# -*- coding: iso-8859-15 -*-

'''
Tokenización, separación de sentencias, análisis morfológico y etiquetamiento de
texto de los artículos de Wikipedia. El resultado de este proceso servirá para
construir un modelo de lenguaje de n-gramas.
'''

import os, re, subprocess

import numpy as np


CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
CORPUSPEDIA_PATH = '/'.join(CURRENT_PATH.split('/')[:-1])


def analyze_morphologically_and_pos_tagging(plaintext):
    '''Analizar morfologicamente el texto y etiquetarlo P-o-S.

    Una vez se obtiene el resultado de Freeling, se lleva a cabo el sig. proceso:
        1. Se descartan algunos P-o-S tags: signos de puntuación, (parcialmente)
           fecha y números. Además, se remueve cualquier caracter que no sea una
           letra del alfabeto.
        2. Con excepción de los nombres propios, los tokens son convertidos a minúscula.
        3. Los nombres propios se escriben en un gazetteer de estos.
    '''
    fname_proper_nouns  = CORPUSPEDIA_PATH + '/corpus/proper-nouns.dat'

    # remover etiqueta 'plaintext'
    plaintext = re.sub(r'^\t<plaintext>(.+)</plaintext>\n$', r'\1', plaintext,
        flags=re.S)

    random_number = np.random.randint(0, 1000)
    # crear un archivo de texto plano con el contenido recibido
    with open('%s/tmp/article-%i.txt' % (CURRENT_PATH, random_number), 'w') as finput:
        finput.write(plaintext)
    # ejecutar Freeling
    process = subprocess.call(['analyzer_client', '50005'],
        stdin=open('%s/tmp/article-%i.txt' % (CURRENT_PATH, random_number)),
        stdout=open('%s/tmp/article-%i.tagger' % (CURRENT_PATH, random_number), 'w'))

    if process != 0:
        return None

    final_text = ''
    with open('%s/tmp/article-%i.tagger' % (CURRENT_PATH, random_number)) as foutput:
        for line in foutput:
            # verificar si se trata del fin de una sentencia
            line = line.rstrip('\n')
            if len(line) == 0:
                final_text += '\n'
                continue
            try:
                word, lemma, tag, prob = line.split(' ')
                if isinstance(word, str):
                    word = word.decode('utf-8')
            except:
                continue
            else:
                if tag.startswith('F'):
                    # remover signos de puntuación
                    continue
                if tag.startswith(('Z', 'W')):
                    # remover cualquier caracter que no pertenezca al alfabeto
                    word = re.sub(u"""[^a-zu\xe1u\xe9u\xedu\xf3u\xfau\xf1_]""", '',
                        word, flags=re.I|re.U)
                    if len(word) <= 1:
                        continue
                # convertir a minúscula la palabra, con excepción de Nombres Propios
                if not tag.startswith('NP'):
                    word = word.lower()
                else:
                    """Deshabilitada la creación de lista base de nombres propios.
                    write_in_corpus(
                        fname_proper_nouns,
                        word.replace('_', ' ').encode('utf-8') + '\n')"""
                    pass
                final_text += word.replace('_', ' ').encode('utf-8') + ' '
    final_text = final_text.decode('utf-8')
    # NOTA: debido a un error de FreeLing, cuando asume abreviatura, las
    # sentencias no son correctamente separadas. Por ej.:
    # "altitud media de 1996 metros sobre el nivel del mar. Limita:"
    # Asume que "mar." es la abreviatura de marzo, y por lo tanto devuelve el
    # token mismo. Además, que "Limita" es un nombre propio.
    # Por lo tanto, para solucionar parcialmente esta situación, se define
    # la siguiente expresión regular.
    final_text = re.sub(u"""([\w]+)\.(?: +)([A-Zu\xc1u\xc9u\xcdu\xd3u\xdau\xd1])""",
        r'\1\n\2', final_text, flags=re.U)
    # remover saltos de linea contiguos (> 1), y espacios al final de línea
    final_text = re.sub(r'[\n]{2,}', '\n', final_text)
    final_text = re.sub(r'[ ]{2,}', ' ', final_text)
    final_text = re.sub(r'(?:[ ]+)\n$', '\n', final_text, flags=re.M)
    final_text = final_text.rstrip('\n')

    # eliminar archivos utilizados
    os.remove('%s/tmp/article-%i.txt' % (CURRENT_PATH, random_number))
    os.remove('%s/tmp/article-%i.tagger' % (CURRENT_PATH, random_number))

    return final_text.encode('utf-8')


def write_in_corpus(fname, line):
    with open(fname, 'a') as foutput:
        foutput.write(line)


def main():
    fname_input  = CORPUSPEDIA_PATH + '/corpus/eswiki-plaintext-corpus.txt'
    fname_output = CORPUSPEDIA_PATH + '/corpus/eswiki-tagged-plaintext-corpus.txt'
    fname_log = CURRENT_PATH + '/tmp/log'

    # crear el directorio "tmp" si no existe
    temp_path = CURRENT_PATH + '/tmp/'
    if not os.path.isdir(temp_path):
        os.mkdir(temp_path)

    article_title = ''
    plaintext = ''
    plaintext_tag_is_open = False
    with open(fname_input) as finput:
        for line in finput:
            if re.match(r"\t<plaintext>", line):
                plaintext = line
                plaintext_tag_is_open = True
            elif re.search(r"</plaintext>\n$", line):
                plaintext += line
                tagged_plaintext = analyze_morphologically_and_pos_tagging(
                    plaintext)
                if tagged_plaintext is None:
                    tagged_plaintext = ''
                    write_in_corpus(fname_log,
                        'Error procesando artículo: "%s"\n' % article_title)
                tagged_plaintext = '\t<tagged_plaintext>' + tagged_plaintext +\
                                   '</tagged_plaintext>\n'
                write_in_corpus(fname_output, tagged_plaintext)
                plaintext_tag_is_open = False
            elif not plaintext_tag_is_open:
                write_in_corpus(fname_output, line)
                match_title = re.match(r'\t<title>(.+?)</title>$', line)
                if match_title:
                    article_title = match_title.group(1)
            else:
                plaintext += line


if __name__ == '__main__':
    main()

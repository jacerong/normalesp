# -*- coding: iso-8859-15 -*-

'''
Analizar gramaticalmente el tag 'wikitext' y convertir su contenido en text plano.
'''

import os, re


CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
CORPUSPEDIA_PATH = '/'.join(CURRENT_PATH.split('/')[:-1])


def parse_wikitext(wikitext):
    """Analiza gramaticalmente contenido y convierte en texto plano.

    Remove wiki mark up"""
    # eliminar el caracter de salto de línea y remover tag wikitext
    plaintext = re.sub(
        r'^(?:\t<wikitext>)(.+)(?:</wikitext>\n)$', r'\1', wikitext,
        flags=re.I|re.M|re.S)

    # remover comentarios HTML y "void"
    plaintext = re.sub(r'<!--.*?-->', '', plaintext, flags=re.I|re.M|re.S)
    plaintext = re.sub(r'{{(?:void|\^)\|.*?}}', '', plaintext,
        flags=re.I|re.M|re.S)

    # tratamiento de títulos de secciones (SIN CAMBIOS PARA ESPAÑOL)
    plaintext = re.sub(r'^(?:[=]{2,})([^=]+)(?:[=]{2,})', r'\1:',
        plaintext, flags=re.M)
    plaintext = re.sub(r'<h[1-6](?:[^>]*?)>(.*?)</h[1-6]>', r'\1:', plaintext,
        flags=re.I|re.M|re.S)

    # reeemplazar regla horizontal por salto de línea (SIN CAMBIOS PARA ESPAÑOL)
    plaintext = re.sub(r'([-]{4,})', '\n', plaintext)
    plaintext = re.sub(r'<hr(?:[^>]*?)>', '\n', plaintext, flags=re.I)

    # remover TOC's (SIN CAMBIOS PARA ESPAÑOL)
    plaintext = re.sub(r'__(?:FORCE|NO)?TOC__', '', plaintext)
    plaintext = re.sub(
        r'{{(?:Horizontal )?TOC(?: (?:limit|right|left))?(?:\|[0-9]{1,})?}}',
        '', plaintext, flags=re.I)
    plaintext = re.sub(
        r'{{TOC(?: )(?:right|left)\|limit=[0-9]{1,}}}', '', plaintext,
        flags=re.I)

    # homologar saltos de linea y espacios (CAMBIOS ESPAÑOL)
    plaintext = re.sub(r'{{(?:break|salto)(?:\|[0-9]{1,})?}}', '\n', plaintext,
        flags=re.I)
    plaintext = re.sub(r'<br(?: ?/)?>', '\n', plaintext, flags=re.I)
    plaintext = re.sub(r'&nbsp;', ' ', plaintext, flags=re.I)
    plaintext = re.sub(r'{{(?:spaces|pad)(?:.*?)}}', ' ', plaintext, flags=re.I)

    # remover 'clear' (CAMBIOS ESPAÑOL)
    plaintext = re.sub(
        r'{{(?:-|(?:saltobloque|clr|(?:(?:subst\:)?clear))(?:(?: |\|)(?:left|right))?)}}',
        '\n', plaintext, flags=re.I)

    # remover tablas (SIN CAMBIOS PARA ESPAÑOL)
    plaintext = re.sub(r'{\|.*?\|}', '', plaintext, flags=re.I|re.M|re.S)
    plaintext = re.sub(r'<table(?:[^>]*?)>.*?</table>', '', plaintext, 
        flags=re.I|re.M|re.S)

    # tratamiento de indentation y 'outdent' (CAMBIOS ESPAÑOL)
    plaintext = re.sub(r'^[:]+(.*)', r'\1', plaintext, flags=re.I|re.M)
    plaintext = re.sub(r'{{indent(.*?)}}', '', plaintext, flags=re.I)
    plaintext = re.sub(
        r'{{(?:(?:(?:outdent|od)2?)|(?:(?:(?:quit|retir)(?:o|ar) sangría)|qs)).*?}}',
        '', plaintext, flags=re.I)

    ############################
    # Inicio: Formato de texto #
    ############################

    # tratamiento de italics y bold
    plaintext = re.sub(r'(?:[\']{2,})(.*?)(?:[\']{2,})', r'\1', plaintext)

    # tratamiento de *caps (CAMBIOS ESPAÑOL)
    plaintext = re.sub(
        r'{{(?:(?:(?:(?:small|all|no|fix)caps)(?: all)?)|sc|sm|aut|versalita)\|(.*?)}}',
        r'\1', plaintext, flags=re.I)

    # tratamiento de etiqueta HTML small y big
    plaintext = re.sub(r'<(?:small|big)(?:[^>]*?)>(.*?)</(?:small|big)>',
        r'\1', plaintext, flags=re.I|re.M|re.S)

    # eliminar etiqueta HTML 'code', 'syntaxhighlight' y 'source'
    plaintext = re.sub(
        r'<(?:code|syntaxhighlight|source)(?:[^>]*?)>(?:.*?)</(?:code|syntaxhighlight|source)>',
        '', plaintext, flags=re.I|re.M|re.S)

    # tratamiento de nowrap
    plaintext = re.sub(r'{{(?:nowrap|nobr|nobreak)\|(.*?)}}', r'\1', plaintext,
        flags=re.I)

    # reemplazos de entidades HTML
    # http://stackoverflow.com/questions/6116978/
    html_entities = {
        "&Agrave;": "À", "&Aacute;": "Á", "&Acirc;": "A", "&Atilde;": "A",
        "&Auml;": "A", "&Aring;": "A", "&Ccedil;": "Ç", "&Egrave;": "È",
        "&Eacute;": "É", "&Ecirc;": "E", "&Euml;": "E", "&Igrave;": "Ì",
        "&Iacute;": "Í", "&Icirc;": "I", "&Iuml;": "I", "&Ntilde;": "Ñ",
        "&Ograve;": "Ò", "&Oacute;": "Ó", "&Ocirc;": "O", "&Otilde;": "O",
        "&Ouml;": "O", "&Oslash;": "O", "&Ugrave;": "Ù", "&Uacute;": "Ú",
        "&Ucirc;": "U", "&Uuml;": "U", "&agrave;": "à", "&aacute;": "á",
        "&acirc;": "a", "&atilde;": "a", "&auml;": "a", "&aring;": "a",
        "&aelig;": "a", "&ccedil;": "ç", "&egrave;": "è", "&eacute;": "é",
        "&ecirc;": "e", "&euml;": "e", "&igrave;": "ì", "&iacute;": "í",
        "&icirc;": "i", "&iuml;": "i", "&ntilde;": "ñ", "&ograve;": "ò",
        "&oacute;": "ó", "&ocirc;": "o", "&otilde;": "o", "&ouml;": "o",
        "&oslash;": "o", "&oelig;": "", "&ugrave;": "ù", "&uacute;": "ú",
        "&ucirc;": "u", "&uuml;": "u", "&iquest;": "¿", "&iexcl;": "¡",
        "&ndash;": "-", "&mdash;": "-", "&lsaquo;": "<", "&rsaquo;": ">",
        "&laquo;": "<", "&raquo;": ">", "&lsquo;": "'", "&rsquo;": "'",
        "&ldquo;": '"', "&rdquo;": '"', "&apos;": "'", "&quot;": '"',
    }
    rep = dict((re.escape(k), v) for k, v in html_entities.iteritems())
    pattern = re.compile("|".join(rep.keys()))
    plaintext = pattern.sub(lambda m: rep[re.escape(m.group(0))], plaintext)

    # remover entidades HTML
    plaintext = re.sub(r'&[^\s;]+;', '', plaintext)
    plaintext = re.sub(r'<hiero(?:[^>]*?)>(?:.+?)</hiero>', '', plaintext,
        flags=re.I)

    # tratamiento de superíndices y subíndices
    plaintext = re.sub(r'<(?:sup|sub)(?:[^>]*?)>(.*?)</(?:sup|sub)>', r'\1',
        plaintext, flags=re.I)

    # remover 'math' tag y template
    plaintext = re.sub(r'<math(?:[^>]*?)>(?:.*?)</math>', '', plaintext,
        flags=re.I|re.M|re.S)
    plaintext = re.sub(r'{{math(?:.*?)}}', '', plaintext, flags=re.I|re.M|re.S)

    # tratamiento de pre y nowiki
    plaintext = re.sub(r'<(?:pre|nowiki)(?:[^>]*?)>(?:.+?)</(?:pre|nowiki)>', '',
        plaintext, flags=re.I|re.M|re.S)
    plaintext = re.sub(r'<nowiki(?:[ ]*?)/>', '', plaintext, flags=re.I)

    # tratamiento de include
    plaintext = re.sub(
        r'<(?:noinclude|onlyinclude|includeonly)(?:[^>]*?)>(.*?)</(?:noinclude|onlyinclude|includeonly)>',
        r'\1', plaintext, flags=re.I|re.M|re.S)

    # remover firma
    plaintext = re.sub(r'[\~]{3,}', '', plaintext)

    #########################
    # Fin: Formato de texto #
    #########################

    #######################
    # Referencias y Citas #
    #######################

    # remover footnotes
    plaintext = re.sub(r'<ref(?:erences?)?(?:[^>]*?)/>', ' ', plaintext, flags=re.I)
    plaintext = re.sub(r'<ref(?:[^>]*?)>(?:.*?)</ref>', '', plaintext,
        flags=re.I|re.M|re.S)

    # remover lista de referencia template (CAMBIOS ESPAÑOL)
    plaintext = re.sub(r'{{(?:reflist|listaref|refn|notelist)(?:.+?)}}', '',
        plaintext, flags=re.I|re.M|re.S)
    plaintext = re.sub(r'{{refbegin(?:.*?)}}(?:.*?){{refend}}', '', plaintext,
        flags=re.I|re.M|re.S)

    # remover citas bibliogŕaficas (CAMBIOS ESPAÑOL)
    plaintext = re.sub(r'{{(?:cita|cite) (?:[^|]+?)\|(?:.+?)}}', '',
        plaintext, flags=re.I)

    ########################
    # Inicio: Links y URLs #
    ########################

    # remover anchor o ancla (CAMBIOS ESPAÑOL)
    plaintext = re.sub(r'{{(?:anchor|(?:(?:ancla)r?))(?:.*?)}}', '', plaintext,
        flags=re.I)

    # link externo
    plaintext = re.sub(r'\[(?:https?|mailto|irc|ftps?|news|gopher)\:(?:[^ ]+?)\]',
        '', plaintext, flags=re.I)
    # link externo con texto
    plaintext = re.sub(r'\[(?:https?|mailto|irc|ftps?|news|gopher)\:(?:[^ ]+?) (.+?)\]',
        r'\1', plaintext, flags=re.I)
    # link externo 'suelto'
    plaintext = re.sub(r'(?:https?|mailto|irc|ftps?|news|gopher)\:[^ ]+',
        '', plaintext, flags=re.I)

    # link a wikimedia
    plaintext = re.sub(r'\[//(?:.*?)\]', '', plaintext)

    # interlanguage link
    plaintext = re.sub(r'\[\[(?:en|fr|de|it|pt|es)\:(.+?)\]\]', r'\1', plaintext)
    plaintext = re.sub(r'\[\[(?:[a-z]{2})\:(?:.+?)\]\]', r'', plaintext)

    # tratamiento de categorías
    plaintext = re.sub(r'{{ORDENAR(?:.*?)}}', '', plaintext, flags=re.I)
    plaintext = re.sub(r'\[\[(?:Category|Categoría)(?:.*?)\]\]',
        r'', plaintext, flags=re.I)
    plaintext = re.sub(r'\[\[\:(?:Category|Categoría):([^|\]]+?)\|?\]\]', r'\1',
        plaintext, flags=re.I)

    # link interno
    plaintext = re.sub(
        r'(?:(?:\[\[)(?!\:?File\:|\:?Archivo\:|\:?Media\:))([^|\]]+?)\|?\]\]',
        r'\1', plaintext, flags=re.I)
    # link interno con texto
    plaintext = re.sub(
        r'(?:(?:\[\[)(?!\:?File\:|\:?Archivo\:|\:?Media\:))(?:[^\]]+?)\|(.+?)\]\]',
        r'\1', plaintext, flags=re.I)

    # remover link de edición
    plaintext = re.sub(r'{{edit(?:.*?)}}', '', plaintext, flags=re.I)

    # remover redirectes
    plaintext = re.sub(r'^#redirect(?:.+)', '', plaintext, flags=re.I|re.M)    

    #####################
    # Fin: Links y URLs #
    #####################

    ###########################################
    # Inicio: Archivos, imágenes y multimedia #
    ###########################################

    # remover template de archivo (CAMBIOS ESPAÑOL)
    plaintext = re.sub(r'\[\[\:?(?:Image|File|Archivo|Media):(.*?)\]\]', '',
        plaintext, flags=re.I)

    # remover imagen múltiple (CAMBIOS ESPAÑOL)
    plaintext = re.sub(r'{{(?:(?:(?:multiple|auto) image)|(?:imagen múltiple))(?:.*?)}}',
        '', plaintext, flags=re.I|re.M|re.S)

    # remover galería, panorámicas e image map(CAMBIOS ESPAÑOL)
    plaintext = re.sub('<(?:gallery|imagemap)(?:[^>]*?)>(?:.+?)</(?:gallery|imagemap)>',
        '', plaintext, flags=re.I|re.M|re.S)
    plaintext = re.sub(
        r'{{(?:Gallery|(?:Galería de imágenes)|panorama|(?:Wide image))(?:.+?)}}',
        '', plaintext, flags=re.I|re.M|re.S)

    # remover multimedia externa (CAMBIOS ESPAÑOL)
    plaintext = re.sub(r'{{ (?:(?:external media)|(?:multimedia externa))(?:.*?)}}',
        '', plaintext, flags=re.I|re.M|re.S)

    # remover otros templaes
    plaintext = re.sub(r'{{(?:Photomontage|(?:Image frame)|(?:image array))(?:.*?)}}',
        '', plaintext, flags=re.I|re.M|re.S)

    ########################################
    # Fin: Archivos, imágenes y multimedia #
    ########################################

    # tratamiento de (font)color
    plaintext = re.sub(
        r'{{(?:font )?color\|(?:[^|\]]+?)\|([^|\]]+?)}}', r'\1', plaintext,
        flags=re.I)

    # remover IPAC
    plaintext = re.sub(r'{{IPAC(?:.*?)}}', '', plaintext, flags=re.I)

    # remover score
    plaintext = re.sub(r'<score>(?:.*?)</score>', '', plaintext,
        flags=re.I|re.M|re.S)

    # remover citación necesaria
    plaintext = re.sub(r'{{(?:(?:Citation needed)|(?:Cita requerida))(?:.*?)}}',
        '', plaintext, flags=re.I|re.M|re.S)

    # remover magic words
    plaintext = re.sub(r'{{(?:__)?[A-Z]{2,}(?:.*?)}}', '', plaintext)

    # tratamiento blockquote, quote, paragraph y poem (CAMBIOS ESPAÑOL)
    plaintext = re.sub(r'<blockquote(?:[^>]*?)>(.*?)</blockquote>', r'\n\1\n',
        plaintext, flags=re.I|re.M|re.S)
    plaintext = re.sub(r'<p(?:[^>]*?)>(.*?)</p>', r'\n\1\n', plaintext,
        flags=re.I|re.M|re.S)
    plaintext = re.sub(r'<poem(?:[^>]*?)>(.*?)</poem>', r'\n\1\n', plaintext,
        flags=re.I|re.M|re.S)
    for match in\
            re.findall(r'{{(?:quote|cita|epígrafe) ?\|(.+?)}}', plaintext,\
                       re.I|re.M|re.S):
        split = match.split('|')
        text, author = '', ''
        for s in split:
            if re.search(r'(?:1|text)=', s, re.I):
                text = re.sub(r'(?:1|text)=', '', s, flags=re.I)
            elif re.search(r'(?:2|sign)=', s, re.I):
                author = re.sub(r'(?:2|sign)=', '', s, flags=re.I)
        text = split[0] if len(text) == 0 else text
        author = (split[1] if len(split)>1 else '') if len(author)==0 else author
        substitution = text + ('\n' + author + '\n' if len(author) > 0 else '')
        plaintext = re.sub(r'{{(?:quote|cita|epígrafe) ?\|(.+?)}}',
            '\n' + substitution + '\n',
            plaintext, count=1, flags=re.I|re.M|re.S)

    # tratamiento alineación de contenido (CAMBIOS ESPAÑOL)
    plaintext = re.sub(r'<div(?:[^>]*?)>(.*?)</div>', r'\1', plaintext,
        flags=re.I|re.M|re.S)
    plaintext = re.sub(r'<span(?:[^>]*?)>(.*?)</span>', r'\1', plaintext,
        flags=re.I|re.M|re.S)
    plaintext = re.sub(r'{{align\|(?:left|right|(?:center|centrar))\|(.*?)}}',
        r'\1', plaintext, flags=re.I)
    plaintext = re.sub(r'{{align\|(?:left|right|(?:center|centrar))}}',
        '', plaintext, flags=re.I)
    plaintext = re.sub(r'{{(?:left|right|(?:center|centrar))}}',
        '', plaintext, flags=re.I)
    plaintext = re.sub(r'{{(?:left|right|(?:center|centrar))\|(.*?)}}',
        r'\1', plaintext, flags=re.I)
    plaintext = re.sub(r'<center(?:[^>]*?)>(.*?)</center>', r'\1', plaintext,
        flags=re.I|re.M|re.S)
    plaintext = re.sub(r'{{stack\|(.*?)}}', r'\1', plaintext, flags=re.I)

    #################################
    # Inicio: Tratamiento de listas #
    #################################

    # plainlist and flatlist (CAMBIOS ESPAÑOL)
    plaintext = re.sub(
        r'{{(?:flatlist|plainlist|(?:lista simple)|(?:lista plana))\|(.*?)}}',
        r'\1', plaintext, flags=re.I|re.M|re.S)
    plaintext = re.sub(
        r'{{(?:(?:startflat|plain)list)}}(.*?){{(?:end(?:plain|flat)list)}}',
        r'\1', plaintext, flags=re.I|re.M|re.S)

    # unbulleted list (CAMBIOS ESPAÑOL)
    for match in\
            re.findall(r'{{(?:(?:unbulleted[ ]+list)|lsv)(.*?)}}', plaintext,\
                       re.I|re.M|re.S):        
        plaintext = re.sub(
            r'{{(?:(?:unbulleted[ ]+list)|lsv)(?:.*?)}}',
            match.strip('|').replace('|', '\n'),
            plaintext, count=1, flags=re.I|re.M|re.S)

    # listas (des-)ordenadas y descripciones (definiciones)
    plaintext = re.sub(r'^[*#:;]+ ?(.+?)', r'\1', plaintext, flags=re.I|re.M)

    # ordered list template (SIN CAMBIOS PARA ESPAÑOL)
    for match in\
            re.findall(r'{{ordered[ ]+list(.*?)}}', plaintext, re.I|re.M|re.S):
        substitution = re.sub(
            r'(?:(?:item[0-9]+_value)|list_style_type|start|item_style|type|style)=[^ ]+',
            ' ', match, flags=re.I)
        substitution = re.sub(r'\|(.*?)', r'\1\n', substitution)        
        substitution = re.sub(r'[0-9]+[ ]?=', '', substitution)
        substitution = substitution.replace('{{=}}', '')
        substitution = re.sub(r'^[ ]{1,}', '', substitution, flags=re.M)
        substitution = re.sub(r'[\n]{1,}', '\n', substitution)
        plaintext = re.sub(r'{{ordered[ ]+list(.*?)}}', substitution, plaintext,
            count=1, flags=re.I|re.M|re.S)

    # listas en HTML: ul, ol y dl
    for match in\
            re.findall(r'<(?:ul|ol|dl)(?:[^>]*?)>(.*?)</(?:ul|ol|dl)>',\
                       plaintext, re.I|re.M|re.S):
        substitution = re.sub(r'<(?:li|dt|dd)(?:[^>]*?)>(.*?)</(?:li|dt|dd)>',
            r'\1\n', match, flags=re.I|re.M|re.S)
        plaintext = re.sub(r'<(?:ul|ol|dl)(?:[^>]*?)>(.*?)</(?:ul|ol|dl)>',
            substitution, plaintext, count=1, flags=re.I|re.M|re.S)
    
    # remover col-begin y multi-column (SIN CAMBIOS PARA ESPAÑOL)
    plaintext = re.sub(r'{{col-begin(?:.*?)}}(?:.*?){{col-end}}', '', plaintext,
        flags=re.I|re.M|re.S)
    plaintext = re.sub(r'{{multi-column(?:.*?)}}', '', plaintext,
        flags=re.I|re.M|re.S)

    # glosario, término y definición templates (SIN CAMBIOS PARA ESPAÑOL)
    # NOTA: glosario es un 'wraper' de 'dl' tag
    plaintext = re.sub(r'{{(?:gbq|ghat)\|(?:1=)?(.+?)}}', r'\1',
        plaintext, flags=re.I)
    for match in re.findall(r'{{defn(.*?)}}', plaintext, re.I|re.M|re.S):
        substitution = re.sub(r'\|(?:no|term|style|id|class)=[^ ]{1,}',
            ' ', match, flags=re.I)
        substitution = re.sub(r'(?:\| ?(?:1|defn)=)(.+?)', r'\1', substitution,
            flags=re.I|re.M|re.S)
        plaintext = re.sub(r'{{defn(.*?)}}', substitution, plaintext, count=1,
            flags=re.I|re.M|re.S)
    for match in re.findall(r'{{term(.*?)}}', plaintext, re.I):
        m = re.search(r'(?:\|(?:1|term)=)([^|]{1,})', match, re.I)
        if m:
            term = m.group(1)
            plaintext = re.sub(r'{{term(.*?)}}', term, plaintext, count=1, flags=re.I)
    plaintext = re.sub(r'{{glossary(?:.*?)}}(.+?){{glossary end}}',
        r'\1', plaintext, flags=re.I|re.M|re.S)
    plaintext = re.sub(r'{{glossary link(.*?)}}', '', plaintext,
        flags=re.I|re.M|re.S)
    
    ##############################
    # Fin: Tratamiento de listas #
    ##############################

    # remover residuos de tablas
    plaintext = re.sub(
        r'^(?:(?:{\|)|(?:\|})|(?:\|-)|(?:\|\+)|(?:\|\|?)|!)', '',
        plaintext, flags=re.M)

    # remover repeticiones de caracter de igual
    plaintext = re.sub(r'[=]{2,}', '', plaintext)

    # remover links no identificados
    plaintext = re.sub(r'\[\[(?:.*?)\]\]', '', plaintext, flags=re.S)

    # remover templates no reconocidos (única línea)
    plaintext = re.sub(r'{{(.*?)}}', '', plaintext)

    # remover templates no reconocidos (multilinea)
    plaintext = re.sub(r'{{(?:.+?)}}', '',
        plaintext, flags=re.I|re.M|re.S)

    # remover etiquetas HTML
    plaintext = re.sub(r'<(?:/)?[^>]+>', '', plaintext, flags=re.I)

    # remover paréntesis vacíos
    plaintext = re.sub(r'\(\)', '', plaintext)      

    #######################################
    # TRATAMIENTO DE SIGNOS DE PUNTUACIÓN #
    #######################################

    if type(plaintext) == str:
        plaintext = plaintext.decode('utf-8')

    # unificación de comillas
    plaintext = re.sub(u"""[\u0060\u00B4\u2018\u2019]""", "'",
        plaintext, flags=re.UNICODE)
    plaintext = re.sub(u"""[\u201C\u201D\u00AB\u00BB]""", '"',
        plaintext, flags=re.UNICODE)    

    # Tratamiento de espacios 
    # remover espacios al inicio de línea
    plaintext = re.sub(r'^[ \t]+', '', plaintext, flags=re.M|re.S)
    # remover espacios contiguos
    plaintext = re.sub(r'[ ]{2,}', ' ', plaintext)
    # remover espacios al final
    plaintext = re.sub(r'(?: )$', '', plaintext, flags=re.M)

    # remover saltos de línea contiguos, al inicio y al final
    plaintext = re.sub(r'^[\n]+', '', plaintext)
    plaintext = re.sub(r'[\n]{2,}', '\n\n', plaintext)
    plaintext = re.sub(r'[\n]+$', '', plaintext)

    # primera letra en mayúscula
    for l in re.findall(u"""^([a-zu\xe1u\xe9u\xedu\xf3u\xfau\xf1])""",\
                        plaintext, re.UNICODE|re.M):        
        plaintext = re.sub(u"""^([a-zu\xe1u\xe9u\xedu\xf3u\xfau\xf1])""",
            l.upper(), plaintext, count=1, flags=re.UNICODE|re.M)

    # si una línea termina con dos letra y sin puntuación,
    # agregar un ';' al final.
    for match in re.findall(r'([\w]{2,})$', plaintext, re.UNICODE|re.M):
        # si contiene número, descartar
        if re.search(r'[0-9]+', match) or match[-1] == '_':
            continue
        plaintext = re.sub(match + '$', match + ';', plaintext,
            count=1, flags=re.UNICODE|re.M)

    # si finaliza con " :", remover el espacio
    plaintext = re.sub(r'[ ]+\:$', ':', plaintext, flags=re.M)
        
    return plaintext.encode('utf-8')


def write_in_corpus(fname, line):    
    with open(fname, 'a') as foutput:
        foutput.write(line)


def main():
    fname_input  = CORPUSPEDIA_PATH + '/corpus/eswiki-corpus_preproc-step-0.txt'
    fname_output = CORPUSPEDIA_PATH + '/corpus/eswiki-plaintext-corpus.txt'

    wikitext = ''
    wikitext_tag_is_open = False
    with open(fname_input) as finput:
        for line in finput:
            if re.match(r"\t<wikitext>", line, re.I):
                wikitext_tag_is_open = True
                wikitext = line
            elif re.search(r"</wikitext>\n$", line, re.I):
                wikitext += line
                plaintext = '\t<plaintext>' + parse_wikitext(wikitext) +\
                            '</plaintext>\n'
                write_in_corpus(fname_output, plaintext)
                wikitext_tag_is_open = False
            elif not wikitext_tag_is_open:
                write_in_corpus(fname_output, line)
            else:
                wikitext += line


if __name__ == '__main__':
    main()

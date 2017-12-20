# -*- coding: iso-8859-15 -*-

"""This is the main program of the Python project.

To use this program, please check the document "/docs/usage.rst".
"""


import difflib, multiprocessing, os, re, socket, subprocess, threading,\
        xml.etree.ElementTree as ET

import kenlm, numpy as np, psutil, py_common_subseq
from sklearn.grid_search import ParameterGrid
from unidecode import unidecode

from timeout import Timeout


CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

###############################
# read the configuration file #
###############################

config = ET.parse(CURRENT_PATH + '/config/general.xml').getroot()

FREELING_PORT = config[0][0].text

FOMA_PATH = config[1][0].text.rstrip('/')

IP_ADDRESS = config[1][1].text

SYSTEM_USER = config[2][0].text

NUM_WORKERS = '%i' % (2 * int(config[2][1].text) + 1)

config = None

##########################
# other config variables #
##########################

TRANSDUCERS_PATH = CURRENT_PATH + '/datasets/transducers/bin'

TRANSDUCERS = {
    'es-dicc':
        [TRANSDUCERS_PATH + '/es-dicc.bin', IP_ADDRESS, '60962'],
    'pnd-gazetteer':
        [TRANSDUCERS_PATH + '/PND-Gazetteer.bin', IP_ADDRESS, '60963'],
    'primary_variants':
        [TRANSDUCERS_PATH + '/primary_variants.bin', IP_ADDRESS, '60964'],
    'dictionary_lookup':
        [TRANSDUCERS_PATH + '/dictionary_lookup.bin', IP_ADDRESS, '60965'],
    'secondary_variants-dicc':
        [TRANSDUCERS_PATH + '/secondary_variants-Dicc.bin', IP_ADDRESS, '60966'],
    'es-verbal-forms-fonemas':
        [TRANSDUCERS_PATH + '/es-verbal-forms-fonemas.bin', IP_ADDRESS, '60967'],
    'es-diminutives-fonemas':
        [TRANSDUCERS_PATH + '/es-diminutives-fonemas.bin', IP_ADDRESS, '60968'],
    'pnd-gazetteer-fonemas':
        [TRANSDUCERS_PATH + '/PND-gazetteer-fonemas.bin', IP_ADDRESS, '60969'],
    'tertiary_variants-dicc':
        [TRANSDUCERS_PATH + '/tertiary_variants-Dicc.bin', IP_ADDRESS, '60970'],
    'tertiary_variants-pnd':
        [TRANSDUCERS_PATH + '/tertiary_variants-PND.bin', IP_ADDRESS, '60971'],
    'pnd-gazetteer-case':
        [TRANSDUCERS_PATH + '/PND-gazetteer-CaSe.bin', IP_ADDRESS, '60972'],
    'iv-candidates-fonemas':
        [TRANSDUCERS_PATH + '/IV-candidates-fonemas.bin', IP_ADDRESS, '60973'],
    'split-words':
        [TRANSDUCERS_PATH + '/split-words.bin', IP_ADDRESS, '60974'],
    'length_normalisation':
        [TRANSDUCERS_PATH + '/length_normalisation.bin', IP_ADDRESS, '60982'],
    'length_normalisation-2':
        [TRANSDUCERS_PATH + '/length_normalisation-2.bin', IP_ADDRESS, '60983'],
    'phonology':
        [TRANSDUCERS_PATH + '/phonology.bin', IP_ADDRESS, '60984'],
    'other-changes':
        [TRANSDUCERS_PATH + '/other-changes.bin', IP_ADDRESS, '60985'],
    'remove_enclitic':
        [TRANSDUCERS_PATH + '/remove_enclitic.bin', IP_ADDRESS, '61002'],
    'accentuate_enclitic':
        [TRANSDUCERS_PATH + '/accentuate_enclitic.bin', IP_ADDRESS, '61003'],
    'remove_mente':
        [TRANSDUCERS_PATH + '/remove_mente.bin', IP_ADDRESS, '61004']}

CORPORA = {
    'eswiki-corpus-3-grams':
        CURRENT_PATH + '/datasets/eswiki/corpora/eswiki-corpus-3-grams.bin'}

####################
# global variables #
####################

ALPHABET = re.compile(u'''[a-z\xe1\xe9\xed\xf3\xfa\xfc\xf1]''', re.I|re.U)

VOWELS_RE = re.compile(u'''[aeiou\xe1\xe9\xed\xf3\xfa\xfc]''', re.I|re.U)

ACCENTED_VOWELS_RE = re.compile(u'''[\xe1\xe9\xed\xf3\xfa]''', re.I|re.U)

ONE_LETTER_WORDS = [u'a', u'e', u'o', u'u', u'y']

TWO_LETTER_WORDS = [u'ah', u'al', u'ay',
    u'da', u'de', 'dé'.decode('utf-8'), u'di', 'dí'.decode('utf-8'),
    u'eh', u'el', 'él'.decode('utf-8'), u'en', u'es', u'ex',
    u'fe',
    u'ha', u'he',
    u'id', u'ir',
    u'ja', u'je', u'ji', u'jo', u'ju',
    u'la', u'le', u'lo',
    u'me', u'mi', 'mí'.decode('utf-8'),
    u'ni', u'no',
    u'oh', 'oí'.decode('utf-8'), u'ok', u'os',
    u'se', 'sé'.decode('utf-8'), u'si', 'sí'.decode('utf-8'), u'su',
    u'te', 'té'.decode('utf-8'), u'ti', u'tu', 'tú'.decode('utf-8'),
    u'uf', u'uh', u'un', u'uy',
    u'va', u've', 'vé'.decode('utf-8'), u'vi',
    u'ya', u'yo']


LOCK = threading.Lock()


def _to_unicode(token):
    return token.decode('utf-8') if not isinstance(token, unicode) else token


def _to_str(token):
    return token.encode('utf-8') if not isinstance(token, str) else token


def _write_in_file(fname, content, mode='w', makedirs_recursive=True):
    dir_ = '/'.join(fname.split('/')[:-1])
    if not os.path.isdir(dir_) and makedirs_recursive:
        os.makedirs(dir_)
    with open(fname, mode) as f:
        f.write(content)


def _deaccent(word):
    '''Remueve las tildes de la palabra.'''
    word = _to_unicode(word)

    remove_accents = {
        u'\xe1': u'a',
        u'\xe9': u'e',
        u'\xed': u'i',
        u'\xf3': u'o',
        u'\xfa': u'u',
        u'\xfc': u'u'}

    return _to_unicode(''.join([
        remove_accents[s] if s in remove_accents.keys() else s
        for s in word]))


def _normalize_unknown_symbols(token):
    """Símbolos (letras) no reconocidos los decodifica a ASCII."""
    return ''.join([
        s if ALPHABET.match(s) else _to_unicode(unidecode(s))
        for s in _to_unicode(token)])


def _switch_freeling_server(
        mode='on', initialization_command='default', port=FREELING_PORT,
        workers=NUM_WORKERS):
    '''Inicia/termina el servico de análisis de FreeLing.

    paráms:
        initialization_command: str | list
            especificar la configuración de FreeLing. Por defecto, es la provista
            por el TweetNorm 2013.
            NOTA: se agrega este parámetro para permitir la inicialización de
            FreeLing desde otros archivos.
        port: int
            cuál puerto se utilizará para ejecutar el servicio de FreeLing.

    NOTA: el proceso se inicia y se termina usando el usuario SYSTEM_USER.
    '''
    pid = None
    for process in psutil.process_iter():
        cmd_line = process.cmdline()
        if (process.username() == SYSTEM_USER and len(cmd_line) > 1
                and re.search('analyzer$', cmd_line[0], re.I)
                and (cmd_line[-4] == port)):
            pid = process.pid
            break
    if pid is not None and mode == 'off':
        psutil.Process(pid=pid).kill()
    elif pid is None and mode == 'on':
        if (isinstance(initialization_command, str)
                and initialization_command == 'default'):
            subprocess.Popen(['analyze', '-f', CURRENT_PATH + '/config/es.cfg',
                '--flush', '--ftok', CURRENT_PATH + '/config/es-twit-tok.dat',
                '--usr', '--fmap', CURRENT_PATH + '/config/es-twit-map.dat',
                '--outlv', 'morfo', '--noprob', '--noloc',
                '--server', '--port', port, '--workers', workers, '&'])
        elif (isinstance(initialization_command, list)
                and len(initialization_command) > 0):
            subprocess.Popen(initialization_command)
        else:
            raise Exception('No ha especificado un comando de inicialización válido')


def _analyze_morphologically(text, port=FREELING_PORT):
    '''Analiza morfologicamente el texto de un tweet.

    Mediante este método se identifican palabras fuera de vocabulario.

    NOTA: la configuración de FreeLing para analizar el tweet es dada por la
          organización del workshop TweetNorm 2013.
          El análisis se realiza haciendo uso del servicio expuesto por FreeLing.
    '''
    text = _to_str(text)

    fname = CURRENT_PATH + '/.tmp/FreeLing-%03d%s%05d' %(
        np.random.randint(0, 100),
        '-' if np.random.randint(0,2) == 1 else '',
        np.random.randint(0, 100000))

    _write_in_file(fname + '.txt', text)

    subprocess.call(["analyzer_client", port],
        stdin=open(fname  + '.txt'),
        stdout=open(fname + '.morpho', 'w'))

    sentences = []
    sentence = []
    with open(fname + '.morpho') as foutput:
        for line in foutput:
            line = line.rstrip('\n')
            if len(line) == 0:
                sentences.append(sentence)
                sentence = []
                continue
            try:
                form, lemma, tag = re.split('\s+', line)[:3]
                sentence.append([
                    form.decode('utf-8'), lemma.decode('utf-8'),
                    tag.decode('utf-8')])
            except:
                form = line
                sentence.append([form.decode('utf-8'), '', ''])

    os.remove(fname + '.txt')
    os.remove(fname + '.morpho')

    return sentences


def _check_flookup_server_status(transducer):
    """Evalúa si el transductor está ejecutándose como servicio.

    paráms:
        transducer: str
            Nombre del transductor. Puede ser la ruta completa
            o parte de esta.

    Retorna el pid del proceso de flookup que ejecuta como servidor
    el transductor.

    NOTA: los procesos deben haber sido ejecutados por el usuario SYSTEM_USER.
    """
    pid = None
    transducer = _to_str(transducer)
    for process in psutil.process_iter():
        cmd_line = process.cmdline()
        if (process.username() == SYSTEM_USER and len(cmd_line) > 1
                and re.search('flookup$', cmd_line[0], re.I)
                and re.search(transducer + '.bin', _to_str(cmd_line[-2]), re.I)):
            pid = process.pid
            break
    return pid


def _switch_flookup_server(
        transducer='all', mode='on', set_of_transducers=TRANSDUCERS):
    """Iniciar o terminar un servicio de transductor como servidor.

    paráms:
        transducer: str
            nombre del transductor definido como clave en el diccionario
            set_of_transducers.
            Por defecto se asumen todos los transductores.
        mode: str
            toma dos posibles valores: ON, para iniciar el servidor;
            OFF, para terminar el servidor.
        set_of_transducers: dict
            conjunto de transductores
            NOTA: este parámetro se agrega para permitir la ejecución
            de transductores que no se especifican en este fichero.

    NOTA: los procesos deben ser ejecutados por el usuario SYSTEM_USER.
    """
    transducer = _to_str(transducer).lower()
    if transducer != 'all' and transducer not in set_of_transducers.keys():
        raise Exception('Transductor %s no reconocido' % transducer)
    elif mode not in ['on', 'off']:
        raise Exception('La acción definida no es válida')

    if transducer == 'all':
        pool = multiprocessing.Pool(processes=3)
        for t in set_of_transducers.keys():
            pool.apply_async(
                _switch_flookup_server,
                [t, mode, set_of_transducers])

        pool.close()
        pool.join()

        return

    pid = _check_flookup_server_status(transducer)
    transducer = set_of_transducers[transducer]

    if mode == 'on':
        if pid is None:
            subprocess.Popen([FOMA_PATH + '/flookup', '-S',
                '-A', transducer[1], '-P', transducer[2],
                '-i', '-x', transducer[0], '&'])
    else:
        if pid is not None:
            process = psutil.Process(pid=pid)
            process.kill()


def _foma_string_lookup(token, transducer, set_of_transducers=TRANSDUCERS):
    '''Analiza el token a través del transductor especificado.

    paráms:
        token: str
            cadena de caracteres a ser analizada.
        transducer: str
            transductor que analizará el token. Puede ser una ruta completa
            o alguna de las claves especificadas en set_of_transducers.
        set_of_transducers: dict
            conjunto de transductores

    NOTA: si el transductor no es una ruta física del sistema, sino una de las
    claves del diccionario set_of_transducers, se analizará como servicio de
    flookup. Para esto, deberá haberse iniciado con anterioridad el servicio de
    flookup.
    '''
    use_server = False
    if transducer.lower() in set_of_transducers.keys():
        use_server = True
    elif not os.path.isfile(transducer):
        raise Exception('El transductor especificado no existe')

    token = _to_str(token)

    result = []
    if not use_server:
        fname_input = '%s-%03d%s%05d.txt' % (
            CURRENT_PATH + '/.tmp/flookup',
            np.random.randint(0, 100),
            '-' if np.random.randint(0,2) == 1 else '_',
            np.random.randint(0, 100000))
        _write_in_file(fname_input, token, mode='w')

        fname_output = fname_input.replace('.txt', '.out')
        subprocess.call([FOMA_PATH + '/flookup', '-i', '-x', transducer],
            stdin=open(fname_input),
            stdout=open(fname_output, 'w'))

        with open(fname_output) as finput:
            for line in finput:
                line = line.rstrip('\n')
                if len(line.strip()) > 0 and line != '?+':
                    result.append(_to_unicode(line))

        os.remove(fname_input)
        os.remove(fname_output)
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        transducer = set_of_transducers[transducer.lower()]
        sock.sendto(token, (transducer[1], int(transducer[2])))

        data, addr = sock.recvfrom(4096)

        result = [_to_unicode(d)
            for d in data.split('\n')
                if len(d.strip()) > 0 and d != '?+']

        sock.close()

    return result


def _transducers_cascade(token, transducers, set_of_transducers=TRANSDUCERS):
    """Ejecuta una cascada de transductores en foma.

    Si bien la cascada puede implementarse directamente sobre foma,
    este método se desarrolla porque puede ser más económico ejecu-
    tar secuncialmente.

    paráms:
        token: str o array de str
    """
    if isinstance(token, list):
        tokens = token
        concatenated_result = []
        for token in tokens:
            concatenated_result += _transducers_cascade(
                token, transducers, set_of_transducers)
        return concatenated_result

    result = []
    for i, transducer in enumerate(transducers):
        tokens = []
        iter_result = []
        if i == 0:
            tokens.append(token)
        else:
            tokens = result[i - 1]
        iter_result = [t2
            for t1 in tokens
                for t2 in _foma_string_lookup(t1, transducer, set_of_transducers)
                    if len(t2.strip()) > 0 and t2 != '?+']
        result.append(np.unique(iter_result).tolist())

    return result[i]


def _recover_original_word_case_from_type(word, case_type):
    """Recupera las minús./mayús de la palabra según el tipo identificado."""
    word = _to_unicode(word).lower()
    if case_type == 0:
        return word
    elif case_type == 1:
        return word[0].upper() + word[1:]
    else:
        return word.upper()


def _get_case_type_in_token(token):
    """Retorna cómo está formada la palabra según mayúsculas/minúsculas.

    El valor (entero) retornado es uno de los siguientes:
        0 -> palabra completamente en minúscula.
        1 -> palabra con la primera letra en mayúscula.
        2 -> palabra principalmente (o totalmente) formada por mayúsculas.
    """
    token = _to_unicode(token)

    case_type = 2

    if token.lower() == token:
        case_type = 0
    elif len(token) > 1 and (token[0].upper() + token[1:].lower()) == token:
        case_type = 1

    return case_type


def _select_non_fused_words(candidates):
    """Seleccciona el menor número de palabras.

    El separador de palabras es el caracter "_".

    Es decir, se selecciona el menor número de "_" insertados.

    NOTA: si la palabra termina en una letra, se descarta. O
    si hay una palabra igual que "ll", también se dercarta.
    También, se aceptan candidatas con una palabra más, al mínimo establecido,
    si y solo si, esta nueva palabra es de longitud uno.
    """
    final_candidates = []
    final_candidates_aux = []
    idx = np.array([len(c.split('_')) for c in candidates], dtype=int)
    lengths = []
    for i in np.where(idx <= (idx.min() + 1))[0]:
        words = candidates[i].split('_')
        words_length = []
        ill_formed_word = False
        for j, word in enumerate(words):
            word = _to_unicode(word)
            words_length.append(len(word))
            if (word == u'll'
                    or (j == (len(words) - 1) and len(word) < 2)
                    or (len(word) == 2 and word not in TWO_LETTER_WORDS)
                    or (j == 0 and word in [u'e', u'o', u'u'])
                    or (word == 'e' and words[j+1].lower()[0] != u'i')
                    or (word == 'o' and words[j+1].lower()[0] == u'o')
                    or (word == 'u' and words[j+1].lower()[0] != u'o')
                    or (not VOWELS_RE.search(word) and word != u'y')):
                ill_formed_word = True
                break
        if not ill_formed_word and len(words) == idx.min():
            lengths.append(words_length)
            final_candidates.append(candidates[i])
        elif not ill_formed_word:
            final_candidates_aux.append(candidates[i])
    for candidate in final_candidates_aux:
        words_length = [len(_to_unicode(w)) for w in candidate.split('_')]
        ill_formed_word = []
        for length in lengths:
            j = 0
            for l in length:
                if l != words_length[j]:
                    if ((words_length[j]==1 or words_length[j+1]==1)
                            and (words_length[j]+words_length[j+1])==l):
                        ill_formed_word.append(0)
                    else:
                        ill_formed_word.append(1)
                    break
                j += 1
        if (len(ill_formed_word) == len(lengths)
                and sum(ill_formed_word) < len(lengths)):
            final_candidates.append(candidate)
    return final_candidates


def _find_longest_common_substring(string_1, string_2):
    """Encuentra el más largo substring entre dos cadenas.

    También devuelve el ratio: longitud del LCSubstring
    dividido el string de mayor longitud entre string_1
    y string_2.
    """
    string_1 = _deaccent(_to_unicode(string_1).lower())
    string_2 = _deaccent(_to_unicode(string_2).lower())

    max_length = len(string_1)
    if len(string_2) > max_length:
        max_length = len(string_2)

    seq_matcher = difflib.SequenceMatcher(None, string_1, string_2)

    longest_match = seq_matcher.find_longest_match(0, len(string_1),
        0, len(string_2))

    longest_match_str = None
    longest_match_ratio = .0
    if longest_match.size != 0:
        longest_match_str = string_1[longest_match.a:
            longest_match.a + longest_match.size]
        longest_match_ratio = len(longest_match_str) / float(max_length)

    return longest_match_str, longest_match_ratio, longest_match.a, longest_match.b


def _compute_longest_common_subsequence_ratio(
        oov_word, iv_word, recursion=False, normalise_lengthening=True):
    """Calcula el radio de LCS entre dos palabras dadas.

    El radio de LCS se calcula sobre el string de mayor
    longitud entre oov-word e iv-word.
    [REF] Lexical Normalisation of Short Text Messages: Makn Sens a #twitter

    NOTA: se remueven acentos para no afectar el cómputo de LCSR.
    """
    if not recursion:
        oov_word = _deaccent(_to_unicode(oov_word).lower())
        iv_word  = _deaccent(_to_unicode(iv_word).lower())

        try:
            with Timeout(2):
                oov_words = _foma_string_lookup(oov_word, 'other-changes')
        except Timeout.Timeout:
            oov_words = [oov_word]
            _switch_flookup_server('other-changes', mode='on')
        LCSR_values = np.zeros(len(oov_words), dtype=float)

        for i, string in enumerate(oov_words):
            LCSR_values[i] = _compute_longest_common_subsequence_ratio(
                string, iv_word, recursion=True,
                normalise_lengthening=normalise_lengthening)

        return LCSR_values.max()

    oov_word = _deaccent(_to_unicode(oov_word).lower())
    iv_word  = _deaccent(_to_unicode(iv_word).lower())

    normalised_variants = [oov_word]
    if normalise_lengthening:
        normalised_variants = _foma_string_lookup(
            oov_word, 'length_normalisation-2')

    LCSR = 0.
    # normalización a una o dos repeticiones
    for normalised_f in normalised_variants:
        normalised_f = _to_unicode(normalised_f)
        max_length = np.max(
            np.array([len(normalised_f), len(iv_word)], dtype=float))
        common_subseq = py_common_subseq.find_common_subsequences(
            normalised_f, iv_word)
        for subseq in common_subseq:
            ratio = len(subseq) / max_length
            LCSR = ratio if ratio > LCSR else LCSR

    return LCSR


def _filter_target_words_by_length(target_words):
    """Filtra candidatas de acuerdo a su longitud.

    Exactamente, si la candidata empieza en minúscula, es decir,
    es recuperada del diccionario de español, y su longitud es
    menor que tres, ésta debe estar en el listado de palabras
    de longitud uno o dos aceptadas.
    """
    target_words_ = []
    for target in target_words:
        target = _to_unicode(target)
        if len(target) in [1, 2] and target[0] == target[0].lower():
            if len(target) == 1 and target in ONE_LETTER_WORDS:
                target_words_.append(target)
            elif target in TWO_LETTER_WORDS:
                target_words_.append(target)
        else:
            target_words_.append(target)

    return target_words_


def _filter_target_words_based_on_LCSR(oov_word, target_words, LCSR):
    """Filtra target words cuyo LCSR está por debajo del umbral requerido."""
    remove_idx = []
    for i, target in enumerate(target_words):
        ratio = _compute_longest_common_subsequence_ratio(
            oov_word, target)
        if ratio < LCSR:
            remove_idx.append(i)
    else:
        for i in reversed(remove_idx):
            target_words.pop(i)
    return target_words


def _check_affixes(word, normalised_variants, affix=None, what_affix=None):
    '''Extrae prefijos y sufijos comunes.

    paráms:
        word: str
            palabra no normalizada (en cuanto a repetición de caracteres).
        normalised_variants: array (de elementos de tipo str)
            variantes normalizadas a uno o dos repeticiones como máximo de
            caracteres.
        affix: str
            tipo de búsqueda a realizar.
            'suffix' (para sufijo) o 'prefix' (para prefijo)
        what_affix: str
            se especifica cuál búsqueda realizar de acuerdo al tipo.
    '''
    if affix is None:
        searches = [
            ['suffix', 'enclitic'],
            ['suffix', 'mente'],
            ['suffix', 'diminutives']]
        target_words = []
        for affix, what_affix in searches:
            target_words += _check_affixes(word, normalised_variants,
                affix, what_affix)

        return np.unique(target_words).tolist()

    target_words = []

    if affix == 'suffix' and what_affix == 'enclitic':
        # identificar cuáles variantes corresponden a una forma
        # verbal (candidata) removiendo hipotéticos enclíticos
        final_verbal_form = [
            '', # forma verbal
            .0, # Longest Common Substring ratio
            '', # enclítico
            False, # si la s de forma verbal fue suprimida (vamos+nos -> vámonos)
            ]
        for verbal_form in _foma_string_lookup(word, 'remove_enclitic'):
            if verbal_form not in normalised_variants:
                # comparar la forma verbal (candidata) con las variantes
                # normalizadas, para así determinar con cuál es más simi-
                # lar y cuál el enclítico removido
                for normalised_f in normalised_variants:
                    longest_match = _find_longest_common_substring(
                        verbal_form, normalised_f)

                    if (longest_match[1] == .0 or
                            longest_match[2] != 0 or longest_match[3] != 0):
                        continue

                    enclitic = normalised_f[len(longest_match[0]):]
                    if longest_match[1] > final_verbal_form[1]:
                        final_verbal_form = [longest_match[0],
                            longest_match[1], enclitic,
                            False]

        if final_verbal_form[1] != .0:
            # realizar la conversión grafema/fonema de la forma verbal
            if final_verbal_form[0].endswith('mo'):
                final_verbal_form[0] =  final_verbal_form[0] + u's'
                final_verbal_form[3] = True

            verbal_forms_from_fonema = _transducers_cascade(final_verbal_form[0],
                ['length_normalisation-2',
                 'phonology',
                 'es-verbal-forms-fonemas'])
            for verbal_form in verbal_forms_from_fonema:
                _verbal_form = verbal_form

                if final_verbal_form[3]:
                    verbal_form = verbal_form[:-1]

                verbal_form = verbal_form + final_verbal_form[2]

                accentuated_forms = np.unique(_foma_string_lookup(verbal_form,
                    'accentuate_enclitic')).tolist()

                # depurar: si hay dos o más tildes en la palabra -> descartar
                remove_idx = []

                non_accented_form = u''
                for i, accentuated_form in enumerate(accentuated_forms):
                    accented_vowels = ACCENTED_VOWELS_RE.findall(accentuated_form)
                    if len(accented_vowels) == 1:
                        target_words.append(accentuated_form)
                    elif len(accented_vowels) > 1:
                        remove_idx.append(i)
                    else:
                        non_accented_form = accentuated_form

                for i in reversed(remove_idx):
                    accentuated_forms.pop(i)

                if (len(target_words) == 0 and not final_verbal_form[3] and
                            (re.search(u'''[\xe1\xe9\xf3]i''', _verbal_form, re.U)
                             or re.search(u'''\xed[aeo]''', _verbal_form, re.U))):
                    target_words.append(_verbal_form + final_verbal_form[2])
                else:
                    target_words.append(verbal_form)
                    target_words.append(non_accented_form)
    elif affix == 'suffix' and what_affix == 'mente':
        # realizar búsqueda del sufijo -mente en la palabra,
        # e identificar posibles adjetivos
        adjectives = []
        for adjective in _foma_string_lookup(word, 'remove_mente'):
            if adjective not in normalised_variants:
                adjectives += _foma_string_lookup(
                    adjective, 'secondary_variants-dicc')

        if len(adjectives) != 0:
            longest_match_ratios = np.zeros((len(adjectives), 2))
            for i, adjective in enumerate(adjectives):
                for normalised_f in normalised_variants:
                    if not re.search(u'(?:mente)$', normalised_f, re.U):
                        continue
                    normalised_f = re.sub(u'(?:mente)$', '',
                        normalised_f, flags=re.U)
                    LCSR = _compute_longest_common_subsequence_ratio(
                        normalised_f, adjective,
                        recursion=False, normalise_lengthening=False)
                    if LCSR > longest_match_ratios[i,0]:
                        longest_match_ratios[i,0] = LCSR
                        longest_match_ratios[i,1] =\
                            _find_longest_common_substring(normalised_f, adjective)[1]
            idx_i = np.where(
                longest_match_ratios[:,0] == longest_match_ratios[:,0].max())[0]
            idx_j = np.where(
                longest_match_ratios[:,1] == longest_match_ratios[:,1].max())[0]
            intersect = np.intersect1d(idx_i, idx_j)
            if len(idx_i) == 1 or len(intersect) == 0:
                target_words.append(adjectives[idx_i[0]] + u'mente')
            else:
                target_words.append(adjectives[intersect[0]] + u'mente')
    elif affix == 'suffix' and what_affix == 'diminutives':
        diminutives = []
        for normalised_f in normalised_variants:
            normalised_f = _deaccent(normalised_f)
            diminutives.append([normalised_f, None])

            if normalised_f.endswith(u'z'):
                normalised_f = normalised_f[:-1] + u's'

            changes = []
            if normalised_f.endswith(u's'):
                normalised_f = normalised_f[:-1]
                diminutives.append([normalised_f, u's'])
                changes.append(u's')
            elif normalised_f.endswith(u'tin'):
                diminutives.append([normalised_f[:-2] + u'o', u'in'])

            if re.search(r'i(?:ll|y)[ao]$', normalised_f, re.U):
                normalised_f = re.sub(r'i(?:ll|y)([ao])$', r'it\1',
                    normalised_f, flags=re.U)
                changes.append(u'll')
                diminutives.append([normalised_f, u'+'.join(changes)])

            if normalised_f.endswith(u'a'):
                diminutives.append([normalised_f[:-1] + u'o',
                    u'+'.join(changes + [u'a'])])
            elif normalised_f.endswith(u'o'):
                diminutives.append([normalised_f[:-1] + u'a',
                    u'+'.join(changes + [u'o'])])

        # realizar transcripción fonética y recuperar diminutivos
        diminutive_candidates = diminutives
        diminutives = []
        for candidate, changes in diminutive_candidates:
            real_words = _transducers_cascade(candidate,
                ['phonology', 'es-diminutives-fonemas'])
            for result in real_words:
                if changes is None:
                    diminutives.append(result)
                    continue
                elif changes == u'in':
                    diminutives.append(result[:-1] + 'ín'.decode('utf-8'))
                    continue

                for change in reversed(changes.split(u'+')):
                    if change == u's':
                        result = result + u's'
                    elif change == u'll':
                        result = re.sub(r'it([ao])', r'ill\1',
                            result, flags=re.U)
                    elif change in [u'a', u'o']:
                        result = result[:-1] + change
                else:
                    diminutives.append(result)

        diminutives = np.unique(diminutives).tolist()

        if len(diminutives) == 1:
            target_words.append(diminutives[0])
        elif len(diminutives) > 1:
            longest_match_ratios = np.zeros(len(diminutives))
            for i, diminutive in enumerate(diminutives):
                longest_match_ratios[i] =\
                    _compute_longest_common_subsequence_ratio(
                        word, diminutive, False, True)
            target_words.append(diminutives[longest_match_ratios.argmax()])

    return np.unique(target_words).tolist()


def _filter_out_acronyms(variants, target_words, max_length):
    '''Filtra palabras objetivo identificadas como acrónimos.

    Un acrónimo es definido como una palabra compuesta de sólo
    consonantes (es decir, sin vocales).
    NOTA: esta definición es parcial.

    Así, descarta acrónimos que no coinciden con alguna de las
    variantes normalizadas (a una y dos repeticiones) de la pa-
    labra objetivo.
    '''
    remove_idx = []
    for i, target in enumerate(target_words):
        target = _to_unicode(target)
        if (max_length < 5
                and (target == target.upper() or not VOWELS_RE.search(target))
                and target.lower() not in variants):
            remove_idx.append(i)

    for i in reversed(remove_idx):
        target_words.pop(i)

    return target_words


def _are_target_words_only_acronyms(target_words):
    """Determina si las palabras sugeridas sólo consisten de acrónimos.

    Es un acrónimo aun si está en minúscula, pero no tiene vocal.
    """
    validation = True
    for target in target_words:
        target = _to_unicode(target)
        if target.upper() != target and VOWELS_RE.search(target[1:]):
            validation = False
            break
    return validation


def _are_target_words_only_proper_nouns(target_words):
    """Evalúa si las palabras sugeridas son sólo PNDs.

    Aun si está en minúscula y no tiene vocal, se considera una variante
    de acrónimo, y por lo tanto PND.
    """
    validation = True
    for target in target_words:
        target = _to_unicode(target)
        if target.lower() == target and VOWELS_RE.search(target):
            validation = False
            break
    return validation


def _suggest_target_words(word, case_type, external_dicc=None):
    """Sugiere variantes aceptadas (in-vocabulary) de acuerdo al token dado.

    Las variantes se producen en cascada; así, si no se generan candidatas en un
    nivel, se busca en el siguiente. Si ningún nivel produce variantes, la pala-
    bra misma es devuelta.

    paráms:
        word: unicode
            Palabra que (probablemente) está fuera del vocabulario.
            Debe estar en minúscula y los caracteres por fuera del alfabeto, nor-
            malizados a su representación en ASCII.
        case_type: int
            Cómo, en mayúsculas/minúsculas, está formada la OOV originalmente.
        external_dicc: dict
            Diccionario de normalización dependiente de contexto, es decir, ex-
            terno. (Véase la explicación [1] en el método `__init__´ de la clase
            `SpellTweet´).
    """
    # variantes normalizadas a una o dos repeticiones de la palabra
    min_length, max_length = 0, 0
    normalised_variants = []
    for normalised_f in _foma_string_lookup(word, 'length_normalisation-2'):
        normalised_f = _deaccent(_to_unicode(normalised_f).lower())
        if min_length == 0 or len(normalised_f) < min_length:
            min_length = len(normalised_f)
        if len(normalised_f) > max_length:
            max_length = len(normalised_f)
        if normalised_f not in normalised_variants:
            normalised_variants.append(normalised_f)

    normalised_variants = np.unique(normalised_variants).tolist()

    target_words = []

    # candidatas siendo la misma OOV.
    # Se tiene en cuenta como estaba escrita originalmente.
    oov_candidates = [word]
    if case_type != 0:
        oov_candidates.append(
            _recover_original_word_case_from_type(word, case_type))

    # 1. Generación de variantes primarias:
    # (Pre:) Normalización de repetición de caracteres.
    # Estas variantes son "marcadas" con alguno de los siguientes sufijos:
    #   _LAUGH: interjección de risa (por ej.: ja, je, ..., ju).
    #       Note que esta es una variación, y por lo tanto, se provee
    #       la correspondiente normalización.
    #   _EMO: emoticón.
    #       Note que esta no es una variación; se trata de un NoEs (no espa-
    #       ñol) y por lo tanto se devuelve la forma misma.
    #   _NORM: variante encontrada en el diccionario de normalización.
    #       Note que esta es una variación, y por lo tanto, se provee
    #       la correspondiente normalización.
    primary_variants = _foma_string_lookup(word, 'primary_variants')

    for variant in primary_variants:
        s = re.search(r"(.+?)_((?:emo)|(?:inter)|(?:laugh)|(?:norm))$",
            variant, re.I|re.U)
        if s and s.group(2).lower() != 'emo':
            target_words.append(s.group(1))
        elif s:
            target_words.append('%' + s.group(2))
            break

    if len(target_words) > 0:
       return target_words
    elif external_dicc is not None:
        original_word = _recover_original_word_case_from_type(word, case_type)

        external_suggestions = _foma_string_lookup(
            original_word, 'external-dicc', external_dicc)
        target_words = external_suggestions

        if len(target_words) > 0:
            return target_words

    # Dictionary lookup
    target_words = _transducers_cascade(word, ['dictionary_lookup', 'es-dicc'])
    target_words = _filter_target_words_by_length(target_words)

    # Buscar si alguna de las palabras candidatas del diccionario
    # hace también parte del gazetteer de nombres propios
    aux_target_words = []
    for candidate in target_words:
        aux_target_words += _foma_string_lookup(
            _recover_original_word_case_from_type(candidate, 1), 'pnd-gazetteer')

    target_words += aux_target_words

    if len(target_words) > 0:
        return np.unique(target_words).tolist()

    # 2. Generación de variantes secundarias:
    # (Pre:) Normalización de repetición de caracteres.
    # Estas variantes corresponden a palabras que suenan igual a la OOV, y
    # pueden ser entradas del diccionario o del gazetteer de PNDs.
    # Para identificar PNDs, la OOV se normaliza de repetición de caracteres
    # y se realiza conversión grafema/fonema.
    target_words = _foma_string_lookup(word, 'secondary_variants-dicc')
    target_words += _check_affixes(word, normalised_variants)
    target_words = _filter_target_words_by_length(target_words)

    target_words += _transducers_cascade(word,
        ['length_normalisation', 'phonology', 'pnd-gazetteer-fonemas'])

    # No se generan variantes de tercer nivel si las generadas en este nivel
    # son palabras y/o nombres propios (conformados por al menos una vocal).
    # Si son solo nombres propios, una de estas candidatas debe tener un LCSR
    # igual o superior a .55
    filtering_PNDs = [
        _compute_longest_common_subsequence_ratio(word, candidate, True) >= .55
        for candidate in target_words]
    num_filtered_candidates = sum([1 if v_ else 0 for v_ in filtering_PNDs])
    if (len(target_words) > 0
            and (not _are_target_words_only_proper_nouns(target_words)
                    or (not _are_target_words_only_acronyms(target_words)
                        and num_filtered_candidates > 0))):
        target_words += oov_candidates
        target_words = np.unique(target_words).tolist()

        return _filter_out_acronyms(normalised_variants,
            target_words,
            max_length)

    # 3. Generación de variantes terciarias:
    # (Pre:)
    #    + Normalización de repetición de caracteres.
    #    + Remover tildes.
    #    + Inserción de una sola vocal en cualquier posición de la palabra.
    #      Esto representa a la escritura consonontal.
    #      NOTA: no se utiliza para la generación de IV-candidates, ni en la
    #            separación de palabras fusionadas.
    #    + Agregar tildes.
    # Las variantes se generan así:
    #   1. Palabras del diccionario estándar o entradas del gazetteer de PNDs
    #      que están a una distancia de edición de 1 (sustitución, reemplazo
    #      e inserción).
    #   2. Palabras de la lista de IV-candidates que suenan igual.
    #   3. Separación de palabras unidas. Esta separación se da fonemas.
    target_words += _foma_string_lookup(word, 'tertiary_variants-dicc')
    target_words = _filter_target_words_by_length(target_words)
    target_words += _transducers_cascade(
        _foma_string_lookup(word, 'tertiary_variants-pnd'),
        ['pnd-gazetteer-case'])
    target_words += _transducers_cascade(word,
        ['length_normalisation', 'phonology', 'iv-candidates-fonemas'])

    fused_words = []
    if min_length > 3:
        LOCK.acquire()
        try:
            # http://stackoverflow.com/questions/8464391
            with Timeout(2):
                fused_words = _foma_string_lookup(word, 'split-words')
                if len(fused_words) > 0:
                    fused_words = _select_non_fused_words(fused_words)
        except Timeout.Timeout:
            fused_words = []
            _switch_flookup_server('split-words', mode='on')
        LOCK.release()

    LCSR = .55
    if min_length == 2:
        LCSR = .5

    target_words = _filter_out_acronyms(normalised_variants,
        np.unique(target_words).tolist(),
        max_length)

    target_words = _filter_target_words_based_on_LCSR(word, target_words, LCSR)
    target_words += oov_candidates

    return np.unique(target_words).tolist() + np.unique(fused_words).tolist()


def _switch_normalisation_services(mode='on'):
    '''Inicia/termina los servicios requeridos por el modelo.'''
    _switch_flookup_server(mode=mode)
    _switch_freeling_server(mode=mode)


class SpellTweet(object):
    '''Analiza el texto del tweet e identifica OOV-words y sugiere correctas.'''
    def __init__(self, external_dicc_ip=None, external_dicc_port=None):
        """Instancia un modelo de normalización léxica.

        paráms:
            external_dicc_ip: str
                Dirección IP (v4) del diccionario de normalización dependiente
                de contexto. Nótese que tal diccionario es externo. (Véase [1]).
            external_dicc_port: str
                Puerto por medio de cual se reciben las solicitudes para el di-
                ccionario de normalización.

        [1] `external_dicc_ip´ y `external_dicc_port´ permiten especificar un
        diccionario de normalización dependiente de contexto, es decir, externo.
        Tal diccionario corresponde a un transductor de estado finito que reci-
        be solicitudes por medio de una instancia de servidor.
        """
        self.language_model = kenlm.LanguageModel(CORPORA['eswiki-corpus-3-grams'])

        self.external_dicc = None
        if external_dicc_ip is not None and external_dicc_port is not None:
            self.external_dicc = {
                'external-dicc': [None, external_dicc_ip, external_dicc_port],}


    def list_oov_words(self, morphological_analysis, include_PND=True):
        """Lista las OOV-words identificadas.

        La identificación es dada porque, o bien la palabra no recibió
        ningún análisis, o es reconocida como nombre propio (su tag
        empieza por NP). Este segundo caso se da porque algunos tweets
        son escritos total o parcialmente en mayúscula.

        paráms:
            include_PND: bool
                indica si los PND identificados serán tratados como OOV-words.

        Retorna un array con la siguiente estructura:
            0 -> sentencia (u oración) en la que aparece.
            1 -> posición que ocupa en la sentencia.
            2 -> tipo de mayúscula/minúscula:
                (véase el método "_get_case_type_in_token")
                0 -> completamente en minúscula.
                1 -> con la inicial en mayúscula.
                2 -> totalmente o con la mayoría de sus letras en mayúscula.
            3 -> forma original de la palabra.
            4 -> forma en minúsculas de la palabra, decodificada a ASCII
                 si alguna de sus letras no es reconocida.
            5 -> indica si la palabra debe comenzar con mayúscula:
                    - si es el inicio de una oración
                    - si va después de un punto seguido,
                      o signos de interrogación o admiración
                    - si va después de puntos suspensivos, y la
                      oov-word empieza con mayúscula
        """
        oov_words = []
        starts_with_uppercase = False
        for i, sentence in enumerate(morphological_analysis):
            j, k = 0, 0
            for form, lemma, tag in sentence:
                if j == 0:
                    starts_with_uppercase = True

                # si el token anterior son puntos suspensivos, y el token actual
                # empieza en mayúscula, entonces la forma corregida, si se trata
                # de una oov, debe empezar con mayúscula
                if (k > 0 and morphological_analysis[i][k-1][2].startswith(u'F')
                        and re.match(r'\.{3,}$', morphological_analysis[i][k-1][0], re.U)
                        and form[0].upper() == form[0]):
                    starts_with_uppercase = True

                if lemma == '' and tag == '':
                    oov_words.append([i, j, _get_case_type_in_token(form),
                        form, _normalize_unknown_symbols(form).lower(),
                        starts_with_uppercase])
                    starts_with_uppercase = False
                elif (include_PND and tag.startswith('NP')
                        and not re.match('(?:#|@)', form, re.U)):
                    for token in form.split('_'):
                        # si el token está en minúscula y está en el
                        # diccionario, descartarlo
                        if (token.lower() == token and
                                len(_foma_string_lookup(token, 'es-dicc')) == 1):
                            j += 1
                            starts_with_uppercase = False
                            continue

                        oov_words.append([i, j, _get_case_type_in_token(token),
                            token, _normalize_unknown_symbols(token).lower(),
                            starts_with_uppercase])

                        j += 1
                        starts_with_uppercase = False

                    j -= 1
                elif tag.startswith(u'F'):
                    if tag.lower() in [u'fat', u'fit', u'fp']:
                        starts_with_uppercase = True
                else:
                    starts_with_uppercase = False

                j += 1
                k += 1

        # Si la oov-word inicia en mayúscula (o inclusive, está completamente en
        # mayúscula), y es encontrada en el diccionario, se deja a ella misma.
        for i, oov_word in enumerate(oov_words):
            if oov_word[2] == 0:
                continue

            search = _transducers_cascade(
                oov_word[3].lower(),
                ['dictionary_lookup', 'es-dicc'])
            if len(search) == 0:
                # búsqueda de pronombre enclítico
                affixes_search = _check_affixes(
                    oov_word[3].lower(), [oov_word[3].lower()],
                    affix='suffix', what_affix='enclitic')
                if (oov_word[3].lower() in affixes_search
                        and len(affixes_search) == 1):
                    search.append(oov_word[3].lower())
                # busqueda de adverbios terminados en -mente
                search += _check_affixes(
                    oov_word[3].lower(), [oov_word[3].lower()],
                    affix='suffix', what_affix='mente')

            search =_filter_target_words_by_length(search)
            if (len(search) == 1
                    and _to_unicode(search[0]).lower() == oov_word[3].lower()):
                oov_words[i].append([oov_word[3].lower()])
                oov_words[i][2] = 0
                if oov_words[i][5]:
                    oov_words[i][6][0] = _recover_original_word_case_from_type(
                        oov_words[i][6][0], 1)

        return oov_words


    def select_candidates(self, analysis, oov_words):
        '''Selecciona los mejores candidatos.'''
        tweet = u''

        j = 1
        for i, sentence in enumerate(analysis):
            for form, lemma, tag in sentence:
                if len(tag) == 0:
                    tweet = tweet + u' ' + (u'{OOV-%d}' % j) + u' '
                    j += 1
                elif tag.startswith(u'NP') and not form.startswith((u'#', u'@')):
                    for token in form.split('_'):
                        if (token.lower() == token
                                and len(_foma_string_lookup(token, 'es-dicc')) == 1):
                            tweet = tweet + u' ' + token + u' '
                        else:
                            tweet = tweet + u' ' + (u'{OOV-%d}' % j) + u' '
                            j += 1
                elif form.startswith((u'#', u'@')) or not tag.startswith(u'F'):
                    if tag.startswith((u'Z', u'W')):
                        form = re.sub(
                            u"""[^a-z\xe1\xe9\xed\xf3\xfa\xfc\xf1_]""", '',
                            form, flags=re.I|re.U)
                        if len(form) < 2:
                            continue
                    elif not tag.startswith(u'NP'):
                        form = form.lower()
                    tweet = tweet + u' ' + form + u' '

        tweet = tweet.strip().replace(u'  ', u' ').replace(u'jajaja', u'ja')

        param_grid = {}
        for i, oov_word in enumerate(oov_words):
            if len(oov_word[6]) == 1 and oov_word[6][0] != '%EMO':
                tweet = tweet.replace(u'{OOV-%d}' % (i + 1), oov_word[6][0])
            elif len(oov_word[6]) == 1:
                tweet = tweet.replace(u'{OOV-%d}' % (i + 1), oov_word[3])
                oov_words[i][6] = [oov_word[3]]
            else:
                param_grid['OOV-%i' % (i + 1)] = np.unique(oov_word[-1]).tolist()

        grid = ParameterGrid(param_grid)
        complete_search = True
        best_combination = []
        max_ppl_value = 1000
        for i, combination in enumerate(grid):
            if i == 100000:
                complete_search = False
                break
            t = tweet

            for oov_id, candidate in combination.iteritems():
                t = t.replace('{' + oov_id + '}', candidate.replace('_', ' '))

            # si solo se va a normalizar un token, des-
            # activar el inicio y fin de la oración
            bos = True
            eos = True

            if len(t.split(' ')) == 1:
                bos = False
                eos = False

            ppl_value = self.language_model.score(t, bos=bos, eos=eos)

            if max_ppl_value == 1000 or ppl_value > max_ppl_value:
                best_combination = combination
                max_ppl_value = ppl_value
        else:
            for oov, candidate in best_combination.iteritems():
                oov_id = int(oov.split('-')[1]) - 1
                idx = oov_words[oov_id][6].index(candidate)
                oov_words[oov_id][6] = [oov_words[oov_id][6][idx]]

        if not complete_search:
            for i in xrange(len(oov_words)):
                if len(oov_words[i][6]) == 1:
                    continue
                t = tweet
                for j in xrange(len(oov_words)):
                    if i == j:
                        continue
                    elif len(oov_words[j][6]) > 1:
                        t = t.replace('{OOV-%i}' % (j + 1), oov_words[j][3])
                ppl_values = np.zeros(len(oov_words[i][6]), dtype=float)
                for k, candidate in enumerate(oov_words[i][6]):
                    ppl_values[k] = self.language_model.score(
                        t.replace('{OOV-%i}' % (i + 1), candidate))
                best_candidate_idx = np.argmax(ppl_values)
                oov_words[i][6] = [oov_words[i][6][best_candidate_idx]]
                tweet = tweet.replace('{OOV-%i}' % (i + 1), oov_words[i][6][0])

        # Mayúsculas: a continuación se identifica la forma correcta de la
        # palabra candidata seleccionada, según mayúsculas y minúsculas.
        # Las siguientes son las reglas:
        #   1. Si la palabra candidata seleccionada empieza por mayúscula (o in-
        #      clusive, está completamente en mayúscula), así se mantiene.
        #   2. Si la palabra candidata seleccionada está en minúscula, no está
        #      en el diccionario de formas estándar y corresponde a la misma
        #      oov-word, y no , se recupera las mayúscula según como estaba ori-
        #      ginalmente.
        #   3. Si la palabra candidata seleccionada está en minúscula, y es di-
        #      ferente de la oov-word, se recuperará su mayúscula si está
        #      al inicio de la oración, después de un punto seguido o signos de
        #      puntación o interrogación.

        # Aplicación de la reglas
        # (Note que la primera no es necesario implementarla)
        for i, oov_word in enumerate(oov_words):
            if (oov_word[3].lower() == oov_word[6][0]):
                if len(_foma_string_lookup(oov_word[6][0], 'es-dicc')) == 0:
                    # segunda regla
                    oov_words[i][6][0] = _recover_original_word_case_from_type(
                        oov_word[6][0], oov_word[2])
                elif oov_word[5]:
                    oov_words[i][6][0] = _recover_original_word_case_from_type(
                        oov_word[6][0], 1)
            elif (oov_word[3].lower() != oov_word[6][0]
                    and oov_word[6][0].lower() == oov_word[6][0]
                    and oov_word[5]):
                # tercera regla
                oov_words[i][6][0] = _recover_original_word_case_from_type(
                    oov_word[6][0], 1)

        return oov_words


    def spell_tweet(self, text):
        '''Analiza léxicamente un tweet y lo corrige, si es necesario.

        paráms:
            text: str
                Texto del tweet.
            only_suggest_candidates: bool
                Si es verdadero, sólo retorna las candidatas por cada OOV
                identificada.

        salida:
            candidatas_seleccionadas: list
                Arreglo con las oov-words identificadas y las candidatas
                seleccionadas. Un arrego por cada OOV, siendo la estruc-
                tura la siguiente:
                    0, sentencia (u oración) en la que aparece.
                    1, posición que ocupa en la sentencia.
                    2, forma original de la palabra.
                    3, candidata seleccionada.
                    4, candidatas sugeridas.
        '''
        if text=='':
            raise Exception('Debe especificar un texto a normalizar')
        else:
            text = _to_unicode(text)

        analysis = _analyze_morphologically(text)
        oov_words = self.list_oov_words(analysis)

        # por cada palabra fuera de vocabulario, proponer candidatas
        pool = multiprocessing.Pool(processes=4)
        candidates = [
            [i, pool.apply_async(_suggest_target_words, [oov_word[4], oov_word[2], self.external_dicc])]
             for i, oov_word in enumerate(oov_words) if len(oov_word) == 6]
        pool.close()
        pool.join()

        normalisation_candidates = {}
        for i, target_words in candidates:
            try:
                oov_words[i].append(target_words.get(timeout=3))
            except (ValueError, multiprocessing.TimeoutError):
                oov_words[i].append(
                    np.unique([
                        oov_words[i][3],
                        oov_words[i][4],
                        _recover_original_word_case_from_type(
                            oov_words[i][4], oov_words[i][2])
                    ]).tolist())
                _switch_flookup_server(mode='on')
            normalisation_candidates[i] = oov_words[i][6]

        oov_words = self.select_candidates(analysis, oov_words)

        for i, oov in enumerate(oov_words):
            if i not in normalisation_candidates.keys():
                normalisation_candidates[i] = []
            oov_words[i] = [oov[0], oov[1], oov[3], oov[6][0],
                np.unique(normalisation_candidates[i] + oov[6]).tolist()]

        return oov_words

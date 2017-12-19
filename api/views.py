# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os, re, sys

import pickle

from rest_framework.decorators import api_view
from rest_framework.response import Response


CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

BASE_PATH = '/'.join(CURRENT_PATH.split('/')[:-1] + ['normalesp',])

sys.path.append(BASE_PATH)

from spell_checking import SpellTweet, _to_str


@api_view(['POST'])
def spell_checking(request):
    """Vista principal de la API.

    paráms:
        text: str
            Texto que se normalizará.
        external_dicc_ip: str
            Dirección IP (v4) del diccionario de normalización dependiente de
            contexto. Nótese que tal diccionario es externo.
        external_dicc_port: str
            Puerto por medio de cual se reciben las solicitudes para el diccio-
            nario de normalización.
        return_normalized_text: boolean
            Indica si se retorna el texto normalizado en vez del arreglo de pa-
            labras fuera de vocabulario.
    """
    spell = None
    if ('external_dicc_ip' in request.data
            and request.data['external_dicc_ip'] is not None
            and 'external_dicc_port' in request.data
            and request.data['external_dicc_port'] is not None):
        spell = SpellTweet(external_dicc_ip=request.data['external_dicc_ip'],
            external_dicc_port=request.data['external_dicc_port'])
    else:
        spell = SpellTweet()

    oov_words = spell.spell_tweet(text=request.data['text'])

    # verificar si se solicitó retornar el texto normalizado
    if ('return_normalized_text' in request.data
            and request.data['return_normalized_text']):
        # convertir el texto a unicode
        text = request.data['text']
        text = text.decode('utf-8') if not isinstance(text, unicode) else text
        for oov in oov_words:
            text = re.sub(r'(\A|\W)' + oov[2],
                          r'\1' + oov[3].replace('_', ' '),
                          text,
                          count=1, flags=re.U)
        return Response({"text": text})
    else:
        return Response(oov_words)

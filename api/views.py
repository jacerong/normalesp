# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os, sys

import pickle

from rest_framework.decorators import api_view
from rest_framework.response import Response


CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

BASE_PATH = '/'.join(CURRENT_PATH.split('/')[:-1] + ['normalesp',])

sys.path.append(BASE_PATH)

from spell_checking import SpellTweet, _to_str


@api_view(['POST'])
def spell_checking(request):
    spell = SpellTweet()
    oov_words = spell.spell_tweet(text=request.data['text'])
    return Response(oov_words)

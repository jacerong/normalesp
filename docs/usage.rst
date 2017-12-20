How to Use
==========

Before using the ``SpellTweet`` class located in the ``/normalesp/spell_checking.py`` file, which is the main one, please make sure the required services are running. To do that, change directory to ``/normalesp/``, open a new terminal, and type the following instructions::

    $ python
    >>> from spell_checking import _switch_normalisation_services
    >>> _switch_normalisation_services('on')

It is strongly recommended **NOT** to close this terminal or type other Python instructions.

To stop the services, please type the following instruction::

    >>> _switch_normalisation_services('off')

On the other hand, there are two methods to use the spell checking program. The first one is to import the ``SpellTweet`` class as a Python module, while the second one is through a REST request. Whichever method is chosen, the first request will take a while because the language model is loaded in memory; there will be no delay from the second request.

As a result, the program returns an array of 1-dimensional arrays, where each 1-dimensional array represents one *out-of-vocabulary* (OOV) token whose structure is described through the following example.

Let the tweet be

    Qué te pasa a ti con Iker? Diego y valdés lo estarán haciendo bien, pero que rápido olvidamos. A Mou le falta humildad.

    ``(What's wrong with Iker? Diego and Valdés are doing it well, but We forget fast. Mou lacks humility.)``

and the array ``oov_words`` be the result of the spell checker,

::

    >>> oov_words
    [[0, 6, u'Iker', u'Iker', [u'Iker', u'iker']],
     [1, 0, u'Diego', u'Diego', [u'Diego']],
     ...,
     [2, 1, u'Mou', u'Mou', [u'Mou', u'mou']]]
    >>> oov_words[0]
    [0, 6, u'Iker', u'Iker', [u'Iker', u'iker']]
    >>> oov_words[0][4]
    [u'Iker', u'iker']

the following explanation can be deduced:

1. ``oov_words[i]`` is a 1-dimensional array representing the *i*-th OOV token.
2. ``oov_words[i][0]`` is the sentence (0-based index) where the OOV token is in.
3. ``oov_words[i][1]`` is the token-based position (0-based index) in which the OOV token is.
4. ``oov_words[i][2]`` is the OOV token.
5. ``oov_words[i][3]`` is the selected normalization candidate.
6. ``oov_words[i][4]`` is the set of normalization candidates.

Having said the above, the methods to use the spell checking program are described.

**1. Use the Spell Checking Program as a Python Module**

::

    >>> from spell_checking import SpellTweet
    >>> tweet = """Qué te pasa a ti con Iker? Diego y valdés lo estarán haciendo bien, pero que rápido olvidamos. A Mou le falta humildad."""
    >>> spell = SpellTweet()
    >>> oov_words = spell.spell_tweet(tweet)
    >>> oov_words
    [[0, 6, u'Iker', u'Iker', [u'Iker', u'iker']],
     [1, 0, u'Diego', u'Diego', [u'Diego']],
     ...,
     [2, 1, u'Mou', u'Mou', [u'Mou', u'mou']]]

**2. REST API**

A REST API has been developed using `Django <https://www.djangoproject.com/>`_ and the `Django REST framework <http://www.django-rest-framework.org/>`_.[#]_ The idea is to enable application integration using REST. It is important to note that server setup is beyond the scope of this document, so it is assumed that the REST API is running (please see [#]_ and [#]_).

Requests can be sent to the REST API using the ``curl`` command-line utility:

::

    $ curl -w --data 'text="Qué te pasa a ti con Iker? Diego y valdés lo estarán haciendo bien, pero que rápido olvidamos. A Mou le falta humildad."' http://127.0.0.1:8000/api/spell_checking/

In the same way, requests can be sent using the Python's ``requests`` module.

::

    >>> import json, requests
    >>> tweet = """Qué te pasa a ti con Iker? Diego y valdés lo estarán haciendo bien, pero que rápido olvidamos. A Mou le falta humildad."""
    >>> head = {"Content-type": "application/json"}
    >>> data = json.dumps({'text': tweet})
    >>> r = requests.post("http://127.0.0.1:8000/api/spell_checking/", data=data, headers=head)
    >>> oov_words = json.loads(r.content)
    >>> oov_words
    [[0, 6, u'Iker', u'Iker', [u'Iker', u'iker']],
     [1, 0, u'Diego', u'Diego', [u'Diego']],
     ...,
     [2, 1, u'Mou', u'Mou', [u'Mou', u'mou']]]

.. [#] As a default setting, the REST API will deny permission to any unauthenticated user. To allow unrestricted access, the following line in the ``/api/views.py`` file::

    @permission_classes((IsAuthenticated, ))

    should be changed by::

    @permission_classes((AllowAny, ))

.. [#] For testing purposes, you can use the Django's `runserver <https://docs.djangoproject.com/en/1.11/ref/django-admin/#runserver>`_ utility.
.. [#] The author recommends `this <https://www.howtoforge.com/tutorial/how-to-install-django-with-postgresql-and-nginx-on-ubuntu-16-04/>`_ tutorial to setup a server using Gunicorn, Supervisor, and Nginx.

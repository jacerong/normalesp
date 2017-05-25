# -*- coding: iso-8859-15 -*-


import os, re, sys, time

import numpy as np
from prettytable import PrettyTable


CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

BASE_PATH = '/'.join(CURRENT_PATH.split('/')[:-1])

sys.path.append(BASE_PATH)

from spell_checking import SpellTweet, _to_str, _to_unicode


def _write_in_file(fname, content, mode='a'):
    with open(fname, mode) as f:
        f.write(content)


def performance_custom_evaluation(corpus_fname):
    """Realiza una evaluación personalizada del desempeño del sistema."""
    spell = SpellTweet()

    num_tweets = 0
    num_oov_words = 0
    num_detected_oov_words = 0
    num_undetected_oov_words = 0

    candidate_coverage = 0
    positives = 0
    negatives = 0
    negatives_for_misuppercasing = 0

    tweet_id = ''
    oov_words = {}
    flat_oov_words = []
    oov_words_idx_used = []
    matching = {}
    gold_standard = {}
    i = 0
    with open(corpus_fname) as f:
        for line in f:
            line = line.rstrip('\n')

            if len(line.strip()) == 0:
                continue

            m = re.match(r'([0-9]{4,})', line)
            if m:
                num_tweets += 1

                tweet_id = m.group(1)

                text = re.sub(tweet_id, '', line).strip()
                oov_words[tweet_id] = spell.spell_tweet(text=text)

                flat_oov_words = np.array([
                    oov[2] for oov in oov_words[tweet_id]], dtype=unicode)
                oov_words_idx_used = []

                matching[tweet_id] = []
                gold_standard[tweet_id] = []

                i = 0
            else:
                line = line.strip()

                num_oov_words += 1

                m = re.match(r'([^ ]+) ([0-9]) ([^ ]+)', line)
                oov_word = _to_unicode(m.group(1))
                type_error = _to_unicode(m.group(2))
                normalization = m.group(3) if type_error == '0' else oov_word
                normalization = _to_unicode(normalization).split('_|_')

                gold_standard[tweet_id].append([oov_word, normalization])

                # emparejar la gold standard OOV con la detectada por el sistema
                search = list(np.where(flat_oov_words == oov_word)[0])
                idx = np.setdiff1d(search, oov_words_idx_used)

                if (len(search) > 0 and idx.shape[0] > 0):
                    matching[tweet_id].append([i, idx[0]])
                    oov_words_idx_used.append(idx[0])
                else:
                    num_undetected_oov_words += 1

                i += 1

    for tweet_id in gold_standard.iterkeys():
        gold = gold_standard[tweet_id]
        prediction = oov_words[tweet_id]

        _write_in_file(CURRENT_PATH + '/resultFile.txt', '%s\n' % tweet_id)

        m = matching[tweet_id]
        num_detected_oov_words += len(m)

        for i, j in m:
            gold_oov = gold[i]
            predicted_oov = prediction[j]

            _write_in_file(CURRENT_PATH + '/resultFile.txt',
                '\t%s %s\n' % (_to_str(predicted_oov[2]), _to_str(predicted_oov[3]))
                )

            is_a_correct_proposal = False

            if predicted_oov[3] in gold_oov[1]:
                positives += 1
                is_a_correct_proposal = True
            else:
                negatives += 1

            _write_in_file(CURRENT_PATH + '/results.txt',
                '%s\t%s\t%s\t%s\n' % ('POS' if is_a_correct_proposal else 'NEG',
                    _to_str(predicted_oov[2]),
                    _to_str(predicted_oov[3]), _to_str('_|_'.join(gold_oov[1]))
                    )
                )

            if np.intersect1d(gold_oov[1], predicted_oov[4]).shape[0] > 0:
                candidate_coverage += 1

    # computar métricas derivativas
    recall_OOV = round(num_detected_oov_words / float(num_oov_words), 4)
    candidate_coverage = round(
        float(candidate_coverage) / num_detected_oov_words, 4)
    precision = round(float(positives) / num_detected_oov_words, 4)
    recall = round(float(positives) / num_oov_words, 4)
    f1_measure = round((2 * precision * recall) / (precision + recall), 4)

    tabular = PrettyTable(['Item', 'Metric', 'Value'])

    tabular.align['Item'] = 'l'
    tabular.align['Metric'] = 'l'

    tabular.add_row(['Tweets', 'Count', num_tweets])
    tabular.add_row(['OOV words', 'Count', num_oov_words])
    tabular.add_row(['Detected OOV words', 'Count', num_detected_oov_words])
    tabular.add_row(['Detected OOV words', 'Recall', recall_OOV])
    tabular.add_row(['Candidate coverage', 'Precision', candidate_coverage])
    tabular.add_row(['Positives', 'Count', positives])
    tabular.add_row(['Negatives', 'Count',
        negatives + negatives_for_misuppercasing])
    #tabular.add_row(['    ...for misuppercasing', 'Count',
    #    negatives_for_misuppercasing])
    tabular.add_row(['Candidate selection', 'Precision', precision])
    tabular.add_row(['Candidate selection', 'Recall', recall])
    tabular.add_row(['Candidate selection', 'F1-Measure', f1_measure])

    _write_in_file(CURRENT_PATH + '/results.txt',
        'OOV: %i\n' % num_oov_words)
    _write_in_file(CURRENT_PATH + '/results.txt',
        'OOV (detected): %i\n' % num_detected_oov_words)
    _write_in_file(CURRENT_PATH + '/results.txt',
        'POS: %i\n' % positives)
    _write_in_file(CURRENT_PATH + '/results.txt',
        'NEG: %i\n' % negatives)
    _write_in_file(CURRENT_PATH + '/results.txt',
        'Precision: %.2f\n' % (precision * 100))
    _write_in_file(CURRENT_PATH + '/results.txt',
        'Recall: %.2f\n' % (recall * 100))
    _write_in_file(CURRENT_PATH + '/results.txt',
        'F1-Measure: %.2f\n' % (f1_measure * 100))

    print tabular


if __name__ == '__main__':
    performance_custom_evaluation(CURRENT_PATH +'/Tweet-Norm_es/tweet-norm-test462_annotated.txt')

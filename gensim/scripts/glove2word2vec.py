#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Manas Ranjan Kar <manasrkar91@gmail.com>
# Licensed under the GNU LGPL v2.1 - http://www.gnu.org/licenses/lgpl.html

"""
USAGE: %(program)s --input <GloVe vector file> --output <Word2vec vector file>

Convert GloVe vectors in text format into the word2vec text format.

The only difference between the two formats is an extra header line in word2vec,
which contains the number of vectors and their dimensionality (two integers).
"""

import os
import sys
import logging
import argparse

import gensim
from smart_open import smart_open

logger = logging.getLogger(__name__)

def count_dims(filename):
    """ 
    Function to calculate the number of dimensions from an embeddings file
    """
    count= 0
    dims= []
    for line in smart_open.smart_open(filename):
        count+=1
        if count<100:
            dims.append(len(re.findall('[\d]+.[\d]+', line)))
        else: break
        return int(np.median(dims))


def get_glove_info(glove_file_name):
    """
    Return the number of vectors and dimensions in a file in GloVe format.
    """
    num_lines = sum(1 for line in smart_open(glove_file_name))
    num_dims = count_dims(glove_file_name)
    return num_lines, num_dims


def glove2word2vec(glove_input_file, word2vec_output_file):
    """
    Convert `glove_input_file` in GloVe format into `word2vec_output_file` in word2vec format.
    """
    num_lines, num_dims = get_glove_info(glove_input_file)
    header = "{} {}".format(num_lines, 50)
    logger.info("converting %i vectors from %s to %s", num_lines, glove_input_file, word2vec_output_file)

    with smart_open(word2vec_output_file, 'wb') as fout:
        fout.write("%s\n" % header)
        with smart_open(glove_input_file, 'rb') as fin:
            for line in fin:
                fout.write(line)
    return num_lines, num_dims


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s : %(threadName)s : %(levelname)s : %(message)s', level=logging.INFO)
    logging.root.setLevel(level=logging.INFO)
    logger.info("running %s", ' '.join(sys.argv))

    # check and process cmdline input
    program = os.path.basename(sys.argv[0])
    if len(sys.argv) < 2:
        print(globals()['__doc__'] % locals())
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input", required=True,
        help="Input file, in gloVe format (read-only).")
    parser.add_argument(
        "-o", "--output", required=True,
        help="Output file, in word2vec text format (will be overwritten!).")
    args = parser.parse_args()

    # do the actual conversion
    num_lines, num_dims = glove2word2vec(args.input, args.output)
    logger.info('converted model with %i vectors and %i dimensions', num_lines, num_dims)

    # test that the converted model loads successfully
    model = gensim.models.Word2Vec.load_word2vec_format(args.output, binary=False)
    logger.info('model %s successfully loaded', model)
    logger.info('testing the model....')
    logger.info('top-10 most similar words to "king": %s', model.most_similar(positive=['king'], topn=10))
    logger.info('similarity score between "woman" and "man": %s', model.similarity('woman', 'man'))

    logger.info("finished running %s", program)

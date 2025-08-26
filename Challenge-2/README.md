# Approach Report – Classical English Text Simplification

## 1. Data Collection Method

The dataset was created by collecting pairs of sentences in three areas: medicine, law, and technology. Each pair includes:

Original sentence: which contains specialized or complex vocabulary.

Simplified sentence: a rewritten version in plain English that keeps the original meaning.

The dataset has about 2,000 sentence pairs, split 80/20 for training and testing. The training set was used to find common word and phrase mappings, while the test set evaluated the simplification performance using BLEU as the main metric.

## 2. Non-Neural Approach Chosen

A rule-based and lexicon-driven method was used, with three main parts:

Word-level Mapping:

The most common complex to simple word pairs were taken from the training set (top 500).

Replacements are applied directly if the complex word appears in the input sentence.

Phrase-level Mapping:

Common multi-word expressions (bigrams and trigrams) from the training set were taken (top 200).

Phrase replacements are applied before word-level substitutions to maintain context and avoid partial replacements.

WordNet Fallback:

For words not in the lexicon, synonyms from WordNet are used.

Preference is given to simpler, shorter synonyms.

Rationale:
This method avoids neural models while using observed simplification patterns in the data. It is clear and understandable and requires no pretraining. Using both word and phrase mappings ensures coverage of frequent substitutions and multi-word expressions, which is important for improving BLEU scores on the test set.

## 3. Challenges and Lessons Learned

Challenges:

Ambiguity in WordNet synonyms: Not all synonyms match the human reference simplifications, which sometimes reduces BLEU.

Phrase overlaps: Multi-word expressions sometimes conflicted with word-level mappings, requiring careful ordering of replacements.

Limited coverage: Even with the top 500 words and top 200 phrases, many complex words in the test set were not included in training, limiting performance.

## Lessons Learned:

Rule-based systems can achieve reasonable BLEU (about 0.47) without neural models, but there is a limit due to the inability to generalize beyond the observed training examples.

Phrase-level mappings greatly improve BLEU compared to word-level replacements alone.

Combining lexicon-based substitutions with WordNet fallbacks provides a backup for unseen words, maintaining readability without major meaning changes.

## Conclusion:
The classical, non-neural pipeline shows that structured, clear rules and data-driven lexicons can effectively simplify text on a limited dataset. However, further improvements in BLEU would need either neural sequence-to-sequence modeling or extensive manual curation of additional mappings.

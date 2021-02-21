from enum import Enum
from typing import List, Tuple

import pandas as pd
import numpy as np

import spacy
from spacy.tokens import Token
from spacy_sentiws import spaCySentiWS

import re

class Topic(Enum):
    PREIS = 'Preis/ Preis-Leistung'
    BEDIENUNG = 'Bedienung'
    DESIGN = 'Design'
    REINIGUNG = 'Reinigung'
    WASSER = 'Wasserbehälter/ Wasser'
    KAPSEL = 'Kapsel'
    LIEFERUNG = 'Lieferung'
    QUALITAET = 'Qualität'
    GESCHMACK = 'Geschmack'
    TASSE = 'Tasse'
    AUSWAHL = 'Auswahl/ Sortiment'
    SONSTIGES = 'Sonstiges'


class LexiconEntry:

    def __init__(self, lemma: str, topic: Topic):
        assert lemma is not None
        self.lemma = lemma
        self._lower_lemma = lemma.lower()
        self.topic = topic

    def matches(self, token: Token) -> bool:
        assert token is not None
        if token.text == self.lemma:
            return True
        if token.text.lower() == self.lemma:
            return True
        if token.lemma_ == self.lemma:
            return True
        if token.lemma_.lower() == self._lower_lemma:
            return True
        if self.lemma in token.text:
            return True
        if  self.lemma in token.text.lower():
            return True
        if self.lemma in token.lemma_ :
            return True
        if self._lower_lemma in token.lemma_.lower()  :
            return True
        else:
            return False

    def __str__(self) -> str:
        return 'LexiconEntry({}: {})'.format(self.lemma, self.topic.value)

    def __repr__(self) -> str:
        return self.__str__()


class Lexicon:
    def __init__(self):
        self.entries: List[LexiconEntry] = []
    
    def append(self, lemma: str, topic: Topic):
        lexicon_entry = LexiconEntry(lemma, topic)
        self.entries.append(lexicon_entry)

    def lexicon_entry_for(self, token: Token) -> LexiconEntry:
        """
        Entry in lexicon that best matches ``token``.
        """
        result = None
        lexicon_size = len(self.entries)
        lexicon_entry_index = 0
        entry_found = False
        while not entry_found and lexicon_entry_index < lexicon_size:
            lexicon_entry = self.entries[lexicon_entry_index]
            matches = lexicon_entry.matches(token)
            if matches:
                result = lexicon_entry
                entry_found = True
            else:    
                lexicon_entry_index += 1
        return result

# Helper class for analysis
class SentimentAnalyzer:

    # Helper Function to split documents at the words "aber" and "und" and at semicolons and commas.
    def set_custom_sentence_end_points(self, doc):
        for token in doc[:-1]:
            if token.text == ';' or token.text == ',':
                doc[token.i+1].is_sent_start = True
            if token.text == 'und' or token.text == 'aber':
                doc[token.i].is_sent_start = True
        return doc

    def __init__(self, lexicon, model):
        self.lexicon = lexicon
        # Initialize large German spaCy model and add spaCy SentiWS
        self.nlp = model
        sentiws = spaCySentiWS(sentiws_path='/SentiWS_v2.0')
        if self.nlp.has_pipe('spaCySentiWS'):
            self.nlp.remove_pipe('spaCySentiWS')
        self.nlp.add_pipe(sentiws)
        
        # Add custom spaCy rule for sentence segmentation because sentences should also be split at the words "aber" and "und" and at semicolons and commas.
        if self.nlp.has_pipe('set_custom_sentence_end_points'):
            self.nlp.remove_pipe('set_custom_sentence_end_points')
        self.nlp.add_pipe(self.set_custom_sentence_end_points, before='parser')

        # Extend the spaCy Token with new extensions to get information if the token has a topic, is an intensifier, diminisher or negation.
        Token.set_extension('topic', default=None, force=True)
        Token.set_extension('is_negation', default=False, force=True)
        Token.set_extension('is_intensifier', default=False, force=True)
        Token.set_extension('is_diminisher', default=False, force=True)

        # Add a function to the spaCy pipeline to set the new extensions for each token (topic, intensifier, diminisher, negation)
        if self.nlp.has_pipe('opinion_matcher'):
            self.nlp.remove_pipe('opinion_matcher')
        self.nlp.add_pipe(self.opinion_matcher)

    """ 
        Creating a list of german intensifying and diminishing words. The words are from these sources: 
            - study.com
            - germanenthusiast.tumblr.com
            - mein-deutschbuch.de
        Maybe there are more and better lists on the internet. This was just the resut after a quick research.
    """
    def is_intensifier(self, token: Token) -> bool:
        INTENSIFIERS = {
            'total', 
            'gross', 
            'intensiv', 
            'hoch', 
            'höchst', 
            'groß', 
            'ausgesprochen', 
            'extrem', 
            'äusserst', 
            'schrecklich', 
            'sehr', 
            'widerlich', 
            'wirklich', 
            'leidenschaftlich', 
            'super', 
            'wahnsinnig', 
            'vollkommen', 
            'besonders', 
            'ziemlich', 
            'unvermindert', 
            'doll', 
            'viel', 
            'verdammt', 
            'praktisch', 
            'furchtbar', 
            'ganz', 
            'klasse', 
            'entsetzlich', 
            'äußerst', 
            'riesig', 
            'arg', 
            'richtig', 
            'grässlich', 
            'komplett', 
            'enorm', 
            'bestimmt', 
            'absolut', 
            'überaus', 
            'fürchterlich', 
            'sicher', 
            'exzeptionell', 
            'ständig', 
            'echt', 
            'erheblich', 
            'steigern', 
            'unglaublich', 
            'bleiben', 
            'tatsächlich', 
            'zusätzlich', 
            'brutal', 
            'irre', 
            'unheimlich', 
            'völlig', 
            'tierisch', 
            'maximal', 
            'recht'
        }
        return token.lemma_.lower() in INTENSIFIERS
  
    def is_diminisher(self, token: Token) -> bool:
        DIMINISHERS = {
            'beinahe',
            'einigermaßen',
            'etwas',
            'ganz',
            'halbwegs',
            'kaum',
            'recht',
            'relativ',
            'vergleichsweise',
            'völlig'
        }
        return token.lemma_.lower() in DIMINISHERS

    # Build a list of german negation words.
    def is_negation(self, token: Token) -> bool:
        NEGATIONS = {
            'keineswegs',
            'keinerweise',
            'keinsterweise',
            'net',
            'nich',
            'nicht',
            'nichts',
            'kein',
            'keinen',
            'keine',
            'können',
            'sollen',
            'dürfen',
            'nix',
            'nie'
        }
        return token.lemma_.lower() in NEGATIONS

    #  Helper preprocessing function to remove unwanted digits from sentences (punctuation, numbers)
    def preprocess_text(self, text):
        text = re.sub(r"[\n\r\t]", " ", text)
        text = re.sub(r"\d+", "", text)
        text = re.sub(r"([,.!?;:]){2,}", r"\1", text)
        text = re.sub(r"[&]", " und ", text)
        text = re.sub(r"[_#*§$%/()=+<>@€]+", "", text)
        text = re.sub('([.,!?()])(\w)', r'\1 \2', text)
        text = re.sub('\s{2,}', ' ', text)
        text = text.strip()
        return text

    # Helper function to set the new extensions for each token (topic, intensifier, diminisher, negation)
    def opinion_matcher(self, doc):
        for sentence in doc.sents:
            for token in sentence:
                if self.is_intensifier(token):
                    token._.is_intensifier = True
                elif self.is_diminisher(token):
                    token._.is_diminisher = True
                elif self.is_negation(token):
                    token._.is_negation = True
                else:
                    lexicon_entry = self.lexicon.lexicon_entry_for(token)
                    if lexicon_entry is not None:
                        token._.topic = lexicon_entry.topic
        return doc

    # Helper filter functions to extract only relevant tokens from a sentence. These are tokens that belong to a topic, are intensifiers, diminishers or negations and/or have a sentiment.
    def is_essential(self, token: Token) -> bool:
        return token._.topic is not None \
            or token._.sentiws is not None \
            or token._.is_diminisher \
            or token._.is_intensifier \
            or token._.is_negation
        
    def essential_tokens(self, tokens):
        return [token for token in tokens if self.is_essential(token)]

    # Main function to extract the topic, sentiment and adjectives from a sentence. It uses the helper functions created before.
    def topic_and_rating_of(self, tokens: List[Token]) -> Tuple[Topic, float, List[str]]:
        result_topic = None
        result_rating = 0.0
        negate = False
        num_intensifiers = 0
        num_diminishers = 0
        opinion_essence = self.essential_tokens(tokens)
        for token in opinion_essence:
            # print(debugged_token(token))
            if (token._.topic is not None) and (result_topic is None):
                result_topic = token._.topic
            if (token._.sentiws is not None):
                result_rating += token._.sentiws
            if (token._.is_negation):
                negate = not(negate)
            if (token._.is_intensifier):
                num_intensifiers += 1
            if (token._.is_diminisher):
                num_diminishers += 1
        if (num_intensifiers > 0):
            for _ in range(num_intensifiers):
                result_rating *= 1.5
        if (num_diminishers > 0):
            for _ in range(num_diminishers):
                result_rating *= 0.5
        if (negate and result_rating != 0.0):
            result_rating *= -1.0
        if result_topic is None:
            result_topic = Topic.SONSTIGES
        adj_adv = [token.lemma_.lower() for token in tokens if token.pos_ in ['ADJ']]
        return result_topic.value, result_rating, adj_adv

    # Uber function to extract results from multiple sentences / a whole review
    def opinions(self, feedback_text: str):
        feedback_text = self.preprocess_text(feedback_text)
        feedback = self.nlp(feedback_text)
        for tokens in feedback.sents:
            yield(self.topic_and_rating_of(tokens), tokens)

    # Analyze reviews from a csv file return analysis output 
    def analyzeReviews(self, reviews):
        reviews_df = reviews.copy()
        reviews_df['SourceReviewId'] = reviews_df['ReviewId']

        reviews = []
        reviewTexts = []
        rating = []
        sources = []
        sourceReviewIds = []
        aspects = []
        sentiments = []
        adjs = []
        productNames = []
        createdAts = []

        # call function to analyze one review for every review text
        for index, review in reviews_df.iterrows():
            for sent in self.opinions(review['ReviewText']):
                aspects.append(sent[0][0])
                sentiments.append(sent[0][1])
                adjs.append(sent[0][2])
                reviews.append(sent[1].text.replace(',','').replace(';',':'))
                reviewTexts.append(review['ReviewText'].replace(';',':'))
                rating.append(review['Rating'])
                sources.append(review['Source'])
                sourceReviewIds.append(review['SourceReviewId'])
                productNames.append(review['ProductName'])
                createdAts.append(review['CreatedAt'])

        analysis_dict = {"SourceReviewId": sourceReviewIds, 'ReviewText': reviewTexts, 'Rating': rating, 'Source':sources ,  'Review':reviews ,  'Aspect':aspects ,'Sentiment':sentiments, 'Adj':adjs, 'ProductName': productNames, 'CreatedAt':createdAts  } 

        output_df = pd.DataFrame(analysis_dict)

        # add unique ID to each sentence
        output_df['1'] = 1
        output_df['sent_id'] = output_df['1'].cumsum()
        output_df['sent_id'] = ['S_'] + output_df['sent_id'].astype(str)
        output_df.drop(columns=['1'])

        # Create dataframe line for each adjective
        output_df = output_df.explode('Adj')
        ES = ('gutes', 'schönes', 'tolles', 'kleines', 'einziges', 'platzsparendes', 'kompaktes', 'stylisches', 'schlichtes', 'heißen', 'leckerer', 'schnellen', 'tollen', 'billigen', 'guter')
        E = ('einfache', 'kleine', 'schöne', 'leichte', 'gute', 'kompakte', 'richtige', 'unkomplizierte', 'perfekte', 'verständliche', 'praktische', 'günstige', 'normale', 'wunderbare', 'platzsparende', 'ideale', 'kurze', 'leckere', 'kinderleichte')
        output_df['Adj'] = np.where((output_df.Adj.isin(ES)), output_df['Adj'].str.slice(0, -2), output_df['Adj'])
        output_df['Adj'] = np.where((output_df.Adj.isin(E)), output_df['Adj'].str.slice(0, -1), output_df['Adj'])

        return output_df

from nltk.stem.wordnet import WordNetLemmatizer
from collections import Counter
import math
import re
import nltk

class TextToTopics:
    """
    This class is used to extract topics from textual content of the HTML document
    
    ...

    Attributes
    ----------
    content : list of strings. 
        Every element in this list is textual content from different nodes of HTML document
        
    Methods
    -------
    _get_pos(token)
        Takes in the token(word) of sentence and returns a character corresponding to its part of speech
    
    _lemmatize_content()
        Returns lemmatized form of the content
    
    _handle_period(sentence)
        This method replaces "." in the acronyms present in a sentence
    
    _handle_punctuation(self,sentence)
        This method replaces the punctuation marks with space " " and then removes duplicate 
        spaces between words
    
     _get_n_grams(n)
         This method takes the number of grams(n) as parameter and constructs n-grams from the content.
         
    pim_based_topics(n,number=None)
        This method extracts the topics out of the content based on the pointwise mutual information score.
        It takes in n (number of grams of tokens to be used) and number (number of top topics to be returned)
        
    pos_based_topics(n,number=None)
        This method extracts the topics out of the content based on the part of speech filtering and then 
        calculating the frequencies. It takes in n (number of grams of tokens to be used) and 
        number (number of top topics to be returned)
    
    
    """
    
    
    
    def __init__(self,content):
        """
        Parameters
        ----------
        content : list(str)
            Every element in this list is textual content from different nodes of HTML document
        """
        self._content = content
        
        
    def _get_pos(self,token):
        """This function returns a character depending on the part of the speech of the token passed to it.
            It returns 'n' if the part of speech is of type noun, 'v' if it is verb, 'r' if it is adverb, 'a' if 
            it is adjective, 's' if it is satelite adjective, else it returns 'n'
            
        Parameters
        ----------
        token : str
            token(word) from a sentence
        
        """
        tag = nltk.pos_tag([token])[0][1]
        if tag[0] == 'N':
            return 'n'
        elif tag[0] == 'V':
            return 'v'
        elif tag[0] == 'R':
            return 'r'
        elif tag[0] == 'J':
            return 'a'
        elif tag[0] == 'S':
            return 's'
        else:
            return 'n'
    
    
    def _lemmatize_content(self):
        """This method returns the lemmatized form of every statement in the content attribute. It tokenizes 
        every statement and then finds its part of speech and then passes it to the lemmatizer function. NLTK
        lemmatizer is used to lemmatize the tokens after which they are joined to form a statement.
        
        """
        total_content = self._content
        lmtzr = WordNetLemmatizer()
        content_lemmatized = []
        for content in total_content:
            content_lemmatized.append(" ".join([lmtzr.lemmatize(c.lower(),self._get_pos(c)) for c in content.split()]))
        return content_lemmatized
    
    
    def _handle_period(self,sentence):
        """This mehtod replaces all the periods "." in acronyms with empty string "" . The regex chceks for
        structures like M.B.A and changes it to MBA
        
        Parameters
        ----------
        sentence : str
            sentence from content
        
        
        """
        regex = r'(?:[A-Z]\.)+'
        for a in re.findall(regex,sentence):
            replaced = a.replace(".","")
            sentence = sentence.replace(a,replaced)
        return sentence
    
    
    def _handle_punctuation(self,sentence):
        """This method returns the statement with punctuations removed. Most of the punctuations are removed
        except for "'" as it is contained in certain words such as don't.
        
        Parameters
        ----------
        sentence : str
            sentence from content
        
        
        """
        sentence = re.sub(r'[!@#$%*()_+-=\[\]\{\}|\\:;",\<\>\.|"]+', ' ', sentence)
        sentence = re.sub(' +',' ',sentence)
        return sentence
        
            
    def _get_n_grams(self,n):
        """ This method constructs n-grams from the statements in the content.It takes the content attribute 
        of the class and then removes period from acronym like words. Then it separates individual statements 
        and then tokenizes them. We only keep the tokens that have part of speech as either noun, verb, adverb,
        adjective. The stop words are automatically removed as most of the stop words have part of speech other
        than the above mentioned. Then contiguous sets of tokens are extracted. For eg. given a sentence 
        "Sun rises in the east and sets in the west" would be first changed to "sun rise east set west" and then 
        n-grams tokens are formed for eg. 2grams such as "sun rise","rise east","east set","set west". It returns
        a list of such tokens.
        
        Parameters
        ----------
        n : int
            n in n-grams. Specifies how many contiguous word tokens need to be formed.
            
        """
        
        
        content = self._lemmatize_content()
        list_ngrams = []
        for sentence in content:
            sentence = self._handle_period(sentence)
            sentence_list = sentence.split(".")
            for sub in sentence_list:
                sub = self._handle_punctuation(sub)
                tokens = [t for t in sub.split() if nltk.pos_tag([t])[0][1].startswith(('N','V','R','J','S'))]
                m = len(tokens)
                if m > n:
                    for i in range(len(tokens)-(n-1)):
                        list_ngrams = list_ngrams + [tokens[i:i+n]]
        return list_ngrams
    
    
    def pim_based_topics(self,n,number=None):
        """This method extracts the topic from the content based on the pointwise mutual information score.
        Pointwise mutual information (PMI) or point mutual information, is a measure of association 
        used in information theory and statistics. It basically measures the conditional probability of the two events
        occuring together. 
        For eg. for 2grams it is given by PMI = p(w1,w2)/(p(w1)*p(w2))
        p(w1,w2) = probability of two words occuring together in the content. 
        p(w1) = probability of word 1 occuring at place 1 and place 2 can have any word
        p(w2) = probability of word 2 occuring at place 2 and place 1 can have any word
        HIgher the PMI higher the association and hence higher the chance of the ngram being a topic.
        However the downside is that if two words are rare and say occur only once then PMI score for such pair
        will be high even though it does not really talk about the content. So I have set the threshold frequency
        to 2. Although this seems very low threshold it worked for me for the test urls.
        
        Parameters
        ----------
        n : int
            n in n-grams. Specifies how many contiguous word tokens need to be formed.
        number : int (optional)
            The top n-grams to be displayed
        
        """
        ngrams = self._get_n_grams(n)
        counter = Counter()
        for value in ngrams:
            counts = [0 for v in value] + [0]
            total = len(ngrams)
            for v in ngrams:
                if v == value:
                    counts[-1] +=1
                for i in range(len(v)):
                    if v[i] == value[i]:
                        counts[i] += 1
            if(counts[-1]>2):
                p_all = counts[-1]/total
                p_other = 1
                for c in counts[:-1]:
                    p_other = p_other * c/total
                pmi = math.log(p_all/p_other)
                topic = " ".join(value)
                counter.update({topic:pmi})
        if number:
            return(counter.most_common(number))
        else:
            return(counter.most_common())
    
    
    def pos_based_topics(self,n,number):
        """This method extracts the topic from the content based on part of speech tags of the contiguous tokens.
        English language has a structure and consecutive words to make sense generally belong to particular part
        of speech. 
        For valid 2-grams the strucure has to be (noun,noun)  or (Adjective,noun). 
        For valid 3-grams the structue has to be (adjective/noun, anything, adjective/noun)
        The n-grams are filtered and then based on their frequency the topics are chosen. higher the frequency
        more the chances of the n-grams to be a topic.
        This approach can only take 2grams or 3grams tokens. Other value of n would raise an exception.
        
        Parameters
        ----------
        n : int
            n in n-grams. Specifies how many contiguous word tokens need to be formed.
        number : int (optional)
            The top n-grams to be displayed
        
        Raises
        ------
        ValueError if n is given value other than 2 or 3
        
        """
        ngrams = [" ".join(v) for v in self._get_n_grams(n)]
        if n==3:
            counter = Counter(ngrams)
            counter_final = Counter()
            for value in ngrams:
                w1,w2,w3 = value.split(" ")[0],value.split(" ")[1],value.split(" ")[2]
                if nltk.pos_tag([w1])[0][1][0] in ['J','N'] and  nltk.pos_tag([w3])[0][1][0] in ['J','N']:
                    counter_final.update({value:counter[value]})
            return counter_final.most_common(number)

        elif n==2:
            counter = Counter(ngrams)
            #print(counter)
            counter_final = Counter()
            for value in ngrams:
                w1,w2 = value.split(" ")[0],value.split(" ")[1]
                if (nltk.pos_tag([w1])[0][1][0] in ['N'] and  nltk.pos_tag([w2])[0][1][0] in ['N'] or \
                   nltk.pos_tag([w1])[0][1][0] in ['J'] and  nltk.pos_tag([w2])[0][1][0] in ['N']):
                    counter_final.update({value:counter[value]})

            return counter_final.most_common(number)
        
        else:
            raise ValueError("Part of speech based topics can only take n=2 or n=3")
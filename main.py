from UrlToText import UrlToText
from TextToTopics import TextToTopics
import argparse


parser = argparse.ArgumentParser(description = 'Topic extraction from URL')
parser.add_argument('url',type=str,help='URL of the webpage of which the topics are to be extracted')
parser.add_argument('--n',type=int,help='n in n-grams - specifies the number of words in the topic. OPtional. If not set then default = 3')
parser.add_argument('--approach',type=str,help='which approach to choose to extract topics. pmi for Pointwise Mututal Information or pos for part of speech tag filtering. Optional. If not set then default = pmi')
parser.add_argument('--number',type=int,help='number of top topics to be displayed. Optional. If not set then default = 5')
args = parser.parse_args()
    
    
if __name__== "__main__":
    
    url = args.url
    n = args.n
    approach = args.approach
    number = args.number
    
    url_text = UrlToText(url)
    total_content = url_text.get_total_content()
    text_topics = TextToTopics(total_content)
    
    if not n:
        n = 3
        
    if not number:
        number = 5
    
    if approach == 'pos':
        print("Finding the topics based on part of speech filtering for {}-grams topic names and displaying top {} topics".format(n,number))
        print(text_topics.pos_based_topics(n,number))
    else:
        print("Finding the topics based on pointwise mutual information for {}-grams topic names and displaying top {} topics".format(n,number))
        print(text_topics.pim_based_topics(n,number))

        
    
    
    
    


    
    
    
    
    
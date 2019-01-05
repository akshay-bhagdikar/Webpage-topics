import requests
from bs4 import BeautifulSoup
import bs4
import re

class UrlToText:
    """
    This class is used to fetch the textual content from HTML markup

    ...

    Attributes
    ----------
    url : str
        The URL of the webpage of which the topics need to be found 
    _status_codes: Dictionary
        The dictionary of common HTTP status codes as the key and their brief description as values
    _body: bs4.element.Tag
        The content under body tag of the HTML 
        
    Methods
    -------
    _get_soup()
        Takes in the URL and returns BeautifulSoup object 
    
    _get_meta_content()
        Returns the textual content under the meta element
    
    _get_title_content()
        Returns the textual content under the Title element
    
     _set_body()
         Sets the ._body attribute
    
    _filter_tags(body)
        Removes the script and style elements from the HTML and returns the HTML structure 
        without any of these tags
    
    _filter_content(node,min_char,threshold)
        Filters the nodes that has less textual density than the threshold parameter 
        and less textual length than min_char parameter
    
    _find_filter_threshold(body)
        Returns the threshold density which is supposed to be the density of the body element
        
    _get_body_content()
        Returns the textual content under the body element
        
    get_total_content()
        Returns the total textual content under body element, title element and the meta 
        element of the HTML document
    
    """
   


    def __init__(self,url):
        """
        Parameters
        ----------
        url : str
            The URL of the webpage of which the topics need to be found 
        """
        self.url = url
        self._status_codes = {200:'OK',
                              400:'Bad request - The request could not be understood by the server \
                                   due to malformed syntax.',\
                              401:'Unauthorized - The request requires user authentication.',\
                              403:'Forbidden - The server understood the request, but is refusing to fulfill it.',\
                              404:'Not Found - The server has not found anything matching the Request-URI.',\
                              409:'Conflict - The request could not be completed due to a conflict with the current state of the resource.'\
                              ,500:'Internal Server error'}
    
    
    def _get_soup(self):
        """This function returns the BeautifulSoup object based on the URL supplied. The class attribute url is used
        by this method

        Raises
        ------
        Exception 
            The status code sent by the server is not of class 2xxx
        ConnectionError
            If you are not connected to the internet or there is some other connection issue
        Timeout Error
            If the connection is timed out
        RequestException
            If some ambiguous error happens
        
        """
        
        url = self.url
        headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}
        try:
            html = requests.get(url,headers=headers,timeout=10)
            status_code = html.status_code
            if str(status_code)[0]!='2':
                if status_code in self._status_codes:
                    raise Exception ('Something bad happened {}'.format(status_code,self._status_codes[status_code]))
                else:
                    raise Exception ('Status code other than 2xxx encountered. Status code is {}'.format(status_code))
        except requests.ConnectionError as e:
            print("Failed to connect. Check if you are connected to the internet {}".format(str(e)))
        except requests.Timeout as e:
            print("Timeout Error {}".format(str(e)))  
        except requests.RequestException as e:
            print("Some ambiguous error while processing the request {}".format(str(e)))
        result = html.content
        soup = BeautifulSoup(result,'html.parser')
        return soup
    
    
    def _get_meta_content(self):
        """This function Returns the keywords/title/description content under the meta tag (element) of the HTML document. 
        If no meta tags are present then it prints out that "No meta information is present"
        
        """
        soup = self._get_soup()
        meta = soup.findAll('meta')
        content = []
        if len(meta)<1:
            print("No meta information found")
        for m in meta:
            attrs = list(m.attrs.keys())
            if('content' in attrs):
                attrs.remove('content')
            for attr in attrs:
                if 'keywords' in m[attr] or 'title' in m[attr] or 'description' in m[attr]:
                    content.append(m['content'])
        return content

    
    def _get_title_content(self):
        """This function Returns the textual content under the title tag of the HTML document. If no Title tag is present
        then it prints out "No title tag found"
        
        """
        soup = self._get_soup()
        if(soup.find('title')):    
            title = [soup.find('title').text]
            return title
        else:
            print("No title tag found")
        
    
    def _set_body(self):
        """This function Sets the class variable _body to the bs4.element.tag object that represents the body element of the
        HTML document
        
        Raises
        ------
        Exception
            If body element is not found in the HTML document.
        
        """
        
        soup = self._get_soup()
        body = soup.find('body')
        if(body and len(body.findAll())>0):
            self._body = body
        else:
            raise Exception ("No body or body content found")
    
    
    def _filter_tags(self,body):
        """This function removes the script and style tags from the HTML structure since they do not give any useful textual
        information. This is one of the strategies to reduce the clutter.
        
        """
        for tag in body(["script", "style"]):
            tag.decompose()
            
            
    def _find_filter_threshold(self):
        """This function calculates the threshold of text density to be used in _filter_content function.
        The threshold is set as the the text density of the body element. The text density for a particular
        node is found by (Ci)/(Ti) where Ci is the number of textual character for a node and Ti is the number
        of nodes present under the i-th node. More the text density more important the node is. This is another
        strategy to reduce the clutter
        
        """
        body = self._body
        total_tags = len(body.findAll())
        total_char = len(body.text)
        density = total_char/total_tags
        return density
        
    
    def _filter_content(self,node,min_char,threshold):
        """ This function removes the HTML nodes that have text density lower than the threshold density
        the nodes that have less textual characters for eg. <li> tag. The threshold is set as the the text 
        density of the body element. The text density for a particular node is found by (Ci)/(Ti) where 
        Ci is the number of textual character for a node and Ti is the number of nodes present under 
        the i-th node. The number of textual characters that represent the hyperlink are subtrcted from the 
        total characters because hyperlink would most of the time not convey meaningful information.
        More the text density more important the node is. This is another strategy to reduce the clutter.
        
        """
        total_tags = len(node.findAll())
        total_char = len(node.text)
        a_tags = node.findAll('a')
        len_links = 0
        for a in a_tags:
            len_links += len(a.text)
        total_char = total_char - len_links
        if(total_tags!=0):
            density = total_char/total_tags
        else:
            density = total_char
        if density>=threshold:
            return True
        else:
            return False
    
    
    def _get_body_content(self):
        """ This function returns the textual content for all the nodes under the body element 
        of the HTML document. The nodes are first checked for text density. If it is lower than the
        threshold density then those nodes are not considered and their textual content is not taken 
        into account.
        """
        body = self._body
        self._filter_tags(body)
        body_content = []
        min_char = 25
        threshold = self._find_filter_threshold()
        for child in body.findAll():
            if(type(child) is bs4.element.Tag):
                if self._filter_content(child,min_char,threshold):
                    content = child.find(text=True, recursive=False)
                    if (content is not None):
                        content = str(content)
                        content = re.sub('\s+',' ',content).strip()
                        if content!='' and (len(content))>min_char:
                            body_content.append(content)
        return body_content
    
    def get_total_content(self):
        """ This function returns all the textual content under the body, meta and the title tag combined
        
        """
        body = self._set_body()
        total_content = self._get_body_content() + self._get_meta_content() + self._get_title_content()
        return total_content
    
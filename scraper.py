from bs4 import BeautifulSoup
from copy import deepcopy
import requests
import os
try:
    import cPickle as pkl
except ImportError:
    import pickle as pkl


def get_links(category, pre_existing_set=None, url=None):
    """
    Generates a list of articles and sub-categories in a category on wikipedia

    category: category name as a string
    pre_existing_set: (Optional) set of subcategories, if provided this code 
    will append to that set

    returns a tuple of (list of links, queue of sub-categories)
    """

    def get_category_url(category_name):
        category_prefix = "https://en.wikipedia.org/wiki/Category:"
        return category_prefix + category_name

    def get_absolute_url(wikipedia_relative_url):
        return "https://en.wikipedia.org" + wikipedia_relative_url

    if url is None:
        url = get_category_url(category)

    html_category_page = requests.get(url).text
    parsed_category_page = BeautifulSoup(html_category_page, "html.parser")
    content = parsed_category_page.findAll("div", {"id":"mw-pages"})
    content.extend(parsed_category_page.findAll("div",{"id":"mw-subcategories"}))

    # Initialize the pages list and subcategory queue
    pages_so_far = []
    if pre_existing_set is not None:
        subcategory_set = pre_existing_set
    else:
        subcategory_set = set()

    # Add all "links to pages" to the pages list, and all 
    # "links to subcategories" to the subcategory queue
    for item in content:
        for link_tag in item.select("a"):
            try:
                link_url = link_tag["href"]
                if "Category:" in link_url:
                    subcategory_set.add(get_absolute_url(link_url))
                elif "/" == link_url[0] and "Wikipedia:FAQ" not in link_url:
                    pages_so_far.append(get_absolute_url(link_url))
            # ignoring anch
            except KeyError:
                pass

    # If this category listing has more pages, then proceed to them
    last_text_on_page = parsed_category_page.findAll("div", \
                     {"class":"mw-content-ltr"})[0].select("a")[-1].text
    if last_text_on_page == "next page":
        next_page_url = get_absolute_url(parsed_category_page.findAll("div",\
                     {"class":"mw-content-ltr"})[0].select("a")[-1]["href"])
        pages_next, subcategory_set_next = get_links(category, \
                                               subcategory_set, next_page_url)
        pages_so_far.extend(pages_next)
        subcategory_set_next.update(subcategory_set_next)

    return pages_so_far, subcategory_set


def get_article_text_and_metadata(url):
    """
    Fetches and cleans a wikipedia article
    returns a tuple of (plaintext article content, number_of_non_tex_images, 
         number_of_tex_images, number_of_internal_links, number_of_citations)
    """
    article_content = ""

    # Fetch the webpage and parse it
    raw_html = requests.get(url).text
    parsed_html = BeautifulSoup(raw_html, "html.parser")
    number_of_citations = 0

    # Iterate over the HTML DOM for each <div> tag in the body
    for html_paragraph in parsed_html.select("div p"):

        # Strip citations from the text and count them
        for citation in html_paragraph.find_all("sup"):
            citation.replaceWith(" ")
            number_of_citations += 1

        # Convert the HTML to text and strip out punctuation
        text_paragraph = html_paragraph.getText().lower()
        cleaned_paragraph = filter(lambda char: char.isalnum() or char == " ", text_paragraph)
        article_content += " " + cleaned_paragraph
    
    images = parsed_html.select("img")

    number_of_images = len(images)
    number_of_tex = 0
    for item in images:
        try:
            tmp = item['class']
        except KeyError:
            tmp = []
        if "mwe-math-fallback-image-inline" in tmp:
            number_of_tex += 1

    number_of_non_tex = number_of_images - number_of_tex
    number_of_internal_links = len(parsed_html.find("div", \
                    {"id":"bodyContent"}).select("a")) - number_of_citations

    return article_content, number_of_non_tex, number_of_tex, number_of_internal_links, number_of_citations


def get_links_upto_depth(category_name, depth=0):
    """
    depth refers to subcatergory level, 0 is the initial page, 1 is 
    first set of subcategories etc.
    """
    pages_so_far, subcategories = get_links(category_name)
    subcategories_at_depth = dict()
    subcategories_at_depth[0] = list(subcategories)
    for current_depth in xrange(depth):
        subcategories_at_depth[current_depth+1] = []
        for subcategory_url in subcategories_at_depth[current_depth]:
            sub_pages, sub_subcategories = get_links(category_name, url=subcategory_url)
            pages_so_far.extend(sub_pages)
            subcategories_at_depth[current_depth+1].extend(list(sub_subcategories))
    return pages_so_far, subcategories_at_depth


if __name__ == "__main__":
    
    with open("categories.txt", "r") as f:
        main_categories = f.readlines()

    all_pages = {}
    list_of_subcategories = {}

    depth = 1
    for category_name in main_categories:
        print "\nCollecting links for", category_name
        pages, subcategories_with_depth = get_links_upto_depth(category_name, depth)
        all_pages[category_name] = set(pages)
        list_of_subcategories[category_name] = deepcopy(subcategories_with_depth)
    
    if not os.path.isdir('data'):
        os.mkdir('data')

    '''
    Everything in this file upto this point will work regardless of scale, 
    unless Wikipedia changes its design. I am only going through categories 
    and storing a list of url-s for articles and subcategories. Wikipedia 
    has a about five million articles, and storing the urls in a list will 
    require 
        
        5*10^6 * 90(bytes) / 10^6 = 450 MB 
        
    This is assuming each url is 50 characters long (~90 bytes in python).

    However, the for-loop below downloads and reads articles for each 
    category and writes to disk. If a category is very large, then I will 
    have to split the list and write separate files. 
    '''
    for category_name in all_pages:
        articles = []
        count = 0
        for url in all_pages[category_name]:
            count += 1
            if count%100 == 0:
                print  100*float(count)/len(all_pages[category_name]),"% done"
            articles.append(list(get_article_text_and_metadata(url)) + [category_name])

        filename = 'data/' + category_name + "_data.pkl"
        pkl.dump(articles, open(filename, 'wb'))

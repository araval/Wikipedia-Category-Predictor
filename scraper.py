from bs4 import BeautifulSoup
import requests
from Queue import Queue

try:
    import cPickle as pkl
except ImportError:
    import pickle as pkl


def get_links(category, pre_existing_queue=Queue(), url=None):
    """
    Generates a list of articles and sub-categories in a category on Wikipedia

    category: category name as a string
    pre_existing_queue: (Optional) queue of subcategories, if provided this code will append to it
    url: url to go to

    return: tuple of (list of links, queue of sub-categories)
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
    links = parsed_category_page.findAll("div", {"class":"mw-category-group"})

    # Initialize the pages list and subcategory queue
    pages = []
    subcategory_queue = pre_existing_queue

    # Add all "links to pages" to the pages list, and all "links to subcategories" to the subcategory queue
    for item in links:
        for link_tag in item.select("a"):
            link_url = link_tag["href"]
            if "Category:" in link_url:
                subcategory_queue.put(get_absolute_url(link_url))
            else:
                pages.append(get_absolute_url(link_url))

    # If this category listing has more pages, then proceed to them
    last_text_on_page = parsed_category_page.findAll("div", {"class":"mw-content-ltr"})[0].select("a")[-1].text
    if last_text_on_page == "next page":
        next_page_url = get_absolute_url(parsed_category_page.findAll("div", {"class":"mw-content-ltr"})[0].select("a")[-1]["href"])
        get_links(category, subcategory_queue, next_page_url)

    return pages, subcategory_queue


def get_article_text_and_metadata(url):
    """
    Fetches and cleans a Wikipedia article
    url: URL of the Wikipedia article
    returns tuple of (plaintext article content, number_of_images, number_of_internal_links, number_of_citations)
    """
    article_content = ""

    # Fetch the webpage and parse it
    raw_html = requests.get(url).text
    parsed_html = BeautifulSoup(raw_html, "html.parser")
    number_of_citations = 0

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
            if "tex" or "mwe-math-fallback-image-inline" in item['class']:
                number_of_tex += 1
        except KeyError:
            pass

    number_of_internal_links = len(parsed_html.find("div", {"id":"bodyContent"}).select("a")) - number_of_citations
    
    return article_content, number_of_images, number_of_tex, number_of_internal_links, number_of_citations

if __name__ == "__main__":

    main_categories = ["Rare_diseases",
                       "Infectious_diseases",
                       "Cancer", 
                       "Congenital_disorders",
                       "Organs_(anatomy)",
                       "Machine_learning_algorithms",
                       "Medical_devices"]

    all_pages = {}
    max_pages = 10000
    
    for category_name in main_categories:
        print "Collecting links for", category_name
        pages, subcategories = get_links(category_name)
        all_pages[category_name] = pages
        while len(all_pages[category_name]) < max_pages and subcategories.qsize() > 0:
            subcategory_url = subcategories.get()
            pages, subcategories = get_links(category_name, subcategories, subcategory_url)
            all_pages[category_name] += pages
    
    with open("all_pages.pkl", "r") as f:
        all_pages = pkl.load(f)

    for category_name in all_pages:
        articles = []
        print "Downloading", len(all_pages[category_name]), "pages about", category_name
        count = 0
        for url in all_pages[category_name]:
            count += 1
            if count%100 == 0:
                print category_name
            articles.append(list(get_article_text_and_metadata(url)) + [category_name])

        filename = category_name + "_data.pkl"
        pkl.dump(articles, open(filename, 'wb'))

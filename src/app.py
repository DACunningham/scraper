# This provides a framework for functions that will be tested as
# part of modulE 5 NLP.  You should test your submissions against
# the cases listed below, they will then be tested against further unseen
# cases before being reviewed manually.

# Do not chance these dependencies
import pytest

# Import your dependencies here
import requests
import json
import spacy
from bs4 import BeautifulSoup
from pprint import pprint

# Load English
nlp = spacy.load("en_core_web_sm")


def bbc_scraper(url):
    """
    This function should take a url, which will relate to a bbc news article
    and return a json object containing the following fields:
    1) URL (provided.  For example https://www.bbc.co.uk/news/uk-51004218)
    2) Title
    3) Date_published
    4) Content --(the main body of article, this must be one
    continuous string without linebreaks)
    The function must be iterable (If placed in a for loop and provided with
    several URLs in turn return the correct json object for each time it is
    invoked without any manual intervention)
    """

    # Get raw article & convert to Python object
    raw_response = requests.get(url)
    page_html_obj = BeautifulSoup(raw_response.text, "html.parser")

    # Get article title, date and content
    title = page_html_obj.find("h1", {"class": "story-body__h1"}).text
    date_published = (
        page_html_obj.find("div", {"class": "story-body"})
        .find("div", {"data-datetime": True})
        .text
    )
    content_intro = (
        page_html_obj.find("div", {"class": "story-body"})
        .find("p", {"class": "story-body__introduction"})
        .text
    )
    content_paragraphs = page_html_obj.find("div", {"class": "story-body"}).findAll(
        "p", {"aria-hidden": False, "class": False}
    )
    content = content_intro
    for para in content_paragraphs:
        content += "\n" + para.text

    content += "\n"

    # Structure article content to required json structure
    result = {
        "URL": url,
        "Title": title,
        "Date_published": date_published,
        "Content": content,
    }

    # Convert Python json object to json string and return
    results_json = json.dumps(result)
    return results_json


def extract_entities(string):
    """
    This function should return a json containing the:
    1) People
    2) Places
    3) Organisations
    in the text string provided.
    """

    # feed text to natural language processing object
    doc = nlp(string)

    # Classify each entity in nlp object text and label
    results_dict = [(X.text, X.label_) for X in doc.ents]
    # Prepare return object structure
    entities_json = {"people": set(), "places": set(), "organisations": set()}

    # Find interesting entities and sort into respective sets (nil duplication)
    for entity in results_dict:
        if entity[1] == "ORG":
            entities_json["organisations"].add(entity[0])
        elif entity[1] == "LOC" or entity[1] == "GPE":
            entities_json["places"].add(entity[0])
        elif entity[1] == "PERSON":
            entities_json["people"].add(entity[0])

    # Convert sets to lists to enable json conversion
    for k, v in entities_json.items():
        entities_json[k] = list(v)

    # Stringify return object to json and return
    entities_json = json.dumps(entities_json)
    return entities_json


####################################################################
# Developer Integration Test cases
""" Not technically a test set as there is no assert (I have tried
to keep this to one file as best I can and I don't think you would
want reams of text in here for the asserts).

As per the specification added a test for iterating over the scraper and
entity extraction functions.

Utilised pretty printer to show function results in the terminal.
"""


def _iterate_scraper(urls):
    results = list()

    for url in urls:
        temp_article = bbc_scraper(url)
        results.append(temp_article)
        pprint(json.loads(temp_article))

    return results


def _integration_test():

    articles = _iterate_scraper(
        [
            "https://www.bbc.co.uk/news/uk-52255054",
            "https://www.bbc.co.uk/news/uk-51004218",
        ]
    )
    entity_result = list()

    for article in articles:
        temp_article = json.loads(article)
        entity_result.append(extract_entities(temp_article["Content"]))

    for er in entity_result:
        temp_er = json.loads(er)
        pprint(temp_er)


_integration_test()

####################################################################
# Test cases


def test_bbc_scrape():
    results = {
        "URL": "https://www.bbc.co.uk/news/uk-52255054",
        "Title": "Coronavirus: 'We need Easter as much as ever,' says the Queen",
        "Date_published": "11 April 2020",
        "Content": '"Coronavirus will not overcome us," the Queen has said, in an Easter message to the nation.\nWhile celebrations would be different for many this year, she said: "We need Easter as much as ever."\nReferencing the tradition of lighting candles to mark the occasion, she said: "As dark as death can be - particularly for those suffering with grief - light and life are greater."\nIt comes as the number of coronavirus deaths in UK hospitals reached 9,875.\nSpeaking from Windsor Castle, the Queen said many religions had festivals celebrating light overcoming darkness, which often featured the lighting of candles.\nShe said: "They seem to speak to every culture, and appeal to people of all faiths, and of none.\n"They are lit on birthday cakes and to mark family anniversaries, when we gather happily around a source of light. It unites us."\nThe monarch, who is head of the Church of England, said: "As darkness falls on the Saturday before Easter Day, many Christians would normally light candles together. \n"In church, one light would pass to another, spreading slowly and then more rapidly as more candles are lit. It\'s a way of showing how the good news of Christ\'s resurrection has been passed on from the first Easter by every generation until now."\nAs far as we know, this is the first time the Queen has released an Easter message.\nAnd coming as it does less than a week since the televised broadcast to the nation, it underlines the gravity of the situation as it is regarded by the monarch.\nIt serves two purposes really; it is underlining the government\'s public safety message, acknowledging Easter will be difficult for us but by keeping apart we keep others safe, and the broader Christian message of hope and reassurance. \nWe know how important her Christian faith is, and coming on the eve of Easter Sunday, it is clearly a significant time for people of all faiths, but particularly Christian faith.\nShe said the discovery of the risen Christ on the first Easter Day gave his followers new hope and fresh purpose, adding that we could all take heart from this. \nWishing everyone of all faiths and denominations a blessed Easter, she said: "May the living flame of the Easter hope be a steady guide as we face the future."\nThe Queen, 93, recorded the audio message in the White Drawing Room at Windsor Castle, with one sound engineer in the next room. \nThe Palace described it as "Her Majesty\'s contribution to those who are celebrating Easter privately". \nIt follows a speech on Sunday, in which the monarch delivered a rallying message to the nation.\nIn it, she said the UK "will succeed" in its fight against the coronavirus pandemic, thanked people for following government rules about staying at home and praised those "coming together to help others".\nShe also thanked key workers, saying "every hour" of work "brings us closer to a return to more normal times".\n',
    }
    scraper_result = bbc_scraper("https://www.bbc.co.uk/news/uk-52255054")
    assert json.loads(scraper_result) == results


def test_extract_entities_amazon_org():
    input_string = "I work for Amazon."
    results_dict = {"people": [], "places": [], "organisations": ["Amazon"]}
    extracted_entities_results = extract_entities(input_string)
    assert json.loads(extracted_entities_results) == results_dict


def test_extract_entities_name():
    input_string = "My name is Bob"
    results_dict = {"people": ["Bob"], "places": [], "organisations": []}
    extracted_entities_results = extract_entities(input_string)
    assert json.loads(extracted_entities_results) == results_dict


test_bbc_scrape()
test_extract_entities_amazon_org()
test_extract_entities_name()

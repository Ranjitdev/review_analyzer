from src.logger import logging
from src.exception import CustomException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import matplotlib.pyplot as plt
from selenium.webdriver.common.action_chains import ActionChains
import nltk
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import re
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()
import os
import sys
from typing import *


def get_selenium_driver(path: str) -> Tuple[Any, Any]:
    try:
        # service = Service(ChromeDriverManager().install())
        service = Service(executable_path=path)
        options = Options()
        # options.add_argument("start-maximized")
        options.add_argument("incognito")
        options.add_argument("disable-extensions")
        # options.add_argument("headless")
        driver = webdriver.Chrome(service=service, options=options)
        actions = ActionChains(driver)
        return driver, actions
    except Exception as e:
        raise CustomException(e, sys)


class EvaluateComments:
    def __init__(self, ratings: list, headers: list, comments: list):
        self.ratings = ratings
        self.headers = headers
        self.comments = comments

    @staticmethod
    def positive_words() -> List[str]:
        out = []
        with open(r'artifacts/positive.txt', 'r') as file:
            for line in file.readlines():
                word = stemmer.stem(line.replace('\n', '').casefold())
                out.append(word)
        return out

    @staticmethod
    def negative_words() -> List[str]:
        out = []
        with open(r'artifacts/negative.txt', 'r') as file:
            for line in file.readlines():
                word = stemmer.stem(line.replace('\n', '').casefold())
                out.append(word)
        return out

    @staticmethod
    def clean_sentences(sentence) -> List[str]:
        result = []
        sentence = re.sub('[^a-zA-Z]', ' ', sentence)
        for word in word_tokenize(sentence):
            word = stemmer.stem(word.casefold())
            if word not in stopwords.words('english'):
                result.append(word)
        return result

    def get_insightes(self) -> Tuple[float, int, int]:
        positive_words = self.positive_words()
        negative_words = self.negative_words()

        total_rating = 0
        for rating in self.ratings:
            total_rating += float(rating)

        positive_count = 0
        negative_count = 0
        for comment in self.comments:
            sentence = self.clean_sentences(comment)
            for word in sentence:
                if word in positive_words:
                    positive_count += 1
                elif word in negative_words:
                    negative_count += 1
        return total_rating, positive_count, negative_count



def get_graph(positivity):
    percent = max(0, min(positivity, 100))

    fig, ax = plt.subplots(figsize=(4, 1))
    ax.add_patch(plt.Rectangle((0, 0), 1, 0.5, alpha=0.4, hatch='|', edgecolor='#010045', facecolor='#f3ff05'))
    ax.add_patch(plt.Rectangle((0, 0), percent / 100, 0.5, edgecolor='#007d00', facecolor='#00ff00'))

    ax.text(0.01, 0.15, f'Positivity {percent}%', fontsize=14, color='black', fontweight='bold')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.title(f'Positive vs Negative Words')
    return fig



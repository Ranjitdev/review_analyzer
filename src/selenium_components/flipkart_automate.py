from src.logger import logging
from src.exception import CustomException
from src.utils import get_selenium_driver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
import time
import numpy as np
import pandas as pd
import os
import sys
import concurrent.futures
import streamlit as st
from typing import *
from src.utils import EvaluateComments


class FlipkartComments:
    def __init__(self):
        driver_path = r'artifacts/chromedriver.exe'
        self.driver, self.actions = get_selenium_driver(driver_path)

    def scroll_page(self, obj) -> None:
        self.actions.move_to_element(obj).perform()
        time.sleep(0.5)

    def load_page(self) -> None:
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    def get_urls(self, url: str, total_comments: int) -> List[str]:
        start = time.monotonic()
        urls = []
        try:
            try:
                self.driver.get(url)
                self.load_page()
                all_comments = self.driver.find_element(By.CSS_SELECTOR, "._3UAT2v")
            except:
                self.driver.get(url)
                self.load_page()
                all_comments = self.driver.find_element(By.CSS_SELECTOR, "._3UAT2v")
            self.scroll_page(all_comments)
            all_comments.click()
            for _ in range(int(np.round(total_comments/10))):
                self.load_page()
                next_comment = self.driver.find_element(By.LINK_TEXT, "NEXT")
                urls.append(next_comment.get_attribute('href'))
                self.scroll_page(next_comment)
                next_comment.click()
            self.driver.close()
            end = time.monotonic()
            st.caption(f':green[Elapsed Counting Time] :blue[{np.round(end-start, 2)} second]')
            return urls
        except Exception as e:
            self.driver.close()
            end = time.monotonic()
            st.caption(':orange[Unable to fetch all comments] :red[Internet Unstable]')
            st.caption(f':green[Elapsed Counting Time] :blue[{np.round(end-start, 2)} second]')
            return urls

    def process_urls(self, url) -> List[List[Dict[str, Any]]]:
        raw_html = requests.get(url)
        parsed_html = BeautifulSoup(raw_html.content, features='html5lib')
        comments = [
            comment.text.replace('READ MORE', '') for comment in parsed_html.find_all('div', attrs={'class': 't-ZTKy'})
        ]
        ratings = [
            star.text for star in parsed_html.find_all('div', attrs={'class': '_3LWZlK _1BLPMq'})
        ]
        heads = [
            head.text for head in parsed_html.find_all('p', attrs={'class': '_2-N8zT'})
        ]
        comment_list = []
        total_rating, positive_count, negative_count = EvaluateComments(ratings, heads, comments).get_insightes()
        for data in zip(ratings, heads, comments):
            result = {
                'Rating': data[0],
                'Header': data[1],
                'Comment': data[2]
            }
            comment_list.append(result)
        results = [comment_list, (total_rating, positive_count, negative_count)]
        return results

    def get_comments(self, url: str, total_comments: int) -> Tuple[pd.DataFrame, float, float, float]:
        start = time.process_time()
        try:
            df = []
            total_rating, positive_count, negative_count = 0, 0, 0
            urls = self.get_urls(url, total_comments)
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as worker:
                futures = [worker.submit(self.process_urls, url) for url in urls]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            for result in results:
                df.extend(result[0])
                total_rating += result[1][0]
                positive_count += result[1][1]
                negative_count += result[1][2]
            positive_score = int(np.round((positive_count*100)/(positive_count+negative_count)))
            negative_score = int(np.round(100-positive_score))
            end = time.process_time()
            st.caption(f':green[Elapsed Processing Time] :blue[{np.round(end-start, 2)} second]')
            return pd.DataFrame(df), np.round(total_rating/len(df), 1), positive_score, negative_score
        except Exception as e:
            end = time.process_time()
            st.caption(f':red[Unable to fetch all comments error {e}]')
            st.caption(f':green[Elapsed Processing Time] :blue[{np.round(end-start, 2)} second]')

    def get_ratings(self, url) -> Tuple[str, pd.DataFrame, str, str]:
        raw_html = requests.get(url)
        parsed_html = BeautifulSoup(raw_html.content, features='html5lib')
        rating = parsed_html.find_all('div', attrs={'class': '_2d4LTz'})[0].text
        stars = parsed_html.find_all('div', attrs={'class': '_1uJVNT'})
        image_src = parsed_html.find_all('img', attrs={'class': "_396cs4 _2amPTt _3qGmMb"})[0]['src']
        product = parsed_html.find_all('img', attrs={'class': "_396cs4 _2amPTt _3qGmMb"})[0]['alt']
        result = {}
        count = 5
        for i in stars:
            result[str(count) + '★'] = i.text
            count -= 1
        ratings = pd.DataFrame([result])
        return rating, ratings, image_src, product




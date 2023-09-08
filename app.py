import numpy as np
import streamlit as st
import time
from src.selenium_components.flipkart_automate import FlipkartComments
from src.utils import *

st.title(":blue[👁‍🗨Review Analyzer]")

tab1, tab2 = st.tabs(['Flipkart', 'Amazon'])
with tab1:
    com_col, url_col = st.columns(2)
    with com_col:
        comment_no = st.number_input('Type how many comments you want to review')
        st.caption("Note: Don't exceed max review given on website")
    with url_col:
        url = st.text_input('URL')
        st.caption('Paste product URL from flipkart')
    if st.button('Submit'):
        col1, col2 = st.columns(2)
        rating, ratings, image_src, product = FlipkartComments().get_ratings(url)
        with col1:
            comments, avg_rating, positivity, negativity = FlipkartComments().get_comments(url,
                                                                                           int(np.round(comment_no)))
        with col2:
            st.dataframe(ratings, hide_index=True)
        col3, col4, col5 = st.columns(3)
        with col3:
            st.caption(':orange[Product User Total Rating]')
            st.subheader(f':rainbow[{rating}★]')
        with col4:
            st.caption(f':orange[Rating Count On {comment_no} Comments]')
            st.subheader(f':rainbow[{avg_rating}★]')
        with col5:
            img = get_graph(positivity)
            st.pyplot(img)
        img_col, name_col = st.columns(2)
        with img_col:
            st.image(image_src)
        with name_col:
            st.subheader(f':violet[{product}]')
        st.caption('Hover on the file and tap expand for full size')
        st.dataframe(comments)
with tab2:
    pass


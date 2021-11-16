# Climate Newsfeed

import os
from newsapi import NewsApiClient
from dotenv import load_dotenv, find_dotenv
from flask import render_template

load_dotenv(find_dotenv())
NEWS_API_KEY = os.getenv('NEWS_API_KEY')


def extendApp_newsfeed(app):

    @app.route('/climatenews/<int:page_id>')
    def newsfeed(page_id):
        """ Show climate news articles depending on page """

        newsapi = NewsApiClient(api_key=NEWS_API_KEY)
        news = newsapi.get_everything(
            q='climate, climate change, global warming, weather, natural disaster',
            language='en',
            sort_by='publishedAt',
            page=page_id
            )
        articles = news["articles"]
        return render_template('other/newsfeed.html', articles=articles, page_id=page_id)
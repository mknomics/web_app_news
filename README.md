# web_app_news
Flask web app that fetches the most current economic reports and let's you ask what they mean for your industry

This repo is the general codebase for a Flask web application that scrapes the most recent authoratative economic reports, 
provides summaries, and allows users to query the reports in a conversational way using an OpenAI api.

The web scraper is proprietary and runs on a schedule to keep the reports current.  

The usage of api calls is inefficient for production purposes in that redundant api calls are made for summary reporting.  
This has been purposeful and useful for development because it gives feedback on the possible LLM outputs, which do show variability.  
This aids in prompt development.

The HTML and CSS are basic to make it easier to develop basic functionality.

# This is a script for a bot that posts facts about sailing twice a day
# It uses chapGPT to generate the fact

import base64
import hashlib
import os
import re
import json
import requests
import redis
import openai
from requests.auth import AuthBase, HTTPBasicAuth
from requests_oauthlib import OAuth2Session, TokenUpdated
from flask import Flask, request, redirect, session, url_for, render_template

r = redis.from_url(os.environ.get("REDIS_URL"))

app = Flask(__name__)
app.secret_key = os.urandom(50)

# Load the OpenAI API key from an environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load the Twitter API keys from environment variables

# Twitter API keys
consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# Get the scopes
scopes = ["tweet.read", "users.read", "tweet.write", "offline.access"]

# Create a code verifier
code_verifier = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8")
code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)


# Twitter API URLs
request_token_url = "https://api.twitter.com/oauth/request_token"
access_token_url = "https://api.twitter.com/oauth/access_token"
authorize_url = "https://api.twitter.com/oauth/authorize"
tweet_url = "https://api.twitter.com/1.1/statuses/update.json"

# Twitter API endpoints
tweet_endpoint = "https://api.twitter.com/1.1/statuses/update.json"
verify_credentials_endpoint = (
    "https://api.twitter.com/1.1/account/verify_credentials.json"
)

# Twitter API OAuth1 session
twitter = OAuth2Session(client_id=consumer_key, token=access_token)

# Twitter API OAuth1 session with access token
twitter = OAuth2Session(client_id=consumer_key, token=access_token)


class TwitterAuth(AuthBase):
    def __call__(self, r):
        r.headers["Authorization"] = f"Bearer {access_token}"
        return r

    def get_fact():
        # Generate a fact using the GPT-3 model
        response = openai.Completion.create(
            engine="davinci",
            prompt="Generate a fact about sailing, epic sailors, sailing boats, sailing history, or anything else related to sailing and write it as a seventeenth century pirate.",
            max_tokens=100,
            n=1,
            stop=None,
        )
        fact = response.choices[0].text.strip()
        return fact

    def post_tweet(fact):
        # Post a tweet with the fact
        response = twitter.post(tweet_endpoint, json={"status": fact})
        response.raise_for_status()
        return response.json()

    def get_user():
        # Get the user's information
        response = twitter.get(verify_credentials_endpoint)
        response.raise_for_status()
        return response.json()

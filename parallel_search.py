from flask import Flask
from flask import request
from flask import Response, jsonify
import json, os
import grequests
app = Flask(__name__)

@app.route('/')
def hello_world():
    searchword = request.args.get('q', '')
    resp = {'query': searchword, 'results': {'google': {}, 'duckduckgo': {}, 'twitter': {}}}
    header = {'Authorization': 'Bearer ' + os.environ['TOKEN']}
    duckduckgo_url = 'http://api.duckduckgo.com/?q={}&format=json'.format(searchword)
    google_url = 'https://www.googleapis.com/customsearch/v1?key={}&cx=017576662512468239146:omuauf_lfve&q={}'.format(os.environ['GOOGLE_API_KEY'],searchword)
    twitter_url = 'https://api.twitter.com/1.1/search/tweets.json?q={}'.format(searchword)
    results = grequests.map([grequests.get(duckduckgo_url, timeout=1),
    grequests.get(google_url, timeout=1),
    grequests.get(twitter_url, headers=header, timeout=1)],
    exception_handler=exception_handler)
    for index, result in enumerate(results):
        if result:
            rsult_json = json.loads(result.content)
            if index == 0:
                if rsult_json['RelatedTopics']:
                    url = rsult_json['RelatedTopics'][0]['FirstURL']
                    text = rsult_json['RelatedTopics'][0]['Text']
                    resp['results']['duckduckgo'] = {'url': url, 'text': text}
            elif index == 1:
                if 'items' in rsult_json:
                    url = rsult_json['items'][0]['link']
                    text = rsult_json['items'][0]['title']
                    resp['results']['google'] = {'url': url, 'text': text}
            else:
                if rsult_json['statuses']:
                    id = rsult_json['statuses'][0]['id_str']
                    text = rsult_json['statuses'][0]['text']
                    resp['results']['twitter'] = {'id': id, 'text': text}
        else:
            if index == 0:
                resp['results']['duckduckgo'] = None
            elif index == 1:
                resp['results']['google'] = None
            else:
                resp['results']['twitter'] = None
    return jsonify(resp)

def exception_handler(request, exception):
    print "Request failed"

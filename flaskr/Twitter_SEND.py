import tweepy
consumer_key ="m7kaScv1OFaSbNamHMJTa1hvp"
consumer_secret ="9rkOnNOwJJoj62QvbRFEdpMHTpm0L04lBgtytnnpckdU5GUXKF"
access_token ="1074664387183558657-do6CI25cSSfBuA0cZsNOSL8YLNbrz0"
access_token_secret ="DjsKyjHthJTar8ZitoG2wiCapO06ec4YMr86dafoOZRP8"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

auth.set_access_token(access_token, access_token_secret) 
api = tweepy.API(auth) 


def message(name, message, handle):
    Twitter_Handle= handle
    api.update_status(status = "@" + Twitter_Handle + " " + message)


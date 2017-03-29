import json
import numpy as np
import requests

def search_track_name(q):
    # searches spotify for track by name
    query = q.lower().replace(' ', '%20')
    
    url_base = "https://api.spotify.com"
    url = "%s/v1/search?q=%s&type=track" % (url_base, query)
    
    response = requests.get(url)

    return json.loads(response.text)

def eval_match(st1, st2):
    # quick evaluation of the how well the queried results match
    # the search terms
    
    s1 = st1.lower()
    s2 = st2.lower()
    
    ct = 0.0
    
    n1 = len(s1)
    n2 = len(s2)
    
    for i in xrange(min(n1,n2)):
        if s1[i] == s2[i]:
            ct += 1.0
    
    return ct/max(n1,n2)

def check_name(q):
    # checks the entered name against the spotify track database
    # returns a tuple: (average name matching score, best matching score, track_id)
    
    a = search_track_name(q)
    tt = len(a['tracks']['items'])
    if tt < 1:
        return (0.0,0.0,0.0)

    match_percs = np.zeros(tt)
    for i in xrange(tt):
        match_percs[i] = eval_match(a['tracks']['items'][i]['name'], q)
    
    j = np.argmax(match_percs)
    id_no = a['tracks']['items'][j]['id']
    
    return (match_percs.mean(), match_percs.max(), id_no)

def create_track_list(string_in, step=2, threshold=.8):
    """
    given a string, seperated by ' ', attempts to create a list of spotify songs
    matching the terms in the string
    inputs:  string_in - a string a track names, seperated by spaces (' ')
             step - the number of words to take at a time when looking for song titles
             threshold - the minimum name-matching threshold for a song title to be added to the track list
    """

    track_base = "http://open.spotify.com/track/"
    string_lst = string_in.strip().split(' ')
    
    beg = 0
    step_init = step
    step = step
    end = beg+step

    track_names = []
    track_list = []

    while True:
        while end < len(string_lst):
            q = ' '.join(string_lst[beg:end])
            names_tpl = check_name(q)
            if names_tpl[1]>threshold:
                print q
                beg = end
                end += step
                track_names.append(q)
                track_list.append("%s%s" % (track_base, names_tpl[2]))
            else:
                end += 1

        q = ' '.join(string_lst[beg:end])
        names_tpl = check_name(q)
        if names_tpl[1]>threshold:
                print q
                track_names.append(q)
                track_list.append("%s%s" % (track_base, names_tpl[2]))
                break
        else:
            beg = 0
            step -= 1
            if step < 1:
                threshold -= .1
                step = step_init
            
    print track_names
    return track_list
    

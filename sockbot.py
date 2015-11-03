import praw
import OAuth2Util
import sqlite3
from html2text import html2text  # thank you Aaron Schwartz

from time import sleep

"""
Sockbot was created using assets and imagery from Elite Dangerous, with the permission of Frontier Developments plc,
for non-commercial purposes. It is not endorsed by nor reflects the views or opinions of Frontier Developments and
no employee of Frontier Developments was involved in the making of it.
"""

version = '0.5'
user_agent = 'windows:sockbot:v{} (by /u/Always_SFW)'.format(version)
testing_mode = False  # switch to test DB and criteria
words = ['sock', 'SOCK', 'Sock']
avoid_words = ['socket', 'SOCKET']
table = 'socks'
user = 'tfaddy'
send_delay = 5
cycle_delay = 3
subreddits = ['elitedangerous', 'eliteracers', 'elitetraders', 'eliteminers', 'fuelrats', 'unknownartefact']

def pause(time=5):
    time_left = time
    while time_left >= 0:
        print('[+] Sockbot will continue in: {}    '.format(time_left), end='\r')
        time_left -= 1
        sleep(1)
    print('                                                       ', end='\r')  # clear the line

def get_old_socks(cursor, table_name=table):
    old_socks = set()
    for row in cursor.execute('SELECT * FROM {} ORDER BY id'.format(table_name)):
        old_socks.add(row[1])  # id, comment id, timestamp
    return old_socks

def insert_comment_in_db(connection, cursor, table_name, id):
    try:
        cursor.execute('INSERT INTO {} VALUES (NULL, ?, CURRENT_TIMESTAMP)'.format(table_name), (id,))
        connection.commit()
    except:
        print('[-] Sockbot did not manage to insert the ID into the DB')
        print('[-] Exception: ', Exception)

def main():
    cycle = 1
    dbcon = sqlite3.connect('socks.db')
    dbcur = dbcon.cursor()
    get_old_socks(dbcur, table)
    r = praw.Reddit(user_agent=user_agent)
    o = OAuth2Util.OAuth2Util(r, server_mode=True)
    o.refresh(force=True)
    while True:
        print('[+] Sockbot cycle: ', cycle)
        cycle += 1
        for subreddit in subreddits:
            try:
                all_comments = r.get_comments(subreddit)
            except Exception:
                print('[-] Exception occurred:', Exception)
            else:
                print('[+] Sockbot is looking through the comments for: {} within subreddit: {}'.format(words, subreddit))
                instances = 0  # of the word present in the comments. Also includes those already in DB
                try:
                    for comment in all_comments:
                        for word in words:
                            if word in comment.body and word not in avoid_words and 'I am a bot!' not in comment.body:  # need to make a list of actual non sock references
                                # if sock is not in the database, put it in and contact the user
                                instances += 1
                                if comment.id not in get_old_socks(dbcur, table):
                                    # add the comment to the database, then send the message
                                    print('[!] Sockbot found a sock! Placing ID: {} in the database'.format(comment.id))
                                    insert_comment_in_db(dbcon, dbcur, table, comment.id)
                                    pk_id = dbcur.execute('SELECT max(id) FROM {}'.format(table)).fetchone()[0]
                                    message_string = 'Sock #{} was spotted at: {}.  If I broke somehow, contact /u/Always_SFW! or get /u/SpyTec13 to ban me!'.format(pk_id, comment.permalink)
                                    print('[!] Sending string:')
                                    print('\t', message_string)
                                    r.send_message(user, 'Sock #{} spotted!'.format(pk_id), message_string)
                                    # reply_string = 'I see you mentioned socks in some way. I have notified tfaddy. I am a bot! You can find my source code here: https://github.com/Winter259/sockbot'
                                    reply_string = '<h1>SOCK DETECTED</h1><br>' \
                                                   'tfaddy has been notified.<br>' \
                                                   '------------------<br>' \
                                                   '<i>I am a bot. Created and maintaned by <a href ="https://www.reddit.com/user/Always_SFW">CMDR Purrcat</a><br>' \
                                                   'You can find my source code <a href="https://github.com/Winter259/sockbot">Github</a><br>' \
                                                   'Current Version: {}</i>'.format(version)
                                    post_string = html2text(reply_string)
                                    print('[!] Replying with:')
                                    print('\t', post_string)
                                    comment.reply(post_string)
                                    pause(send_delay)
                except Exception:
                    print('[-] Encountered exception: {} when trying to search the comments'.format(Exception))
                print('[+] Current amount of socks in DB: {}, Instances found this cycle: {}'.format(len(get_old_socks(dbcur, table)), instances))
                pause(cycle_delay)

if __name__ == '__main__':
    main()

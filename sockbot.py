import praw
import OAuth2Util
from pysqlite import Pysqlite
from html2text import html2text  # thank you Aaron Schwartz
from purrtools import pause
from time import sleep, strftime, gmtime

__author__ = 'Simon Agius Muscat, www.github.com/purrcat259'

"""
Sockbot was created using assets and imagery from Elite Dangerous, with the permission of Frontier Developments plc,
for non-commercial purposes. It is not endorsed by nor reflects the views or opinions of Frontier Developments and
no employee of Frontier Developments was involved in the making of it.
"""

version = '1.1'
testing_mode = True
user_agent = 'raspberrypi:sockb0t259:v{} (by /u/Always_SFW)'.format(version)
table = 'socks'
send_delay = 5
cycle_delay = 0.5
words_to_avoid = ['Socket', 'Sockpuppet']
user = 'tfaddy'
subreddits = [
    'elitedangerous',
    'elitetraders',
    'eliteexplorers',
    'eliteminers',
    'eliteracers',
    'elitebountyhunters',
    'elitedangerouspics',
    'elitestories',
    'elitewings',
    'elitehumor',
    'eliteschool',
    'elitetankers',
    'eliteone',
    'eliteoutfitters',
    'fuelrats',
    'unknownartefact',
    'elitealliance',
    'elitemahon',
    'elitewinters',
    'elitehudson',
    'elitetorval',
    'elitelavigny',
    'elitepatreus',
    'aislingduval',
    'kumocrew',
    'eliteantal',
    'elitesirius',
    'elitelivery'
    # 'EiteDagerous'
]


if testing_mode:
    user = 'Always_SFW'
    table = 'test'
    subreddits = ['sockbottery']


def get_comment_id_list(db, table_name):
    comment_id_list = []
    data = db.get_db_data(table_name)
    for row in data:
        comment_id_list.append(row[1])
    return comment_id_list


def main():
    cycle = 1
    startup_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    print('[!] Sockbot version {} starting at: {} in testing mode: {}'.format(version, startup_time, testing_mode))
    database = Pysqlite('socks_db', 'socks.db')  # initialise the database
    print('[!] Sockbot is initialising connection to Reddit...')
    r = praw.Reddit(user_agent=user_agent)
    o = OAuth2Util.OAuth2Util(r, server_mode=True)
    o.refresh(force=True)  # avoids having to refresh the token manually
    print('[!] Sockbot is now connected to Reddit')
    while True:
        print('[+] Sockbot cycle: {}'.format(cycle))
        cycle += 1
        socks_spotted = 0  # amount of socks currently present in the comments. Also includes those already in DB
        for subreddit in subreddits:
            try:
                all_comments = r.get_comments(subreddit)
            except Exception as e:
                print('[-] Exception occurred: {}'.format(e))
            else:
                print('[+] Sockbot is checking /r/{}  '.format(subreddit))
                try:
                    for comment in all_comments:
                        print('[+] Checking comment with ID: {}    '.format(comment.id), end='\r')
                        if 'sock' in comment.body.lower() and not comment.author.name == 'sockbot259':
                            avoid_word_present = False  # check for words you are supposed to avoid, like 'Socket'
                            for bad_word in words_to_avoid:
                                if bad_word.lower() in comment.body.lower():
                                    print('[-] Comment with ID: {} is invalid'.format(comment.id))
                                    avoid_word_present = True
                                    break
                            if avoid_word_present:
                                break  # avoid extra iterations, go to the next comment
                            else:
                                # if sock is not in the database, put it in and contact the user
                                socks_spotted += 1
                                if comment.id in get_comment_id_list(database, table):
                                    print('[-] Comment with ID: {} is already in database'.format(comment.id))
                                else:
                                    # add the comment to the database, then send the message
                                    print('[!] Sockbot found a sock! Placing ID: {} in the database'.format(comment.id))
                                    database.insert_db_data(table, '(NULL, ?, CURRENT_TIMESTAMP)', (comment.id,))
                                    pk_id = database.dbcur.execute('SELECT max(id) FROM {}'.format(table)).fetchone()[0]
                                    """
                                    # Unused end condition
                                    if int(pk_id) == 1000:
                                        r.send_message('Always_SFW', 'SOCKBOT LIMIT REACHED', 'SOCKBOT LIMIT REACHED')
                                        quit()
                                    """
                                    message_string = '<h1>Sock #{} was spotted at:</h1> {} <br><hr><br>' \
                                                     'Post contents: <p>{}</p><br>' \
                                                     'Post time: <b>{}</b><br>'.format(
                                                        pk_id,
                                                        comment.permalink,
                                                        comment.body,
                                                        strftime("%Y-%m-%d %H:%M:%S", gmtime())
                                                     )
                                    if not subreddit == 'EiteDagerous' and not (comment.body.lower() == 'sock' or len(comment.body) < 6):
                                        print('[!] Sending string about sock #{}'.format(pk_id))
                                        r.send_message(user, 'Sock #{} spotted!'.format(pk_id), html2text(message_string))  # user, title, contents
                                    reply_string = '[ಠ‿ಠ]<br><br>' \
                                                   '<h1>SOCK DETECTED</h1><br><br>' \
                                                   'tfaddy has been notified.<br>' \
                                                   '<hr><br>' \
                                                   'I am <a href="https://imgur.com/RKuioGf">an automated bot running from a Raspberry Pi</a>, created and maintained by <a href ="https://www.reddit.com/user/Always_SFW">CMDR Purrcat, /u/Always_SFW</a>.<br>' \
                                                   'Click <a href="https://www.reddit.com/r/EliteDangerous/comments/3sz817/learn_how_to_get_ripped_in_4_weeks/cx261wx">here</a> to find out why I exist. You can find my source code <a href="https://github.com/Winter259/sockbot">on GitHub</a>.<br>' \
                                                   'Socks detected so far: <b>{}</b><br>' \
                                                   'Online since: <b>{} (GMT)</b><br>'.format(pk_id, startup_time)
                                    post_string = html2text(reply_string)
                                    post_string += 'Need something to keep your feet warm? How about some [ELITE DANGEROUS SOCKS??](https://www.frontierstore.net/merchandise/elite-dangerous-logo-socks-black.html)'
                                    if subreddit == 'EiteDagerous':
                                        post_string = 'ಠ_ಠ'
                                    # if the comment is unimaginative...
                                    if comment.body.lower() == 'sock' or len(comment.body) < 8:
                                        post_string = 'You could try to be a bit more imaginative with your post...'
                                    if comment.author.name == 'tfaddy':
                                        post_string = 'Hey man, I\'m your biggest fan!'
                                    print('[!] Replying to comment with ID: {}'.format(comment.id))
                                    comment.reply(post_string)
                                    pause('Holding after sending message', send_delay)
                except Exception as e:
                    print('[-] Comment parse exception:'.format(e))
                sleep(cycle_delay)
        print('[+] Current socks in DB count: {}, Socks spotted this cycle: {}'.format(len(get_comment_id_list(database, table)), socks_spotted))

if __name__ == '__main__':
    main()

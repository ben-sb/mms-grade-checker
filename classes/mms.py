import requests
from bs4 import BeautifulSoup as soup
from datetime import datetime
from threading import Thread
from classes.feedback import Feedback
import time

class MMS_Monitor():
    def __init__(self, session_cookie, courseworks_to_monitor, refresh_time):
        self.session = requests.Session()
        self.session.cookies.set('JSESSIONID', session_cookie)
        self.base_url = 'https://mms.st-andrews.ac.uk'
        self.courseworks_to_monitor = courseworks_to_monitor
        self.refresh_time = refresh_time
        self.feedbacks = []

    def log(self, text):
        print('[{}]: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), text))

    def run(self):
        if self.get_modules():
            self.log('Logged in')
            self.load_modules()
        else:
            self.log('Failed to login')
            exit(1)

    def get_modules(self):
        get_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': 'mms.st-andrews.ac.uk',
            'Pragma': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
        }
        modules_req = self.session.get('https://mms.st-andrews.ac.uk/mms/user/me/Modules', headers=get_headers)
        self.modules_page_html = modules_req.text

        return modules_req.status_code == 200 and 'Web Login Service - Loading Session Information' not in modules_req.text

    def load_modules(self):
        modules_page = soup(self.modules_page_html, 'html.parser')
        module_cards = modules_page.findAll('div', {'class':'card card-primary'})
        found = False

        for module_card in module_cards:
            courseworks = module_card.findAll('a', {'class':'resource coursework'})
            for coursework in courseworks:
                if coursework.text in self.courseworks_to_monitor:
                    self.log('Started monitoring ' + coursework.text)
                    t = Thread(target=self.monitor_module, args=(coursework.text, coursework['href'],))
                    t.start()
                    found = True
        
        if not found:
            self.log('Found no matching courseworks')

    def monitor_module(self, coursework_name, relative_path):
        request_count = 0
        while True:
            module_headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
                'Connection': 'keep-alive',
                'Host': 'mms.st-andrews.ac.uk',
                'Referer': 'https://mms.st-andrews.ac.uk/mms/user/me/Modules',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
            }

            try:
                coursework_get = self.session.get(self.base_url + relative_path, headers=module_headers)
            except:
                self.log('Error with request for {}'.format(coursework_name))
                self.wait()
                continue

            coursework_page = soup(coursework_get.text, 'html.parser')
            assignments_table = coursework_page.find('table', {'id':'studentAssignmentsTable'})

            rows = assignments_table.findAll('tr')

            found_new_feedback = False
            for row in rows:
                cells = row.findAll('td')
                if len(cells) > 0:
                    name = cells[0].text.strip()
                    comments = cells[5].findAll('a')
                    grade = cells[6].text.strip()

                    cmnts = []
                    for comment in comments:
                        if 'Add Comment' not in comment.text.strip():
                            cmnts.append(comment.text.strip())

                    if grade.strip() == '':
                        continue

                    feedback = Feedback(name, cmnts, grade)

                    exists = False
                    for existing_feedback in self.feedbacks:
                        if existing_feedback == feedback:
                            exists = True

                    if not exists:
                        found_new_feedback = True
                        if request_count == 0:
                            self.log('Loaded existing feedback for {}'.format(coursework_name))
                        else:
                            self.log('Detected new feedback for {}'.format(coursework_name))
                        feedback.display()
                        print('\n')
                        self.feedbacks.append(feedback)


            if not found_new_feedback:
                self.log('No new feedback detected for {}'.format(coursework_name))
            request_count += 1

            self.wait()

    def wait(self):
        self.log(f'Waiting {self.refresh_time}s')
        time.sleep(self.refresh_time)

    def generate_feedback_url(self, current_url, relative_path):
        last_slash_pos = current_url.rfind('/')
        if last_slash_pos < 0:
            return None

        return current_url[0:last_slash_pos + 1] + relative_path

    def get_domain(self, url):
        return url.split('//')[1].split('/')[0]
import os
import re
import scrapy

REGEX_JOB_ID = r"= {jk:'(.*)',efccid:"


class IndeedP2Spider(scrapy.Spider):
    name = "indeed-p2"

    def __init__(self, query='target', **kwargs):
        self.query = query
        self.page_id = 0
        self.start_url = self.get_next_url(query, self.page_id)
        # Python 2
        super(IndeedP2Spider, self).__init__(**kwargs)
        # Python 3
        # super().__init__(**kwargs)

    def start_requests(self):
        yield scrapy.Request(url=self.start_url, callback=self.parse)

    def parse(self, response):
        url = response.url
        matched_job_ids = re.findall(REGEX_JOB_ID, response.body)
        job_id_filename = 'output/{}/job_ids.txt'.format(self.query)

        # Create the file if it does not exist
        if not os.path.exists(job_id_filename):
            os.makedirs('output/{}'.format(self.query))
            os.makedirs('output/{}/p2_raw_htmls'.format(self.query))
            os.makedirs('output/{}/p3_raw_htmls'.format(self.query))
            open(job_id_filename, 'a').close()

        # Records job ids crawled from p2
        with open(job_id_filename, "a+") as job_ids_file:
            for matched_job_id in matched_job_ids:
                job_ids_file.write(matched_job_id + "\n")

        # Keep a copy of raw file for validation in the future
        raw_html_filename = 'output/{}/p2_raw_htmls/{}-{}.html'.format(
            self.query,
            self.query,
            self.page_id
        )
        with open(raw_html_filename, 'wb+') as f:
            f.write(response.body)
        self.log('Saved file %s' % raw_html_filename)

        self.page_id += 10
        # crawl next page
        if len(matched_job_ids) != 0:
            yield scrapy.Request(
                self.get_next_url(self.query, self.page_id),
                callback=self.parse
            )

    @staticmethod
    def get_next_url(query, page_id):
        return "https://www.indeed.com/jobs?q={}&l=CA&fromage=14&start={}".format(
            query,
            page_id
        )

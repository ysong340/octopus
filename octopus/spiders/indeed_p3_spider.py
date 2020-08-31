import os
import csv
import scrapy

REGEX_JOB_ID = r"= {jk:'(.*)',efccid:"


class IndeedP2Spider(scrapy.Spider):
    name = "indeed-p3"

    def __init__(self, query='software%20engineer', **kwargs):
        self.start_url = 'https://www.indeed.com/jobs?q={}&start=0'.format(
            query
        )
        # Python 2
        self.query = query
        super(IndeedP2Spider, self).__init__(**kwargs)
        # Python 3
        # super().__init__(**kwargs)

    def start_requests(self):
        file = open("output/software%20engineer/job_ids.txt", "r")
        for job_id in file:
            yield scrapy.Request(url=self.get_url(job_id), callback=self.parse)

    def parse(self, response):
        url = response.url
        job_key = url.split("=")[-1]
        job_content_filename = 'output/{}/job_contents.txt'.format(self.query)

        # Create the file if it does not exist
        if not os.path.exists(job_content_filename):
            open(job_content_filename, 'a').close()

        name = response.xpath("//h1[contains(@class, 'icl-u-xs-mb--xs icl-u-xs-mt--none jobsearch-JobInfoHeader-title')]/text()").extract_first()
        company = response.xpath("//div[contains(@class, 'icl-u-lg-mr--sm icl-u-xs-mr--xs')]/text()").extract_first()
        location = response.xpath("//div[contains(@class, 'jobsearch-InlineCompanyRating icl-u-xs-mt--xs  jobsearch-DesktopStickyContainer-companyrating')]/*/text()").extract()[-1]
        details = " ".join(response.xpath("//div[contains(@id, 'jobDescriptionText')]/text()").extract())
        details += " ".join(response.xpath("//div[contains(@id, 'jobDescriptionText')]/*/text()").extract())
        details += " ".join(response.xpath("//div[contains(@id, 'jobDescriptionText')]/*/*/text()").extract())
        details += " ".join(response.xpath("//div[contains(@id, 'jobDescriptionText')]/*/*/*/text()").extract())
        details += " ".join(response.xpath("//div[contains(@id, 'jobDescriptionText')]/*/*/*/*/text()").extract())

        # Records job ids crawled from p2
        fields = ['job_name', 'company', 'location', 'details']
        with open(job_content_filename, 'a') as csv_file:
            # creating a csv writer object
            csv_writer = csv.writer(
                csv_file,
                delimiter=' ',
                quotechar='|',
                quoting=csv.QUOTE_MINIMAL
            )
            raw_row = [job_key, name, company, location, details]
            csv_writer.writerow([text.encode("utf8") for text in raw_row])

        # Keep a copy of raw file for validation in the future
        raw_html_filename = 'output/{}/p3_raw_htmls/{}.html'.format(
            self.query,
            job_key
        )

        with open(raw_html_filename, 'wb+') as f:
            f.write(response.body)
        self.log('Saved file %s' % raw_html_filename)


    @staticmethod
    def get_url(job_id):
        return "https://www.indeed.com/viewjob?jk={}".format(
            job_id
        )

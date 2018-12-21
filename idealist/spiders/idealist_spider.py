from datetime import datetime
import re
import json
import scrapy
import requests

from scrapy.utils.project import get_project_settings
from ..items import IdealistItems

project_settings = get_project_settings()
key_word = project_settings.get('KEYWORD')

headers = {"accept": "application/json",
           "content-type": "application/x-www-form-urlencoded",
           "Origin": "https://www.idealist.org",
           "Referer": "https://www.idealist.org/en/?functions=ACCOUNTING_FINANCE&functions=ADMINISTRATIVE&functions"
                      "=DATA_EVALUATION_ANALYSIS&functions=OPERATIONS&q={}&sort=relevance&type=JOB".format(key_word),
           "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/70.0.3538.102 Safari/537.36"}

params = {"params": "facets=*&hitsPerPage=1000&page=0&attributesToSnippet=%5B%22description%3A20%22%5D"
                    "&attributesToRetrieve=objectID%2Ctype%2Cpublished%2Cname%2Ccity%2Cstate%2Ccountry%2Curl%2CorgID"
                    "%2CorgUrl%2CorgName%2CorgType%2CgroupID%2CgroupUrl%2CgroupName%2CisFullTime%2CremoteOk%2Cpaid"
                    "%2ClocalizedStarts%2ClocalizedEnds&filters=("
                    "functions%3A'ACCOUNTING_FINANCE'%20OR%20functions%3A'ADMINISTRATIVE'%20OR%20functions%3A"
                    "'DATA_EVALUATION_ANALYSIS'%20OR%20functions%3A'OPERATIONS')%20AND%20type%3A'JOB'&aroundLatLng=53"
                    ".9%2C%2027.5667&aroundPrecision=15000&minimumAroundRadius=16000&getRankingInfo=true"
                    "&clickAnalytics=true&query={}".format(key_word)}

params_for_request = json.dumps(params, ensure_ascii=False)

url_for_start_request = "https://nsv3auess7-dsn.algolia.net/1/indexes/idealist7-production/query?x-algolia-agent=Algolia%20for%20vanilla%20JavaScript%203.30.0&x-algolia-application-id=NSV3AUESS7&x-algolia-api-key=c2730ea10ab82787f2f3cc961e8c1e06"


class Idealist(scrapy.Spider):
    name = 'Idealist'
    allowed_domains = ['idealist.org']

    def start_requests(self):
        resp = None
        try:
            resp = requests.post(url=url_for_start_request, data=params_for_request)
        except Exception:
            self.start_requests()
        data = [url for url in resp.json()['hits']]
        for data_for_request in data:
            url = 'https://www.idealist.org/data/website/jobs/' + data_for_request['objectID']
            yield scrapy.Request(
                url=url,
                callback=self.parse
            )

    def parse(self, response):
        resp = json.loads(response.body_as_unicode())
        line1 = resp.get('job', {}).get('address', {}).get('line1', {})
        line2 = resp.get('job', {}).get('address', {}).get('line2', {})
        street_address = '{} {}'.format(line1 if line1 is not None else '',
                                        line2 if line2 is not None else '')

        professional_level = resp.get('job', {}).get('professionalLevel')
        professional_level = professional_level if 'NONE' not in professional_level else None
        full_time = resp.get('job', {}).get('isFullTime')
        full_time = 'Full time' if full_time else None
        is_temporary = resp.get('job', {}).get('isTemporary')
        is_temporary = 'Temporary' if is_temporary else None
        is_contract = resp.get('job', {}).get('isContract')
        is_contract = 'Contract' if is_contract else None
        remote_ok = resp.get('job', {}).get('remoteOk')
        remote_ok = 'On-site Location' if remote_ok is False else None
        education = resp.get('job', {}).get('education')
        education = education if 'NO_REQUIREMENT' not in education else None
        details_at_a_glance = ', '.join(list(filter(None, [professional_level, full_time, is_temporary, is_contract,
                                                           remote_ok, education])))
        apply_url = resp.get('job', {}).get('applyUrl')
        apply_email = resp.get('job', {}).get('applyEmail')
        list_apply_urls_and_emails = 'Apply url : {}, Apply emails: {}'.format(apply_url, apply_email)
        salary_min = resp.get('job', {}).get('salaryMinimum')
        salary_max = resp.get('job', {}).get('salaryMaximum')
        salary_details = resp.get('job', {}).get('salaryDetails')
        salary = '{} {} {}'.format((str(salary_min) + ' -') if salary_min else '',
                                   str(salary_max) if salary_max else '',
                                   salary_details if salary_details else '')
        date = resp.get('job', {}).get('firstPublished', '')
        date_posted = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ') if date else ''
        job_description_data = resp.get('job', {}).get('description', '')
        job_description_data_with_new_line = job_description_data.replace('<br>', '\n') if job_description_data else ''
        job_description = re.sub("<.*?>", "",
                                 job_description_data_with_new_line) if job_description_data_with_new_line else ''
        how_to_apply_data = resp.get('job', {}).get('applyText', '')
        how_to_apply = ' '.join(re.sub("<.*?>", "", how_to_apply_data).split()) if how_to_apply_data else ''

        items = IdealistItems()
        items['url'] = response.url
        items['organization'] = resp.get('job', {}).get('org', {}).get('name')
        items['organization_URL'] = 'https://www.idealist.org' + resp.get('job', {}).get('org', {}).get('url', {}).get(
            'en')
        items['job_posting_title'] = resp.get('job', {}).get('name')
        items['job_description'] = job_description
        items['streetAddress'] = street_address
        items['addressLocality'] = resp.get('job', {}).get('address', {}).get('city', '-')
        items['addressRegion'] = resp.get('job', {}).get('address', {}).get('state', '-')
        items['postalCode'] = resp.get('job', {}).get('address', {}).get('zipcode', '-')
        items['addressCountry'] = resp.get('job', {}).get('address', {}).get('country', '-')
        items['details_at_a_glance'] = details_at_a_glance
        items['how_to_apply'] = how_to_apply
        items['list_emails_and_urls'] = list_apply_urls_and_emails
        items['salary'] = salary if salary else ''
        items['date_posted'] = date_posted
        org_id = resp.get('job', {}).get('org', {}).get('id')
        if org_id:
            yield scrapy.Request(url=('https://www.idealist.org/data/website/organizations/' +
                                      org_id),
                                 callback=self.parse_organization,
                                 meta={
                                     'items': items
                                 }, dont_filter=True)
        else:
            yield items

    def parse_organization(self, response):
        organizations = json.loads(response.body_as_unicode())
        items = response.meta.get('items')
        items['organization_WEB_SITE'] = organizations.get('org', {}).get('website', '-')
        yield items

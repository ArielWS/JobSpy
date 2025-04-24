from __future__ import annotations
import json
import math
import re
import time
import random
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from bs4 import BeautifulSoup

from jobspy.ziprecruiter.constant import (
    API_HEADERS,
    build_cookie_payload,
    USER_AGENTS,
    HTML_HEADERS,
)
from jobspy.util import (
    extract_emails_from_text,
    create_session,
    markdown_converter,
    remove_attributes,
    create_logger,
)
from jobspy.model import (
    JobPost,
    Compensation,
    Location,
    JobResponse,
    Country,
    DescriptionFormat,
    Scraper,
    ScraperInput,
    Site,
)
from jobspy.ziprecruiter.util import get_job_type_enum, add_params

import cfscrape

log = create_logger("ZipRecruiter")

class ZipRecruiter(Scraper):
    base_url = "https://www.ziprecruiter.com"
    api_url  = "https://api.ziprecruiter.com"

    def __init__(
        self,
        proxies: list[str] | str | None = None,
        ca_cert: str | None            = None
    ):
        super().__init__(Site.ZIP_RECRUITER, proxies=proxies)

        # 1) Build raw session with proxy/CA logic
        raw_session = create_session(proxies=proxies, ca_cert=ca_cert)
        self.session = cfscrape.create_scraper(sess=raw_session)

        # 1.1) Normalize & apply the first proxy if provided
        if proxies:
            if isinstance(proxies, list):
                self.proxies = [
                    p if p.startswith(("http://", "https://")) else "http://" + p
                    for p in proxies
                ]
            else:
                self.proxies = (
                    proxies
                    if proxies.startswith(("http://", "https://"))
                    else "http://" + proxies
                )
            first = self.proxies[0] if isinstance(self.proxies, list) else self.proxies
            self.session.proxies.update({"http": first, "https": first})
        else:
            self.proxies = None

        # 2) Pick initial User-Agent
        initial_ua = random.choice(USER_AGENTS)

        # 3) Prime Cloudflare JS challenge on HTML and API domains
        try:
            # Set UA for priming
            self.session.headers.update({"User-Agent": initial_ua})
            # HTML domain
            self.session.get(self.base_url + "/", allow_redirects=True, timeout=10)
            self.session.headers.update(HTML_HEADERS)
            self.session.headers["Referer"] = f"{self.base_url}/"
            self.session.get(
                self.base_url + "/Search-Jobs-Near-Me", allow_redirects=True, timeout=10
            )
            # API subdomain
            self.session.get(self.api_url + "/", allow_redirects=True, timeout=10)
        except Exception as e:
            log.warning(f"Could not prime Cloudflare clearance: {e}")

        # 4) Build API headers with dynamic UA and apply
        api_headers = {**API_HEADERS, "User-Agent": initial_ua}
        self.session.headers.update(api_headers)
        self.last_user_agent = initial_ua

        # 5) Seed cookies via the event call
        self._get_cookies()

        # 6) Initialize internal state
        self.delay = 1
        self.jobs_per_page = 20
        self.seen_urls = set()
        self.proxy_index = 0
        self.request_count = 0
        self.user_agent_switch_interval = 5

    def get_rotated_headers(self) -> dict[str, str]:
        """
        Rotate proxies and user-agents. When UA changes, clear cookies and re-prime Cloudflare.
        """
        # ---- Proxy rotation ----
        if isinstance(self.proxies, list):
            proxy = self.proxies[self.proxy_index % len(self.proxies)]
            self.proxy_index += 1
        else:
            proxy = self.proxies

        # Normalize proxy URL
        if proxy and not proxy.startswith(("http://", "https://")):
            proxy = "http://" + proxy
        self.session.proxies.update({"http": proxy, "https": proxy})

        # ---- UA rotation ----
        self.request_count += 1
        if self.request_count % self.user_agent_switch_interval == 0:
            new_ua = random.choice(USER_AGENTS)
            if new_ua != self.last_user_agent:
                log.info("Switching to a new User-Agent. Clearing cookies & re-priming Cloudflare.")
                # clear cookies
                self.session.cookies.clear()

                # Rebuild API headers with new UA
                api_headers = {**API_HEADERS, "User-Agent": new_ua}
                self.session.headers.update(api_headers)
                self.last_user_agent = new_ua

                # Reseed cookies with the new UA
                self._get_cookies()

                # Re-prime Cloudflare challenges
                try:
                    # HTML domain priming with updated headers
                    self.session.headers.update(HTML_HEADERS)
                    self.session.headers["Referer"] = f"{self.base_url}/"
                    self.session.get(self.base_url + "/", allow_redirects=True, timeout=10)
                    self.session.get(
                        self.base_url + "/Search-Jobs-Near-Me",
                        allow_redirects=True,
                        timeout=10,
                    )
                    # API subdomain priming
                    self.session.headers.update({"User-Agent": new_ua})
                    self.session.get(self.api_url + "/", allow_redirects=True, timeout=10)
                except Exception as e:
                    log.warning(f"Failed to re-prime Cloudflare after UA rotation: {e}")
            else:
                log.info(f"Reusing existing User-Agent: {new_ua}")

        return dict(self.session.headers)

    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        """
        Scrapes ZipRecruiter for jobs with scraper_input criteria.
        :param scraper_input: Information about job search criteria.
        :return: JobResponse containing a list of jobs.
        """
        self.scraper_input = scraper_input
        job_list: list[JobPost] = []
        continue_token = None

        max_pages = math.ceil(scraper_input.results_wanted / self.jobs_per_page)
        for page in range(1, max_pages + 1):
            if len(job_list) >= scraper_input.results_wanted:
                break
            if page > 1:
                time.sleep(random.uniform(0.5, 2))  # Random delay between 3 and 7 seconds between page requests
            log.info(f"search page: {page} / {max_pages}")
            jobs_on_page, continue_token = self._find_jobs_in_page(
                scraper_input, continue_token
            )
            if jobs_on_page:
                job_list.extend(jobs_on_page)
            else:
                break
            if not continue_token:
                break
        return JobResponse(jobs=job_list[: scraper_input.results_wanted])

    def _find_jobs_in_page(
        self, scraper_input: ScraperInput, continue_token: str | None = None
    ) -> tuple[list[JobPost], str | None]:
        """
        Scrapes a page of ZipRecruiter for jobs with scraper_input criteria,
        rotating UA/proxy & clearing cookies when needed.
        """
        jobs_list: list[JobPost] = []
        params = add_params(scraper_input)
        if continue_token:
            params["continue_from"] = continue_token

        # --- rotate UA/proxy/cookies if it’s time ---
        self.get_rotated_headers()

        try:
            res = self.session.get(
                f"{self.api_url}/jobs-app/jobs",
                params=params,
                timeout=1,
            )
            time.sleep(random.uniform(0.5, 1.5))
            if res.status_code not in range(200, 400):
                if res.status_code == 429:
                    log.error("429 Response - rate-limited by ZipRecruiter")
                    time.sleep(random.uniform(2, 3))
                else:
                    log.error(
                        f"ZipRecruiter response status code {res.status_code} "
                        f"with response: {res.text}"
                    )
                return [], None
        except Exception as e:
            if "Proxy responded with" in str(e):
                log.error("Bad proxy")
            else:
                log.error(f"Error fetching jobs page: {e}")
            return [], None

        data = res.json()
        raw_jobs = data.get("jobs", [])
        next_token = data.get("continue")

        # process each job concurrently
        with ThreadPoolExecutor(max_workers=self.jobs_per_page) as executor:
            futures = [executor.submit(self._process_job, j) for j in raw_jobs]
        jobs_list = [job for job in (f.result() for f in futures) if job]

        return jobs_list, next_token


    def _process_job(self, job: dict) -> JobPost | None:
        """
        Processes an individual job dict from the response
        """
        time.sleep(random.uniform(0.5, 1.5))  # Delay between processing each job
        title = job.get("name")
        job_url = f"{self.base_url}/jobs//j?lvk={job['listing_key']}"
        if job_url in self.seen_urls:
            return
        self.seen_urls.add(job_url)

        description = job.get("job_description", "").strip()
        listing_type = job.get("buyer_type", "")
        description = (
            markdown_converter(description)
            if self.scraper_input.description_format == DescriptionFormat.MARKDOWN
            else description
        )
        company = job.get("hiring_company", {}).get("name")
        country_value = "usa" if job.get("job_country") == "US" else "canada"
        country_enum = Country.from_string(country_value)

        location = Location(
            city=job.get("job_city"), state=job.get("job_state"), country=country_enum
        )
        job_type = get_job_type_enum(
            job.get("employment_type", "").replace("_", "").lower()
        )
        date_posted = datetime.fromisoformat(job["posted_time"].rstrip("Z")).date()
        comp_interval = job.get("compensation_interval")
        comp_interval = "yearly" if comp_interval == "annual" else comp_interval
        comp_min = int(job["compensation_min"]) if "compensation_min" in job else None
        comp_max = int(job["compensation_max"]) if "compensation_max" in job else None
        comp_currency = job.get("compensation_currency")
        description_full, job_url_direct = self._get_descr(job_url)

        return JobPost(
            id=f'zr-{job["listing_key"]}',
            title=title,
            company_name=company,
            location=location,
            job_type=job_type,
            compensation=Compensation(
                interval=comp_interval,
                min_amount=comp_min,
                max_amount=comp_max,
                currency=comp_currency,
            ),
            date_posted=date_posted,
            job_url=job_url,
            description=description_full if description_full else description,
            emails=extract_emails_from_text(description) if description else None,
            job_url_direct=job_url_direct,
            listing_type=listing_type,
        )

    def _get_descr(self, job_url):
        # inject browser-like headers
        self.session.headers.update(HTML_HEADERS)
        self.session.headers["Referer"] = f"{self.base_url}/Search-Jobs-Near-Me"

        res = self.session.get(job_url, allow_redirects=True, timeout=10)
        description_full = job_url_direct = None
        if res.ok:
            soup = BeautifulSoup(res.text, "html.parser")
            job_descr_div = soup.find("div", class_="job_description")
            company_descr_section = soup.find("section", class_="company_description")
            job_description_clean = (
                remove_attributes(job_descr_div).prettify(formatter="html")
                if job_descr_div
                else ""
            )
            company_description_clean = (
                remove_attributes(company_descr_section).prettify(formatter="html")
                if company_descr_section
                else ""
            )
            description_full = job_description_clean + company_description_clean

            try:
                script_tag = soup.find("script", type="application/json")
                if script_tag:
                    job_json = json.loads(script_tag.string)
                    job_url_val = job_json["model"].get("saveJobURL", "")
                    m = re.search(r"job_url=(.+)", job_url_val)
                    if m:
                        job_url_direct = m.group(1)
            except:
                job_url_direct = None

            if self.scraper_input.description_format == DescriptionFormat.MARKDOWN:
                description_full = markdown_converter(description_full)

        return description_full, job_url_direct

    def _get_cookies(self):
        url = f"{self.api_url}/jobs-app/event"
        ua = self.session.headers["User-Agent"]
        payload = build_cookie_payload(ua)
        res = self.session.post(url, data=payload, timeout=10)
        res.raise_for_status()

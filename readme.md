# Nice Companies:
- Robinhood (https://careers.robinhood.com/#page-block-mzzcf1eaais) (no pages)
- Coinbase (https://www.coinbase.com/en-ca/careers/positions?department=Internships%2520%2526%2520Emerging%2520Talent%2520Positions) (no pages)
- Stripe (https://stripe.com/jobs/search?tags=University) (no pages)
- Ramp (https://ramp.com/emerging-talent#jobs) (no pages)
- Anduril (https://www.anduril.com/open-roles?employmentType=intern&) (no pages)
- Palantir (https://www.palantir.com/careers/open-positions/) (no pages)
- Rippling (possible issue with multiple duplicate positions with diff locations - we record this as 1 position)
- Wealthsimple (https://jobs.lever.co/wealthsimple) (no pages)  
- ScaleAI (https://scale.com/careers) (no pages)
- Databricks (https://www.databricks.com/company/careers/open-positions) (no pages)
- Cohere (https://jobs.ashbyhq.com/cohere?employmentType=Intern) (no pages)
- Figure (https://www.figure.ai/careers) (no pages)
- Replit (https://jobs.ashbyhq.com/replit) (no pages)
- Github (https://www.github.careers/careers-home/jobs?keywords=intern&sortBy=relevance&limit=100) (no pages since limit is 100 per page, but delimeter is page=1)
- Figma (https://www.figma.com/careers/#job-openings) (no pages)
- Notion (https://www.notion.com/careers) (no pages)
- Roblox (https://careers.roblox.com/jobs?groups=early-career-talent&type=internship) (pages, doesn't have page delimeter)
- Rho (https://www.rho.co/careers) (no pages)
- Jane Street (https://www.janestreet.com/join-jane-street/open-roles/?type=internship&location=all-locations) (no pages)
- Fizz (https://jobs.ashbyhq.com/fizz) (no pages)
- Intuit (https://jobs.intuit.com/category/internship-jobs/27595/9205024/1) (pages, but we can't access them)
- Citadel (https://www.citadel.com/careers/open-opportunities?experience-filter=internships&selected-job-sections=388,389,387,390&sort_order=DESC&per_page=10&action=careers_listing_filter) (pages, page delimeter is current_page)
- Block (https://block.xyz/careers/jobs?businessUnits[]=block&employeeTypes[]=Intern&query=intern) (no pages)
- Affirm ([greenhouse pages](https://job-boards.greenhouse.io/affirm/?keyword=intern) (pages, ?page=)

# Not so nice:
- Lockheed (Weird pages, sometimes gets 50+ jobs per page and sometimes not. Ended up with 150 scraped jobs even though )
- Plaid (Uses ripplematch which is weird)
- Brex (although they just might not have their internships on here)
- Snowflake (their intern stories are getting picked up as jobs)

# Unknown:
- OpenAI (no internships)
- Microsoft
- Vercel
- Mercury

# TODO:
- Verify robots.txt for each company (maybe use LLMs for this lol)
- Handle some sort of 404 error or other problem causing no jobs to be scraped (we shouldn't record this as no jobs present, since if the site is down the jobs probably still exist)
- Handle not so nice scenarios
- Turn down LLM temperature

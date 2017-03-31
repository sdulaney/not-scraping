var scraper = {
  iterator: '.profile-block',
  data: {
    Name: {
        sel: '.profile-block__name',
        method: 'text'
    },
    "Job Title": {
        sel: '.profile-block__job-title',
        method: 'text'
    },
    Area: {
        sel: '.profile-block__area',
        method: 'text'
    },
    Country: {
        sel: '.profile-block__country',
        method: 'text'
    },
    "Business Line": {
        sel: '.profile-block__business-line',
        method: 'text'
    },
    Mobile: {
        sel: '.numbers-wrapper__numbers--mobile',
        method: 'text'
    },
    Office: {
        sel: '.numbers-wrapper__numbers--office',
        method: 'text'
    },
    Email: {
        sel: '.email',
        attr: 'href'
    }
  }
};

function nextUrl($page) {
  return $page.find('.next.pagination-links_anchor').attr('href');
}

artoo.log.debug('Starting the scraper...');
var frontpage = artoo.scrape(scraper);

artoo.ajaxSpider(
  function(i, $data) {
    return nextUrl(!i ? artoo.$(document) : $data);
  },
  {
    limit: 30,
    throttle: 2000,
    scrape: scraper,
    concat: true,
    done: function(data) {
      artoo.log.debug('Finished retrieving data. Downloading...');
      artoo.saveCsv(
        frontpage.concat(data),
        {filename: 'agents.csv'}
      );
    }
  }
);

var scraper = {
  iterator: '.agentWrap',
  data: {
    Name: {
        sel: 'h3',
        method: 'text'
    },
    "Job Title / Phone": {
        sel: '.innerOne',
        method: function($) {
            return $(this).text().replace(/\"/g, '').trim();
        }
    },
    Specialization: {
        sel: '.linksList',
        method: 'text'
    },
    "Profile Link": {
        sel: 'a',
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
    limit: 100,
    throttle: 5000,
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

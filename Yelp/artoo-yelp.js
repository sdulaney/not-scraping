var scraper = {
  iterator: '.regular-search-result',
  data: {
    title: {sel: '.biz-name span'},
    phone: {
        sel: '.biz-phone'
    },
    link: {
        sel: '.biz-name',
        attr: 'href'
    },
    address: {
        sel: 'address',
        method: 'text'
    },
    neighborhood: {
        sel: '.neighborhood-str-list',
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
        {filename: 'yelp.csv'}
      );
    }
  }
);

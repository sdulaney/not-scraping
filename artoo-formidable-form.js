var scraper = {
  iterator: '#the-list tr',
  data: {
    name: {sel: '.row-title'},
    email: {
        sel: '.column-2_contact_email'
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
    limit: 20,
    throttle: 2000,
    scrape: scraper,
    concat: true,
    done: function(data) {
      artoo.log.debug('Finished retrieving data. Downloading...');
      artoo.saveCsv(
        frontpage.concat(data),
        {filename: 'formidable-form.csv'}
      );
    }
  }
);

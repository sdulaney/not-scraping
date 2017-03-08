var scraper = {
  iterator: '.showcaseItemInfo',
  data: {
    Title: {sel: 'h1'},
    WebsiteAddress: {
        sel: '.customShowcaseFieldweb dd a',
        attr: 'href'
    },
    ServicesOffered: {
        sel: '.customShowcaseFieldlive dd ul li',
        method: 'text'
    },
    TypeOfStore: {
        sel: '.customShowcaseFieldtype dd ul li',
        method: 'text'
    },
    StreetAddress: {
        sel: '.customShowcaseFieldstreet dd',
        method: 'text'
    },
    City: {
        sel: '.customShowcaseFieldcity dd',
        method: 'text'
    },
    State: {
        sel: '.customShowcaseFieldstate dd',
        method: 'text'
    },
    ZipCode: {
        sel: '.customShowcaseFieldzip dd',
        method: 'text'
    }
  }
};

function nextUrl($page) {
  return $page.find('td.title:last > a').attr('href');
}

artoo.log.debug('Starting the scraper...');
var frontpage = artoo.scrape(scraper);

artoo.ajaxSpider(
  function(i, $data) {
    return nextUrl(!i ? artoo.$(document) : $data);
  },
  {
    limit: 2,
    scrape: scraper,
    concat: true,
    done: function(data) {
      artoo.log.debug('Finished retrieving data. Downloading...');
      artoo.saveCsv(
        frontpage.concat(data),
        {filename: 'store.csv'}
      );
    }
  }
);

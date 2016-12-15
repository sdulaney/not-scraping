// Does not download JSON correctly, downloads in 4 strings
var newList = artoo.scrapeTable('.agridtable', {
  value: 'text',
  method: function($) {
        return $(this).text().trim().replace('&nbsp;', '').replace(/\s+/g,' ');

  }
});
artoo.savePrettyJson(niceList);
niceList



var niceList = artoo.scrape('td', {
  method: function($) {
    return $(this).text().replace('&nbsp;', '').replace(/\s+/g,' ');
  },
});
artoo.savePrettyJson(niceList);
niceList


// recursive
var niceList = artoo.scrape('agridtable', function($) {
  return artoo.scrape($(this).find('abodyinfo'), 'text');
});
niceList



artoo.scrape('agridtable', function($) {
  return artoo.scrape($(this).find('ul.sublist > li'), 'text');
});

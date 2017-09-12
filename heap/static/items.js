var getItems = function(page, sources) {
  var query = {};
  if (page) {
    query.page = page;
  }
  if (sources) {
    query.sources = sources;
  }
  $('.items').empty();
  $.post('/list_items/', query, function(data) {
    data.items.forEach(function(item) {
      var itemDiv = $('<div>').addClass('item').attr('data-id', item.pk);
      var itemLink = $('<a>').attr('href', item.url).text(item.url);
      itemDiv.append(itemLink);
      $('.items').append(itemDiv);
    });

    $('.prev').show();
    $('.next').show();
    if (page === 1) {
      $('.prev').hide();
    } else if (data.total === page) {
      $('.next').hide();
    }
    $('.page').text(page + ' of ' + data.total);
  });
};

var page = 1;
var sources = [];
$(document).ready(function() {
  "use strict";
  $('.next').click(function() {
    page++;
    getItems(page, sources);
  });

  $('.prev').click(function() {
    page--;
    getItems(page, sources);
  });

  $('.source').each(function() {
    if ($(this).hasClass('active')) {
      if (!Number.isNaN(parseInt($(this).attr('data-id')))) {
        sources.push(parseInt($(this).attr('data-id')));
      }
    }
  });

  $('.source').click(function() {
    $(this).toggleClass('active');
    sources = [];
    $('.source').each(function() {
      if ($(this).hasClass('active')) {
        sources.push(parseInt($(this).attr('data-id')));
      }
    });
    getItems(page, sources);
  });
  getItems(1, sources);
});

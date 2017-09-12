var delete_action = function(event) {
    "use strict";
    $.post('/feed/delete_source/',{pk: event.target.parentNode.id}, function(res){
        if (res.success) {
            $(event.target.parentNode).slideUp(200, function() {
                event.target.parentNode.remove();
            });
        }
    });
};

$(document).ready(function() {
    "use strict";
    $('.selector').click(function() {
            $('#rss_error').text('');
        $('.selector').removeClass('active');
        $(this).addClass('active');
        $('.form').css('display', 'none');        
        var name = $(this).attr('data-name');
        console.log('#add_' + name);
        $('#add_' + name).css('display', 'block');
    });

    function addLoading() {
        var loader = $('<div>').attr('id','loader');
        var top = $('<div>').attr('id','top');
        var bottom = $('<div>').attr('id','bottom');
        var line = $('<div>').attr('id','line');
        loader.append(top);
        loader.append(bottom);
        loader.append(line);
        loader.hide();
        $('#rss_feeds').prepend(loader);
        loader.slideDown(200);
    }

    function removeLoading() {
        $('#loader').slideUp(200, function() {
            $('#loader').remove();
        });
    }

    $('#add_rss_button').click(function() {
        $('#rss_error').text('');
        addLoading();
        $.post("/feed/add_source/", {url:$('#rss_url').val()}, function(res) {
            removeLoading();
            if (res.success) {
                $('#rss_url').val('');
                $('#added').slideDown(200);
                var rss_div = $('<div>', {class: 'source list_item', id: res.source.pk});
                var name_div = $('<div>', {class: 'list_item_name', text: res.source.name});
                var url_div = $('<div>', {class: 'list_item_desc', text: res.source.url});
                var button_div = $('<div>', {class: 'delete_button small_button', text: 'Delete'});
                button_div.click(delete_action);
                rss_div.append(name_div);
                rss_div.append(url_div);
                rss_div.append(button_div);
                rss_div.hide();
                $('#rss_feeds').prepend(rss_div);
                rss_div.slideDown(200);
                setTimeout(function() {
                    $('#added').slideUp(200);
                }, 1000);
            } else {
                if (res.url) {
                    window.location = res.url;
                }
                $('#rss_error').text('Invalid Score');
            }
        }).fail(add_fail);
    });

    $('#rss_url').keypress(function(e) {
      if (e.which === 13) {
        $('#add_rss_button').click();
      }
    });

    $('#add_hn_button').click(function() {
        $('#rss_error').text('');
        addLoading();
        $.post("/feed/add_hn_source/", {score: $('#hn_score').val()}, function(res) {
            removeLoading();
            if (res.success) {
                $('#hn_score').val('');
                $('#added').slideDown(200);
                var rss_div = $('<div>', {class: 'source list_item', id: res.source.pk});
                var name_div = $('<div>', {class: 'list_item_name', text: res.source.name});
                var url_div = $('<div>', {class: 'list_item_desc', text: res.source.url});
                var button_div = $('<div>', {class: 'delete_button small_button', text: 'Delete'});
                button_div.click(delete_action);
                rss_div.append(name_div);
                rss_div.append(url_div);
                rss_div.append(button_div);
                rss_div.hide();
                $('#rss_feeds').prepend(rss_div);
                rss_div.slideDown(200);
                setTimeout(function() {
                    $('#added').slideUp(200);
                }, 1000);
            } else {
                if (res.url) {
                    window.location = res.url;
                }
                $('#rss_error').text('Invalid Url');
            }
        }).fail(add_fail);
    });

    $('#hn_score').keypress(function(e) {
      if (e.which === 13) {
        $('#add_hn_button').click();
      }
    });

    $('#add_reddit_button').click(function() {
        $('#rss_error').text('');
        var key = makeId();
        $.cookie("reddit-key", key, {path: '/' });
        var redirect_url = 'http://heap.nobr.me/feed/redditd/';
        redirect_url = encodeURIComponent(redirect_url);
        var url = 'https://www.reddit.com/api/v1/authorize?client_id=s03SUqQUXI4Txw&response_type=code&state=' + key + '&redirect_uri=' + redirect_url + '&duration=permanent&scope=read';
        window.location = url;
    });

    function add_fail() {
        removeLoading();
        $('#rss_error').text('Sorry. There was an error.');
        setTimeout(function() {
            $('#rss_error').slideUp(200);
            setTimeout(function() {
                $('#rss_error').text('');
                $('#rss_error').slideDown(200);
            }, 200);
        }, 2000);
    }

    $('.delete_button').click(delete_action);
});

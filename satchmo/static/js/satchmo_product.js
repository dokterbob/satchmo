var satchmo = satchmo || {};

// Get the current selected product price.  If taxed is true, then
// return the price inclusive of taxes.
satchmo.get_current_price = function(detail, qty, taxed) {
    var k = taxed ? "TAXED" : "PRICE";
    var prices = detail[k];
    if (prices) {
        var best = prices['1'];
        if (qty > 1) {
            for (var pricekey in prices) {
                var priceqty = parseInt(pricekey);
                if (priceqty > qty) {
                    break;
                }
                best = prices[pricekey];
            }
        }
        return best;        
    }
    else {
        return ""
    }
};

satchmo.make_optionkey = function() {
    var work = Array(satchmo.option_ids.length);
    for (var ix=0; ix<satchmo.option_ids.length; ix++) {
        var k = "#" + satchmo.option_ids[ix];
        var v = $(k).fieldValue()[0];
        work[ix] = v;
    }
    return work.join('::');
};
        
// used for sorting numerically
satchmo.numeric_compare = function(a, b) {
    return a-b;
};
   
satchmo.option_ids = "";
        
// Update the product name
satchmo.set_name = function(name) {
    $("#productname").attr('value', name);
};

satchmo.set_option_ids = function(arr) {
    arr.sort(satchmo.numeric_compare);
    satchmo.option_ids = arr;
};

// Update the product price
satchmo.set_price = function(price) {
    $("#price").text(price);
};

satchmo.show_error = function(msg) {
    var section = $('#js_error');
    if (section.length == 0) {
        if (msg != "") {
            $('form#options').before("<div id='js_error' class='error'>" + msg + "</div>");
        }
    }
    else {
        section.text(msg);
        if (msg == "") {
            section.hide();
        }
    }
    var disabled = (msg != "");
    $('#addcart').attr('disabled', disabled);
};
    
// update name and price based on the current selections
satchmo.update_price = function() {
    var key = satchmo.make_optionkey();
    var detail = satchmo.variations[key];
    var msg = "";
    if (detail) {
        var qty = parseInt($('#quantity').fieldValue()[0]);
        satchmo.set_name(detail['SLUG']);
        var price = satchmo.get_current_price(detail, qty, satchmo.default_view_tax);
        satchmo.set_price(price);
        if (qty && qty > detail['QTY']) {
            if (detail['QTY'] == -1) {
                msg = "Sorry, we are out of stock on that combination.";
             }
             else {
                 msg = "Sorry, we only have " + detail['QTY'] + " available in that combination.";
             }
        }
    }
    else {
        msg = "Sorry, we don't have any of that combination available.";
    }
    satchmo.show_error(msg);
};

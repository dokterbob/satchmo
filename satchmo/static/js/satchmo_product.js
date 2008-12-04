var satchmo = satchmo || {};

satchmo.use_sale_prices = true;

// Get the current selected product price.
satchmo.get_current_price = function(detail, qty, use_sale) {
    var taxed = satchmo.default_view_tax,
        k, prices;
            
    if (use_sale) {
        k = taxed ? "TAXED_SALE" : "SALE";
    }
    else {
        k = taxed ? "TAXED" : "PRICE";
    }
    
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
    var key = satchmo.make_optionkey(),
        detail = satchmo.variations[key],
        msg = "",
        use_sale, sale_price, full_price;
        
    if (detail) {
        var qty = parseInt($('#quantity').fieldValue()[0]);
        satchmo.set_name(detail['SLUG']);
        
        if (!satchmo.variations['SALE']) {
            use_sale = false;
        }
        else {
            use_sale = satchmo.use_sale_prices;
        }

        if (use_sale) {
            full_price = satchmo.get_current_price(detail, qty, false);
            $('#fullprice').text(full_price);

            sale_price = satchmo.get_current_price(detail, qty, true);
        }
        else {
            sale_price = satchmo.get_current_price(detail, qty, false);
            $('#fullprice').hide();
        }

        satchmo.set_price(sale_price);

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

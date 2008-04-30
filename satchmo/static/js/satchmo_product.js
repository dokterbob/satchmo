var satchmo = satchmo || {};

// Get the current selected product price.  If taxed is true, then
// return the price inclusive of taxes.
satchmo.get_current_price = function(slug, taxed) {
    if (!slug) { 
        slug = satchmo.get_current_slug(); 
    }
    var qty = parseInt($('#quantity').fieldValue()[0]);
    var k = taxed ? "taxes" : "prices";
    var prices = satchmo[k][slug];
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
};
    
// look up the slug by options selected
satchmo.get_current_slug = function() {
    var optkey = satchmo.make_optionkey();
    return satchmo.optmap[optkey];
};
    
// Update the product name
satchmo.set_name = function(name) {
    $("#productname").attr('value', name);
};

// Update the product price
satchmo.set_price = function(price){
    $("#price").text(price);
};
    
// update name and price based on the current selections
satchmo.update_price = function() {
    slug = satchmo.get_current_slug();
    satchmo.set_name(slug);
    satchmo.set_price(satchmo.get_current_price(slug, satchmo.default_view_tax));
};

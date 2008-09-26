var satchmo = satchmo || {};
satchmo.ship_form_toggler = function(state) {
    var inputs = $('tr.shiprow input');
    inputs.attr('disabled', state);
    var selects = $('tr.shiprow select')
    selects.attr('disabled', state);
    var rows = $('tr.shiprow');
    if (state) {
        rows.addClass('disabled');
        inputs.each(function() {
            $(this)[0].value = "";
        });
        selects.each(function() {
            $(this)[0].value = "";
        });
    } else {
        rows.removeClass('disabled');
    }
};

satchmo.update_ship_copy = function(elt) {
    var state = $(elt)[0].checked;
    satchmo.ship_form_toggler(state);
}

$(function() {
    $('#id_copy_address').click(function() {
        satchmo.update_ship_copy(this);
    });
    satchmo.update_ship_copy('#id_copy_address');
});

name_change = function() {
    var first_name = $('#id_first_name').attr('value');
    var last_name = $('#id_last_name').attr('value');
    if (!first_name ) { first_name = '' };
    if (!last_name ) { last_name = '' };
    $('#id_addressee').attr('value',  jQuery.trim(first_name + ' ' + last_name));
    $('#id_ship_addressee').attr('value', $('#id_addressee').attr('value'));
};

$(document).ready(function() {
    name_change();
    $('#id_first_name').bind("change", {}, name_change);
    $('#id_last_name').bind("change", {}, name_change);
    $('#id_addressee').bind("change", function() {
         $('#id_ship_addressee').attr('value', $('#id_addressee').attr('value'));
    });
});
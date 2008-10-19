var satchmo = satchmo || {};

satchmo.required_issue_types = [];

satchmo.maybe_require_issue_fields = function() {
    var c = $('#id_credit_type').fieldValue();
    req = false;
    for (var ix in satchmo.required_issue_types) {
        var f = satchmo.required_issue_types[ix];
        if (f == c) {
            req = true;
            log.debug('match = ' + f);
            break;
        }
    }
    satchmo.require_issue_fields(req);
}

satchmo.require_issue_fields = function(state) {
    log.debug('require issue fields = ' + state);
    if (state) {
        $('.issue').show();
    }
    else {
        $('.issue').hide();
    }
}

satchmo.setup_issue_fields = function(required) {
    satchmo.required_issue_types = required;
    $('#id_credit_type').change(satchmo.maybe_require_issue_fields);
    satchmo.maybe_require_issue_fields();
}
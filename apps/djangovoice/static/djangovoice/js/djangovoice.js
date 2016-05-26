var dv_data = {
    div: {
        widget: document.getElementById('djangovoice-widget'),
        dialogbox: document.getElementById('djangovoice-dialogbox')
    }
};

var dv_connectSignals = function() {
    var closeButton = dv_data.div.dialogbox.getElementsByTagName('img')[0];
    dv_data.div.widget.onclick = function() {
        if (dv_data.div.dialogbox.style.display === 'block') {
            dv_data.div.dialogbox.style.display = 'none';
        } else {
            dv_data.div.dialogbox.style.display = 'block';
        }
    };
    closeButton.onclick = function() {
        dv_data.div.dialogbox.style.display = 'none';
    };
};

dv_connectSignals();

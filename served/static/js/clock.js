/**************************
* Monitor application     *
* Clock displayer         *
* Author: Stephane Diemer *
**************************/

function Clock() {
    this.date = "";
    this.hour = "";
    this.date_element = null;
    this.hour_element = null;

    var obj = this;
    if (window.attachEvent) // IE
        window.attachEvent("onload", function () { obj.init(); });
    else
        window.addEventListener("load", function () { obj.init(); }, true);
}

Clock.prototype.init = function () {
    this.date_element = document.getElementById("date_place");
    this.hour_element = document.getElementById("hour_place");
    this.refresh();
};

Clock.prototype.refresh = function () {
    var now = new Date();
    var y, m, d, H, M, S;
    y = now.getFullYear();
    m = now.getMonth() + 1;
    d = now.getDate();
    H = now.getHours();
    M = now.getMinutes();
    S = now.getSeconds();
    var new_date = (y < 10 ? "0"+y : y)+" - "+(m < 10 ? "0"+m : m)+" - "+(d < 10 ? "0"+d : d);
    var new_hour = (H < 10 ? "0"+H : H)+" : "+(M < 10 ? "0"+M : M)+" : "+(S < 10 ? "0"+S : S);

    if (new_date != this.date) {
        this.date = new_date;
        this.date_element.innerHTML = new_date;
    }
    this.hour_element.innerHTML = new_hour;

    var obj = this;
    setTimeout(function() {
        obj.refresh();
    }, 1000);
};

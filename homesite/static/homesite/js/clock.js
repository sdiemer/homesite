/**************************
* Clock displayer         *
**************************/

function Clock () {
    this.date = '';
    this.dateElement = null;
    this.hourElement = null;

    const obj = this;
    window.addEventListener('load', function () {
        obj.dateElement = document.getElementById('date_place');
        obj.hourElement = document.getElementById('hour_place');
        obj.refresh();
        setInterval(function () {
            obj.refresh();
        }, 1000);
    }, true);
}

Clock.prototype.refresh = function () {
    const now = new Date();
    const y = now.getFullYear();
    const m = now.getMonth() + 1;
    const d = now.getDate();
    const H = now.getHours();
    const M = now.getMinutes();
    const S = now.getSeconds();
    const newDate = (y < 10 ? '0' + y : y) + ' - ' + (m < 10 ? '0' + m : m) + ' - ' + (d < 10 ? '0' + d : d);
    const newHour = (H < 10 ? '0' + H : H) + ' : ' + (M < 10 ? '0' + M : M) + ' : ' + (S < 10 ? '0' + S : S);

    if (newDate != this.date) {
        this.date = newDate;
        this.dateElement.innerHTML = newDate;
    }
    this.hourElement.innerHTML = newHour;
};

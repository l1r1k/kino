const modalWindow = document.querySelector('.buyticket-modal');
const closeModalWindowBTN = document.querySelector('.closemodal-btn');
const premierWidgetOpenBTNs = document.querySelectorAll('#openPremierWidget');
const buyTicketBTN = document.getElementById('buyticket-btn');

if (buyTicketBTN){
    buyTicketBTN.onclick = function() {
        modalWindow.hidden = false;
    };
}

if (closeModalWindowBTN){
    closeModalWindowBTN.onclick = function(){
        modalWindow.hidden = true;
    };   
}

for (let premierWidgetOpenBTN of premierWidgetOpenBTNs){
    premierWidgetOpenBTN.onclick = function(e) {
        e.preventDefault();
        var $target = $(e.currentTarget);
        var prismaTheatreId = $target.data('prisma-theatre-id');
        var filmId = $target.data('film-id');
        var sessionId = $target.data('session-id');
        var apiHost = "https://widget-new.premierzal.ru";
        var metrikaId = "";
        var bar = ""; 
        var roistatVisit ="";
        initPaymentWidgetNew($target, prismaTheatreId, sessionId, apiHost,metrikaId,bar,roistatVisit, filmId);
    };
}
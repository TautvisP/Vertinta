document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');
    if (!calendarEl) return;
    
    // Get calendar events data from the global variable
    const eventsData = window.calendarEvents || [];
    
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev dayGridMonth',
            center: 'title',
            right: 'listMonth next'
        },
        locale: 'lt',
        events: eventsData,
        eventTimeFormat: {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        },
        firstDay: 1,
        navLinks: true,
        
        // Important event display settings
        dayMaxEvents: 1,             // Only show 3 events per day
        dayMaxEventRows: 1,          // Same as dayMaxEvents but for rows
        fixedWeekCount: true,        // Forces calendar to always display 6 weeks
        handleWindowResize: true,    // Redraw on window resize
        height: 'auto',              // Auto height based on content
        eventDisplay: 'block',       // Block-style events
        
        // Ensure month views never expand past their container
        views: {
            dayGridMonth: {
                dayMaxEventRows: 3,
                dayMaxEvents: 3
            }
        },
        
        buttonText: {
            month: 'Mėnuo',
            list: 'Sąrašas',
        },
        moreLinkClick: 'popover',

        eventClassNames: function(arg) {
            return [arg.event.extendedProps.eventType || 'other'];
        },
        eventDidMount: function(info) {
            if (!info.event.extendedProps.eventType) {
                let eventTitle = info.event.title.toLowerCase();
                if (eventTitle.includes('meeting') || eventTitle.includes('susitikimas')) {
                    info.el.classList.add('meeting');
                } else if (eventTitle.includes('deadline') || eventTitle.includes('terminas')) {
                    info.el.classList.add('deadline');
                } else if (eventTitle.includes('visit') || eventTitle.includes('vizitas')) {
                    info.el.classList.add('site-visit');
                } else {
                    info.el.classList.add('other');
                }
            }
            
            info.el.setAttribute('title', 
                `${info.event.title}\n${info.event.start.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`);
            
            info.el.addEventListener('mouseenter', function() {
                this.style.boxShadow = '0 3px 8px rgba(0,0,0,0.2)';
                this.style.transform = 'translateY(-1px)';
                this.style.zIndex = '5';
            });
            
            info.el.addEventListener('mouseleave', function() {
                this.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)';
                this.style.transform = 'translateY(0)';
                this.style.zIndex = '1';
            });
        },
        dayHeaderDidMount: function(info) {
            const headerElement = info.el.querySelector('.fc-col-header-cell-cushion');
            if (headerElement) {
                headerElement.textContent = 
                    headerElement.textContent.charAt(0).toUpperCase() +
                    headerElement.textContent.slice(1);
            }
        },
        moreLinkText: function(n) {
            return '+ ' + n + ' ' + (n === 1 ? 'daugiau' : 'daugiau');
        },
        
        views: {
            dayGridMonth: {
                dayMaxEventRows: 1,
                dayMaxEvents: 1
            }
        }
    });
    
    calendar.render();
});
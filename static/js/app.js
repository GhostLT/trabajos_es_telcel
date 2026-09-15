// Client side utilities for Trabajos ES Telcel
document.addEventListener("DOMContentLoaded", function() {
    // Automatically convert site input to uppercase
    const siteInputs = document.querySelectorAll("input[name='site'], #exportSiteInput, #siteInput");
    siteInputs.forEach(input => {
        input.addEventListener("input", function() {
            this.value = this.value.toUpperCase();
        });
    });

    // Tooltips initialization
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

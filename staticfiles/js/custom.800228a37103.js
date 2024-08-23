// Handle form navigation
$(document).ready(function() {
    $(".next-section").click(function() {
        var nextTab = $(this).data('next');
        $('#' + nextTab).tab('show');
    });

    $(".previous-section").click(function() {
        var prevTab = $(this).data('previous');
        $('#' + prevTab).tab('show');
    });
});

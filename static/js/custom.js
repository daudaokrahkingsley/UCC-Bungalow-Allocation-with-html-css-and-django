// Handle form navigation
$(document).ready(function(){
    $('.next-section').click(function(){
        var nextTab = $(this).data('next');
        $('#' + nextTab).tab('show');
    });

    $('.previous-section').click(function(){
        var prevTab = $(this).data('previous');
        $('#' + prevTab).tab('show');
    });
});

$(document).ready(function() {
    $("#staff_number").on('input', function() {
        var staff_number = $(this).val();
        if (staff_number) {
            $.ajax({
                url: "{% url 'get_buildings' %}",
                data: {
                    'staff_number': staff_number
                },
                success: function(data) {
                    var preferences = data.preferences;
                    var container = $("#preferences-container");
                    container.empty();  // Clear existing input fields
                    var preferenceCount = 0;

                    if (preferences.length > 0) {
                        container.append('<label for="preferences">Preferences (available rooms: ' + preferences.join(', ') + '):</label>');
                        preferences.forEach(function(pref, index) {
                            container.append('<input type="text" class="preference-input" name="preference_' + preferenceCount + '" placeholder="Enter preference ' + (preferenceCount + 1) + '">');
                            preferenceCount++;
                        });

                        $("#preference_count").val(preferenceCount);  // Update preference count
                    } else {
                        container.append('<p>No buildings available</p>');
                        $("#preference_count").val(0);
                    }
                }
            });
        } else {
            $("#preferences-container").empty();
            $("#preference_count").val(0);
        }
    });
});

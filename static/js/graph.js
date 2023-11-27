$(document).ready(function () {
    $('#analysisGraphGet').on('click', function () {
        console.log($('#startDate').val());
        console.log($('#endDate').val());
        const data = {
            startData: $('#startDate').val(),
            endDate: $('#endDate').val()
        };

        $.ajax({
            type: 'post',
            url: '/rGraphGenerate',
            data: data,
            dataType: 'json',
            success: function (result) {
                if (result.result == 'true') {
                    $('#graphContainer').show();
                }
            }
        });
    });
});
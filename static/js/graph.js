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
                    genGraphUI();
                }
            }
        });
    });
    
    function genGraphUI () {
        $('#graphContainer').html('');
        $('#graphContainer').append(
            '            <div class="row row-cols-1 row-cols-sm-2 g-4">' +
            '                <div class="col d-flex flex-column gap-2">' +
            '                    <h4 class="fw-semibold mb-0 text-body-emphasis">언어별 요청 수</h4>' +
            '                  <img class="bi" src="static/img/language_analysis.png?time=' + Math.floor((new Date()).getTime() / 1000) + '">' +
            '                </div>' +
            '                <div class="col d-flex flex-column gap-2">' +
            '                    <h4 class="fw-semibold mb-0 text-body-emphasis">소스코드 검증 성공/실패</h4>' +
            '                    <img class="bi" src="static/img/result_analysis.png?time=' + Math.floor((new Date()).getTime() / 1000) + '">' +
            '                </div>' +
            '            </div>');
    }
});
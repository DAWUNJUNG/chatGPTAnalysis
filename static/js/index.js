$(document).ready(function () {
    $('#gptRequest').on('click', function () {
        const btnText = $(this).text();
        if (btnText === 'GPT에게 소스코드 물어보기') {
            $('#goGraphPage').hide();
            $('#gptRequestContent').show();
            $('#reloadPageBtn').show();
            $(this).text('GPT에게 질문하기');
        } else if (btnText === 'GPT에게 질문하기') {
            $('#gptRequestContent').hide();
            $('#loadingContainer').show();
            $('#gptRequest').attr('disabled', true);
            gptRequest();
        } else if (btnText === '사용 라이브러리 지정하기') {
            $('#gptResponseContainer').hide();
            $('#libarySetContainer').show();
            $('#gptRequest').text('GPT 소스코드 증명하기');
        } else if (btnText === 'GPT 소스코드 증명하기') {
            $('#libarySetContainer').hide();
            $('#loadingContainer').show();
            $('#gptRequest').attr('disabled', true);
            certification();
        } else if (btnText === '처음으로 돌아가기') {
            location.reload();
        }
    });

    $('#reloadPageBtn').on('click', function () {
        location.reload();
    });

    $('#goGraphPage').on('click', function () {
       location.href = '/graph';
    });

    function gptRequest() {
        const data = {
            language: $('#language').val(),
            content: $('#order-content').val()
        };
        $.ajax({
            type: 'post',
            url: '/gptRequest',
            data: data,
            dataType: 'json',
            success: function (result) {
                $('#gptResponse').val(result.gptMessage)
                    .data('contentId', result.contentId);
                $('#loadingContainer').hide();
                $('#gptResponseContainer').show();
                $('#gptRequest').attr('disabled', false);
                $('#gptRequest').text('사용 라이브러리 지정하기');
            }
        });
    }

    function certification() {
        let installLibs = [];
        $('.need-lib').each(function (index, item) {
            installLibs.push($(item).val());
        });

        const data = {
            libs: JSON.stringify(installLibs),
            contentId: $('#gptResponse').data('contentId')
        }

        $.ajax({
            type: 'post',
            url: '/checkSourceCode',
            data: data,
            dataType: 'json',
            success: function (result) {
                $('#loadingContainer').hide();
                $('#gptRequest').attr('disabled', false);
                $('#reloadPageBtn').hide();
                $('#gptRequest').text('처음으로 돌아가기');
                if (result.result == 'true') {
                    $('#successContainer').show();
                } else {
                    $('#failContainer').show();
                }
            }
        });
    }

    $('#checkSourceBtn').on('click', function () {
       certification();
    });

    $('#moreLibary').on('click', function () {
        $('#libAddPoint').before('<input type="text" class="lib form-control" id="language">');
    });

});
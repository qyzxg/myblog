/**
 * Created by qyzxg on 2017/5/26.
 */
$(document).ready(function () {
    $('#sys_messages_t,#unread_messages_t,#read_messages_t,#sended_messages_t,#stable1,#stable2').dataTable({
        retrieve: true,
        "dom": 'tip',
        language: {
            url: '/static/json/chinese.json'
        },
    });
});

$(document).ready(function () {
    var table = $('#stable').DataTable({
        retrieve: true,
        dom: 'ltip',
        language: {
            url: '/static/json/chinese.json'
        },
    });

    $('#dsearch').on('keyup click', function () {
        var tsval = $("#dsearch").val()
        table.search(tsval, false, false).draw();
    });
});


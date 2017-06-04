/**
 * Created by qyzxg on 2017/5/26.
 */
$(document).ready(function () {
    $('#sys_messages_t,#unread_messages_t,#read_messages_t,#sended_messages_t,#stable1,#stable2').dataTable({
        retrieve: true,
        deferRender: true,
        dom: 'tip',
        language: {
            url: '/static/json/chinese.json'
        },
    });
});

$(document).ready(function () {
    var table = $('#stable').DataTable({
        retrieve: true,
        deferRender: true,
        scrollY: "520px",
        scrollCollapse: true,
        lengthMenu: [[10, 50, 100, 1000, -1], [10, 50, 100, 1000, '所有']],
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


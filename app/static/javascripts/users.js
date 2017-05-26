/**
 * Created by qyzxg on 2017/5/26.
 */
$(document).ready(function () {
    $('#sys_messages_t,#unread_messages_t,#read_messages_t,#sended_messages_t').dataTable({
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
    $("#checkAll").on("click", function () {
        if ($(this).prop("checked") === true) {
            $("input[name='checkList']").prop("checked", $(this).prop("checked"));
            $('#stable tbody tr').addClass('selected');
        } else {
            $("input[name='checkList']").prop("checked", false);
            $('#stable tbody tr').removeClass('selected');
        }
    });

    $('#stable tbody').on('click', 'tr input[name="checkList"]', function () {
        var $tr = $(this).parents('tr');
        if ($(this).prop("checked") === true) {
            $tr.addClass('selected');
        } else {
            $tr.removeClass('selected');
        }
    });
    $('#dsearch').on('keyup click', function () {
        var tsval = $("#dsearch").val()
        table.search(tsval, false, false).draw();
    });
    //显示隐藏列
    var x = 0
    $('.toggle-vis').on('change', function (e) {
        e.preventDefault();
        var column = table.column($(this).attr('data-column'));
        column.visible(x++ % 2 == 1, false);

    });
    var flip = 0;
    $("#hids").click(function () {
        $(".showul").toggle(flip++ % 2 == 0);
    });
});


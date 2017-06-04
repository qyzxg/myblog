/**
 * Created by qyzxg on 2017/5/26.
 */


$(document).ready(function () {
    var table = $('#stable').DataTable({
        retrieve: true,
        dom: 'ltip',
        scrollY: "520px",
        scrollCollapse: true,
        lengthMenu: [[10, 50, 100, 1000,-1 ],[10, 50, 100, 1000,'所有']],
        deferRender: true,
        language: {
            url: '/static/json/chinese.json'
        },
        columnDefs: [
            {
                orderable: false,
                targets: 0
            },
            {
                orderable: false,
                targets: 1
            }],
        order: [
            [0, null]
        ],


    });
    //添加索引列
    table.on('order.dt search.dt',
        function () {
            table.column(0, {
                search: 'applied',
                order: 'applied'
            }).nodes().each(function (cell, i) {
                cell.innerHTML = i + 1;
            });
        }).draw();
    //checkbox全选
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
    //自定义搜索
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


$(document).ready(function () {
    var table1 = $('#msg_t').DataTable({
        retrieve: true,
        deferRender: true,
        scrollY: "520px",
        scrollCollapse: true,
        lengthMenu: [[10, 50, 100, 1000,-1 ],[10, 50, 100, 1000,'所有']],
        dom: 'ltip',
        language: {
            url: '/static/json/chinese.json'
        },

    });
    $('#esearch').on('keyup click', function () {
        var tsval = $("#esearch").val()
        table1.search(tsval, false, false).draw();
    });
});
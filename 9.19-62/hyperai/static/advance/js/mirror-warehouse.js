
//    页码
var page=function (a) {
    $("#page").paging({
        pageNo:1,    //显示页面
        totalPage: a,   //总页数
        totalSize: 300,
        callback: function(num) {

            console.log('---------',num)

            $.ajax({
                type:'POST',
                url:'/sysmanager/load_project',
                data:{'num':num},
                success:function (e) {
                    console.log('-----------',e)

                    $('.mirror-list tr').hide()

                    for (var i = 0;i<e.project_list.length;i++){

                        $('.mirror-list tr').eq(i).show()
                        var year = new Date(e.project_list[i]['create_time']).getFullYear()
                        var month = new Date(e.project_list[i]['create_time']).getMonth()+1
                        var date = new Date(e.project_list[i]['create_time']).getDate()
                        var hour = new Date(e.project_list[i]['create_time']).getHours();
                        var min = new Date(e.project_list[i]['create_time']).getMinutes();
                        var second = new Date(e.project_list[i]['create_time']).getSeconds();
                        if(month < 10){
                            month = '0' + month
                        }
                        if(date <10){
                            date = '0'+date
                        }
                        if(hour < 10){
                            hour = '0' + hour
                        }
                        if(min < 10){
                            min = '0' + min
                        }
                        if(second < 10){
                            second = '0' + second
                        }

                        // $('.clone-box ul').clone().appendTo('.mirror-list')
                        $('.mirror-list tr').eq(i).find('td').eq(1).html(e.project_list[i]['project_name'])
                        $('.mirror-list tr').eq(i).find('td').eq(2).html(e.project_list[i]['access_level'])
                        $('.mirror-list tr').eq(i).find('td').eq(3).html(e.project_list[i]['role_name'])
                        $('.mirror-list tr').eq(i).find('td').eq(4).html(year+'-'+month+'-'+date+' '+hour+':'+min+':'+second)
                        $('.mirror-list tr').eq(i).find('.pid').html(e.project_list[i]['project_id'])


                        if($('.mirror-list tr').eq(i).find('td').eq(2).html() == 'true'){
                            $('.mirror-list tr').eq(i).find('td').eq(2).html('公开')
                        }else if($('.mirror-list tr').eq(i).find('td').eq(2).html() == 'false'){
                            $('.mirror-list tr').eq(i).find('td').eq(2).html("私有")
                        }

                    }
                }
            })

        }
    })
}







<!--数据交互-->
$.ajax({
    type:'GET',
    url:'/sysmanager/load_project',
    success:function (e) {
        console.log('------------',e)
        $('.mirror-list tr').hide()
        for (var i = 0;i<e.project_list.length;i++){

            console.log(e.project_list[i]['project_id'])
            var year = new Date(e.project_list[i]['create_time']).getFullYear()
            var month = new Date(e.project_list[i]['create_time']).getMonth()+1
            var date = new Date(e.project_list[i]['create_time']).getDate()
            var hour = new Date(e.project_list[i]['create_time']).getHours();
            var min = new Date(e.project_list[i]['create_time']).getMinutes();
            var second = new Date(e.project_list[i]['create_time']).getSeconds();
            if(month < 10){
                month = '0' + month
            }
            if(date <10){
                date = '0'+date
            }
            if(hour < 10){
                hour = '0' + hour
            }
            if(min < 10){
                min = '0' + min
            }
            if(second < 10){
                second = '0' + second
            }

            console.log('----',year+'-'+month+'-'+date+' '+hour+':'+min+':'+second)

            // $('.clone-box tr').clone().appendTo('.mirror-list')
            $('#tableid .mirror-list tr').eq(i).show()
            $('.mirror-list tr').eq(i).find('td').eq(1).html(e.project_list[i]['project_name'])
            $('.mirror-list tr').eq(i).find('td').eq(2).html(e.project_list[i]['access_level'])
            $('.mirror-list tr').eq(i).find('td').eq(3).html(e.project_list[i]['role_name'])
            $('.mirror-list tr').eq(i).find('td').eq(4).html(year+'-'+month+'-'+date+' '+hour+':'+min+':'+second)
            $('.mirror-list tr').eq(i).find('.pid').html(e.project_list[i]['project_id'])


            if($('.mirror-list tr').eq(i).find('td').eq(2).html() == 'true'){
                $('.mirror-list tr').eq(i).find('td').eq(2).html('公开')
            }else if($('.mirror-list tr').eq(i).find('td').eq(2).html() == 'false'){
                $('.mirror-list tr').eq(i).find('td').eq(2).html("私有")
            }


        }
        for (var j =0;j<e.user_list.length;j++){
            $('#pj-manage').append("<option value="+e. user_list[j]['name'] +">"+ e.user_list[j]['name']+ "</option>")
        }
        page(e.project_pages)
    }
})


// 新建项目

$('#pjname').focus(function () {
    $(this).parents('.form-group').removeClass('has-error')
    $('.name_tishi').css('display','none')
})



$('#newProject .btn-yes').on('click',function () {

    var pjname = $('#pjname').val()
    var pjaccess = '' +$('#pjaccess').is(":checked")
    var pjmanager = $('#pj-manage').val()
    console.log(pjmanager)
    if(pjname == ''){
        $('#pjname').parents('.form-group').addClass('has-error')
        $('.name_tishi').css('display','inline-block')
        $('.name_tishi').html('项目名称不能为空')
    }

    else{

        $.ajax({
            type:'POST',
            url:'/sysmanager/project_name',
            data:{"project_name":$(this).val()},
            success:function (e) {
                console.log('-----------+++++--',e)
                if (e.res == 1){
                    $('#pjname').parents('.form-group').addClass('has-error')
                    $('.name_tishi').css('display','inline-block')
                    $('.name_tishi').html('该项目已存在')
                    $('.pj-btn-yes').find('input').attr('disabled',true)
                }else{

                    $.ajax({
                        type:'POST',
                        url:'/sysmanager/add_project',
                        data:{"project_name":pjname,"public_value":pjaccess,'name':pjmanager},
                        success:function (e) {
                            $('#newProject').css('display','none')
                            $('.modal-backdrop').hide()
                            console.log('-------------',e)
                            if(e.errmsg == 'ok'){

                                $('.static').show()
                                $('#myAlert').addClass('alert-success').removeClass('alert-warning')
                                $('.static strong').html('创建成功！')

                            }else {
                                $('.static').show()
                                $('#myAlert').addClass('alert-warning').removeClass('alert-success')
                                $('.static strong').html('创建失败！')

                            }
                        }
                    })


                }
            }
        })
    }
})

//关闭提示框
$(".close").click(function(){
    // $(".alert").alert('close');
    $('.static').css('display','none')
    $('.modal-backdrop').hide()
});


//项目跳转详情页
$('.mirror-list').on('click','.project_name',function () {

    localStorage.setItem('project_id',$(this).parents('tr').find('.pid').html())
    window.location.href ='/sysmanager/img_details'
})


//删除项目
var project_id = []
$('.delete-icon').on('click',function () {
    project_id = []

    $('.mirror-list .check_each').each(function () {
        if($(this).is(':checked') == true){
            project_id.push($(this).parents('td').siblings('.pid').html())
            console.log('--------------',$(this).parents('td').siblings('.pid').html())
        }

    })
    console.log('--------------',project_id)

})

$('#deleteProject .btn-yes').on('click',function () {
    console.log('--------------',project_id)
    $.ajax({
        type:"POST",
        url:"/sysmanager/delete_project",
        data:{"project_id":project_id},
        success:function (e) {
            console.log('delete-project',e)
            if(e.errmsg == 'ok'){
                $('.mirror-list .pid').each(function () {
                    for(var i = 0; i<e.project_id.length;i++){
                        if($(this).html() == e.project_id[i]){
                            $(this).parents('ul').remove()
                        }
                    }

                })
                $('.delete-icon').css('visibility','hidden')
                // $('.tishi-box').css('display','block')
                // $('.tishi-box .alert-div-content h3').html('成功！')
            }else{
                $('.static').show()
                $('#myAlert').addClass('alert-warning').removeClass('alert-success')
                $('.static strong').html('删除失败！')
            }

        }
    })
    $('#deleteProject').css('display','none')
    $('.modal-backdrop').hide()

})





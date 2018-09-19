$('.title-btn').on('click','.s-btn',function(){
	$(this).addClass('s-bdr').siblings().removeClass('s-bdr')
	if($(this).html() == '用户'){
        // $('.user-all-box').show()
//		$('.wait-box').show()
//		$('.depart-box').hide()
//		$('.user-box').hide()
//		$('.create-user').show();
//		$('.create-depart').hide()
	}else{
		$('.depart-box').show()
		$('.wait-box').hide()
		$('.user-box').hide()
        $('.user-all-box').hide()
		$('.create-depart').show();
		$('.create-user').hide()
	}
})

$('.wait-user').on('click',function(){
    $('.user-all-box').show()
	$('.wait-box').show()
	$('.user-box').hide()
	$('.depart-box').hide()
    $('.create-user').show();
    $('.create-depart').hide()
})
$('.pass-user').on('click',function(){
    $('.user-all-box').show()
	$('.user-box').show()
	$('.wait-box').hide()
	$('.depart-box').hide()
    $('.create-user').show();
    $('.create-depart').hide()
})



var gpu_pattern = /^\+?[1-9][0-9]*$/;
var pattern1 = /^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$/
var pattern2 = /^[1][3,4,5,7,8][0-9]{9}$/;
var pattern3 = /^[a-zA-Z][a-zA-Z0-9_]{5,16}$/;

var page1=function (a) {
    $("#page1").paging({
        pageNo:1,    //显示页面
        totalPage: a,   //总页数
        totalSize: 300,
        callback: function(num) {

            console.log('---------',num)

            $.ajax({
                type:'POST',
                url:'/user_manage_load',
                data:{'num':num},
                success:function (e) {
                    console.log('-----------',e)

                    $('.user_all_select tr').hide()
                    for(var i=0;i<e.no_examined_user.length;i++){
                        console.log(i)
                        $('.user_all_select tr').eq(i).show()
                        // $('.clone_box .user-select-i').clone().appendTo($('.user_all_select'))
                        $('.user_all_select tr').eq(i).children().eq(0).html(e.no_examined_user[i]['name'])
                        $('.user_all_select tr').eq(i).children().eq(1).html(e.no_examined_user[i]['department'])
                        $('.user_all_select tr').eq(i).children().eq(3).html(e.no_examined_user[i]['id'])
                    }
                }
            })

        }
    })
}

var page2=function (a) {
    $("#page2").paging({
        pageNo:1,    //显示页面
        totalPage: a,   //总页数
        totalSize: 300,
        callback: function(num) {

            console.log('---------',num)

            $.ajax({
                type:'POST',
                url:'/user_manage_load',
                data:{'num':num},
                success:function (e) {
                    console.log('-----------',e)

                    $('.user_all tr').hide()
                    for(var i=0;i<e.examined_user.length;i++){
                        // $('.clone_box .user-i').clone().appendTo($('.user_all'))
                        $('.user_all tr').eq(i).show()
                        $('.user_all tr').eq(i).children().eq(1).html(e.examined_user[i]['name'])
                        $('.user_all tr').eq(i).children().eq(2).html(e.examined_user[i]['department'])
                        $('.user_all tr').eq(i).children().eq(3).html(e.examined_user[i]['email'])
                        $('.user_all tr').eq(i).children().eq(4).html(e.examined_user[i]['phone'])
                        $('.user_all tr').eq(i).children().eq(6).html(e.examined_user[i]['id'])
                    }
                }
            })

        }
    })
}

var page=function (a) {
    $("#page").paging({
        pageNo:1,    //显示页面
        totalPage: a,   //总页数
        totalSize: 300,
        callback: function(num) {

            console.log('---------',num)

            $.ajax({
                type:'POST',
                url:'/user_manage_load',
                data:{'num':num},
                success:function (e) {
                    console.log('-----------',e)

                    $('.depart_list tr').hide()
                    for(var i = 0; i< e.department_list.length;i++){
                        $('.depart_list tr').eq(i).show()
                        // $('.clone_box .depart-detail').clone().appendTo($('.depart_list'))
                        $('.depart_list tr').eq(i).children().eq(0).html(e.department_list[i]['name'])
                        $('.depart_list tr').eq(i).children().eq(1).find('span').html( e.department_list[i]['gpu'] )
                        $('.depart_list tr').eq(i).children().eq(2).html(e.department_list[i]['power'])
                        $('.depart_list tr').eq(i).children().eq(4).html( e.department_list[i]['id'] )

                        $('#select2').append('<option value="' + e.department_list[i]['name'] + '">' + e.department_list[i]['name'] + '</option>');
                        $('#select3').append('<option value="' + e.department_list[i]['name'] + '">' + e.department_list[i]['name'] + '</option>')
                    }
                }
            })

        }
    })
}


//    交互加载
$.get('/user_manage_load',function (e) {
//        已经完成的账户
    console.log(e)
    $('.user_all tr').hide()
    for(var i=0;i<e.examined_user.length;i++){
        // $('.clone_box .user-i').clone().appendTo($('.user_all'))
        $('.user_all tr').eq(i).show()
        $('.user_all tr').eq(i).children().eq(1).html(e.examined_user[i]['name'])
        $('.user_all tr').eq(i).children().eq(2).html(e.examined_user[i]['department'])
        $('.user_all tr').eq(i).children().eq(3).html(e.examined_user[i]['email'])
        $('.user_all tr').eq(i).children().eq(4).html(e.examined_user[i]['phone'])
        $('.user_all tr').eq(i).children().eq(6).html(e.examined_user[i]['id'])
    }
    page2(e.examined_pages)
//        账户审批
    $('.user_all_select tr').hide()
    for(var i=0;i<e.no_examined_user.length;i++){
        console.log(i)
        $('.user_all_select tr').eq(i).show()
        // $('.clone_box .user-select-i').clone().appendTo($('.user_all_select'))
        $('.user_all_select tr').eq(i).children().eq(0).html(e.no_examined_user[i]['name'])
        $('.user_all_select tr').eq(i).children().eq(1).html(e.no_examined_user[i]['department'])
        $('.user_all_select tr').eq(i).children().eq(3).html(e.no_examined_user[i]['id'])
    }
    page1(e.no_examined_pages)
})

//    部门交互
$.get('/department_load',function (e) {
    console.log('depart',e)
    $('#u-depart').children().remove();
    $('#u-olddepart').children().remove();
    $('.depart_list tr').hide()
    for(var i = 0; i< e.department_list.length;i++){
        $('.depart_list tr').eq(i).show()
        // $('.clone_box .depart-detail').clone().appendTo($('.depart_list'))
        $('.depart_list tr').eq(i).children().eq(0).html(e.department_list[i]['name'])
        $('.depart_list tr').eq(i).children().eq(1).find('span').html( e.department_list[i]['gpu'] )
        $('.depart_list tr').eq(i).children().eq(2).html(e.department_list[i]['power'])
        $('.depart_list tr').eq(i).children().eq(4).html( e.department_list[i]['id'] )

        $('#u-depart').append('<option value="' + e.department_list[i]['name'] + '">' + e.department_list[i]['name'] + '</option>');
        $('#u-olddepart').append('<option value="' + e.department_list[i]['name'] + '">' + e.department_list[i]['name'] + '</option>')
    }
    page(e.department_page)

})

//	通过
var examined_id = null
$('.user_all_select').on('click','.user_alert_btn_yer',function () {
    examined_id = $(this).parents('td').next('.pid').html()
    console.log('yes',examined_id)
    // $('.alert-box-user .user_alert_content').html('确认通过？')
    // $(".alert-box-user").css('display','block')
    // $('.alert-box-user .user-btn-no').on('click',function () {
    //     $(".alert-box-user").css('display','none')
    // })
    // $('.alert-box-user .user-btn-yes').on('click',function () {
    $.ajax({
        type:'POST',
        url:"/user_examined",
        data:{'user_id':examined_id},
        success:function (data) {
            console.log('审核',data)
            if(data.errmsg == 'ok'){



                $('.user_all_select .pid').each(function () {


                    if($(this).html() == data.id){
                        console.log('pppp')
                        $(this).parents('td').prev('td').html('通过审核')
                    }
                })
            }
        }
    })
//        $(".alert-box-user").css('display','none')
//             })
})
<!--驳回-->
$('.user_all_select').on('click','.user_alert_btn_no',function () {

    examined_id = $(this).parents('td').next('.pid').html()

    $('#unUser .btn-yes').on('click',function () {
        $.ajax({
            type:'POST',
            url:"/user_noexamined",
            data:{'user_id':examined_id},
            success:function (data) {
                console.log('待审核',data.errmsg)
                if(data.errmsg == 'ok'){
                    console.log('11111')
                    $("#unUser").hide()
                    $('.modal-backdrop').hide()
                    $('.user_all_select .pid').each(function () {

                        if($(this).html() == data.id){
                            console.log('pppp')
                            $(this).parents('td').prev('td').html('未通过审核')
                        }
                    })
                }
            }
        })
//        $(".alert-box-user").css('display','none')
    })
})


//	添加用户
$('.create-user').on('click',function () {
    $('#user-name').val('')
    $('#user-email').val('')
    $('#user-phone').val('')

})


$('#user-name').blur(function () {
    if(!pattern3.test($(this).val())){
        $(this).parents('.form-group').addClass('has-error')
        $(this).prev('.name_tishi').html('字母开头6-16位字母、数字、下划线')
        $(this).prev('.name_tishi').show()
    }else{
        console.log('==',$(this).val())
        $.post('/user/name',{'name':$(this).val()},function(e){
            console.log('----',e.res)
            if(e.res==1){

                $('#user-name').parents('.form-group').addClass('has-error')
                $('#user-name').prev('.name_tishi').html('该用户已存在')
                $('#user-name').prev('.name_tishi').show()
                console.log('--dd--',$('#user-name'))
            }
            else if(e.res==0){

            }

        },'json')
    }
})
$('#user-name').focus(function () {
    $(this).parents('.form-group').removeClass('has-error')
    $(this).prev('.name_tishi').hide()
})
$('#user-email').focus(function () {
    $(this).parents('.form-group').removeClass('has-error')
    $(this).prev('.name_tishi').hide()
})
$('#user-phone').focus(function () {
    $(this).parents('.form-group').removeClass('has-error')
    $(this).prev('.name_tishi').hide()
})



$('#myModal .btn-yes').on('click',function () {
    var user_name = $('#user-name').val()
    var user_depart = $('#u-depart').val()
    var user_email = $('#user-email').val()
    var user_phone = $('#user-phone').val()

    if(!pattern1.test(user_email)){
        $('#user-email').parents('.form-group').addClass('has-error')
        $('#user-email').prev('.name_tishi').html('邮箱格式不正确！')
        $('#user-email').prev('.name_tishi').css('display','block')

    }else if(!pattern2.test(user_phone)){
        $('#user-phone').parents('.form-group').addClass('has-error')
        $('#user-phone').prev('.name_tishi').html('手机号格式不正确！')
        $('#user-phone').prev('.name_tishi').css('display','block')
    }
    else{

        $.ajax({
            type:'POST',
            url:'/user_add',
            data:{'user_name':user_name,'user_depart':user_depart,'user_email':user_email,'user_phone':user_phone},
            success:function (data) {

                if(data.errmsg == 'ok'){
                    console.log(data.errmsg)

                    $('#myModal').hide()
                    $('.modal-backdrop').hide()

                    $.get('/user_manage_load',function (e) {
//        已经完成的账户
                        console.log(e)
                        $('.user_all tr').hide()
                        for(var i=0;i<e.examined_user.length;i++){
                            // $('.clone_box .user-i').clone().appendTo($('.user_all'))
                            $('.user_all tr').eq(i).show()
                            $('.user_all tr').eq(i).children().eq(1).html(e.examined_user[i]['name'])
                            $('.user_all tr').eq(i).children().eq(2).html(e.examined_user[i]['department'])
                            $('.user_all tr').eq(i).children().eq(3).html(e.examined_user[i]['email'])
                            $('.user_all tr').eq(i).children().eq(4).html(e.examined_user[i]['phone'])
                            $('.user_all tr').eq(i).children().eq(6).html(e.examined_user[i]['id'])
                        }
                        page2(e.examined_pages)
                    })


                }else{
                    $('#myModal').hide()
                    $('.modal-backdrop').hide()
                    $('.static').show()
                    $('#myAlert').addClass('alert-warning').removeClass('alert-success')
                    $('.static strong').html('用户添加失败！')
                }
            }
        })
    }

})





//  用户删除

var user_id = []
$('.delete-icon').on('click',function () {
    user_id = []

    $('.check_each').each(function () {
        if($(this).is(':checked') == true){
            user_id.push($(this).parents('td').siblings('.pid').html())

        }

    })
    console.log(user_id)

})
$('#deleteUser .btn-yes').on('click',function () {
    console.log('job_id',user_id)
    $.ajax({
        type:'POST',
        url:'/user_delete',
        data:{'user_id':user_id},
        success:function (e) {
            console.log('delete',e)
            if(!e.errmsg =='ok'){
                $('#deleteUser').hide()
                $('.modal-backdrop').hide()
                $('.static').show()
                $('#myAlert').addClass('alert-warning').removeClass('alert-success')
                $('.static strong').html('该用户不能删除！')

            }
            else{
                $('#deleteUser').hide()
                $('.modal-backdrop').hide()
                $('.check_each').each(function () {
                    if($(this).is(':checked') == true){
                        $(this).parents('tr').remove()
                        $('.delete-icon').css('visibility','hidden')
                    }

                })
//                    location.reload()
            }
        }
    })

})
//	用户编辑

var users_id = null
$('.user_all').on('click','.user-edit',function () {


    var usernames = $(this).parents('tr').find('td').eq(1).html();
    var userdeparts = $(this).parents('tr').find('td').eq(2).html();
    var useremail = $(this).parents('tr').find('td').eq(3).html();
    var userphone = $(this).parents('tr').find('td').eq(4).html();
    users_id = $(this).parents('tr').find('.pid').html();
    $('#user-oldname').html(usernames)
    $('#u-olddepart').find("option[value=" +userdeparts+"]").attr('selected',true)
    $('#user-oldemail').val(useremail)
    $('#user-oldphone').val(userphone)


})

$('#user-oldemail').focus(function () {
    $('#user-oldemail').parents('.form-group').removeClass('has-error')
    $('#user-oldemail').prev('.name_tishi').hide()
})

$('#user-oldphone').focus(function () {
    $('#user-oldphone').parents('.form-group').removeClass('has-error')
    $('#user-oldphone').prev('.name_tishi').hide()
})

$('#editorUser .btn-yes').on('click',function () {

    if(!pattern1.test($('#user-oldemail').val())){
        $('#user-oldemail').parents('.form-group').addClass('has-error')
        $('#user-oldemail').prev('.name_tishi').show()
        $('#user-oldemail').prev('.name_tishi').html('邮箱格式不正确！')


    }else if(!pattern2.test($('#user-oldphone').val())){
        $('#user-oldphone').parents('.form-group').addClass('has-error')
        $('#user-oldphone').prev('.name_tishi').show()
        $('#user-oldphone').prev('.name_tishi').html('手机号格式不正确！')

    }else {

        $.ajax({
            type: 'POST',
            url: '/user_update',
            data: {
                'depart_name': $('#u-olddepart').val(),
                'user_id': users_id,
                'phone': $('#user-oldphone').val(),
                'email': $('#user-oldemail').val()
            },
            success: function (data) {
                console.log(data)
                if (data.errmsg == 'ok') {
                    $('#editorUser').hide()
                    $('.modal-backdrop').hide()
                    $('.user_all .pid').each(function () {
                        if($(this).html() == data.user_id){
                            $(this).parents('tr').find('td').eq(2).html($('#u-olddepart').val())
                            $(this).parents('tr').find('td').eq(3).html($('#user-oldemail').val())
                            $(this).parents('tr').find('td').eq(4).html($('#user-oldphone').val())
                        }
                    })
                }
            }
        })
    }

})


//	新建部门

$('.create-depart').on('click',function () {
    $('#depart-name').val('');
    $('#gpu-max').val('')
})

$('#gpu-max').focus(function () {
    $(this).parents('.form-group').removeClass('has-error')
    $(this).prev('.name_tishi').hide()
})
$('#depart-name').focus(function () {
    $(this).parents('.form-group').removeClass('has-error')
    $(this).prev('.name_tishi').hide()
})
$('#depart-name').blur(function () {

    $.post('/department_name',{'name':$(this).val()},function(e){
        console.log('-----',e)
        if(e.res==1){
            $('#depart-name').parents('.form-group').addClass('has-error')
            $('#depart-name').prev('.name_tishi').show()
            $('#depart-name').prev('.name_tishi').html('该部门已存在！')
        }
        else if(e.res==0){

        }
        console.log(e.res)
    },'json')
//        }
})





$('#myDepart .btn-yes').on('click',function () {
    var depart_name = $('#depart-name').val()
    var depart_gpu = $('#gpu-max').val()
    var priority = $('#depart-priority').val()

    var total_gpu = null;


//        获取系统总gpu
    $.ajax({
        type:'GET',
        url:'/get_gpu_number',
        success:function (e) {
            console.log('gpu',e.total_gpu_count)
            total_gpu = e.total_gpu_count

            console.log('total_gpu',total_gpu)

            if (depart_gpu > total_gpu) {
                $('#gpu-max').parents('.form-group').addClass('has-error')
                $('#gpu-max').prev('.name_tishi').show()
                $('#gpu-max').prev('.name_tishi').html('不能超过系统总GPU ' + total_gpu)

            }

            else if(!gpu_pattern.test(depart_gpu)){
                $('#gpu-max').parents('.form-group').addClass('has-error')
                $('#gpu-max').prev('.name_tishi').show()
                $('#gpu-max').prev('.name_tishi').html('GPU数为整数')
            }
            else {

                $.ajax({
                    type: 'POST',
                    url: '/department_add',
                    data: {'depart_name': depart_name, 'depart_gpu': depart_gpu, 'priority': priority},
                    success: function (data) {
                        console.log('make depart', data)
                        if (data.errmsg == 'ok') {
                            $('#myDepart').hide()
                            $('.modal-backdrop').hide()
                            $.get('/department_load',function (e) {


                                $('#u-depart').children().remove();
                                $('#u-olddepart').children().remove();
                                $('.depart_list tr').hide()
                                for(var i = 0; i< e.department_list.length;i++){
                                    $('.depart_list tr').eq(i).show()
                                    // $('.clone_box .depart-detail').clone().appendTo($('.depart_list'))
                                    $('.depart_list tr').eq(i).children().eq(0).html(e.department_list[i]['name'])
                                    $('.depart_list tr').eq(i).children().eq(1).find('span').html( e.department_list[i]['gpu'] )
                                    $('.depart_list tr').eq(i).children().eq(2).html(e.department_list[i]['power'])
                                    $('.depart_list tr').eq(i).children().eq(4).html( e.department_list[i]['id'] )

                                    $('#u-depart').append('<option value="' + e.department_list[i]['name'] + '">' + e.department_list[i]['name'] + '</option>');
                                    $('#u-olddepart').append('<option value="' + e.department_list[i]['name'] + '">' + e.department_list[i]['name'] + '</option>')
                                }
                                page(e.department_page)

                            })
                        }else{

                            $('#myModal').hide()
                            $('.modal-backdrop').hide()
                            $('.static').show()
                            $('#myAlert').addClass('alert-warning').removeClass('alert-success')
                            $('.static strong').html('部门添加失败！')

                            // $('.depart').css('display', 'none')
                            // $('.success-box').css('display', 'block')
                            // $('.success-box .alert-div-content').find('h3').html('部门添加失败')
                        }
                    }
                })
            }
        }
    })
})
//	删除部门
var depart_id = null;
$('.depart_list').on('click','.depart-delete',function () {

    depart_id = $(this).parents('td').next('.pid').html()
    console.log(depart_id)
})

$('#deleteDepart .btn-yes').on('click',function () {
    $.ajax({
        type:'POST',
        url:'/department_delete',
        data:{'id':depart_id},
        success:function (e) {
            console.log('delete-depart',e)
            if(e.errmsg == 'ok'){
                $('#deleteDepart').hide()
                $('.modal-backdrop').hide()


                $('.depart_list .pid').each(function () {
                    if($(this).html() == e.department_id){
                        $(this).parents('tr').remove()
                    }
                })

                $.get('/department_load',function (e) {

                    $('#u-depart').children().remove();
                    $('#u-olddepart').children().remove();
                    for(var i = 0; i< e.department_list.length;i++){

                        $('#u-depart').append('<option value="' + e.department_list[i]['name'] + '">' + e.department_list[i]['name'] + '</option>');
                        $('#u-olddepart').append('<option value="' + e.department_list[i]['name'] + '">' + e.department_list[i]['name'] + '</option>')
                    }
                })
            }else{

                $('#deleteDepart').hide()
                $('.modal-backdrop').hide()
                $('.static').show()
                $('#myAlert').addClass('alert-warning').removeClass('alert-success')
                $('.static strong').html(e.errmsg)

            }
        }
    })

})


//	编辑部门
var deparid = null
$('.depart_list').on('click','.depart-edit',function () {
    $('#depart-oldname').html($(this).parents('tr').find('td').eq(0).html())
    $('#oldgpu-max').val($(this).parents('tr').find('td').eq(1).find('span').html())
    var editor_priority = $(this).parents('tr').find('td').eq(2).html()
    $('#depart-oldpriority').find("option[value=" + editor_priority +"]").attr('selected',true)

    departid = $(this).parents('tr').next('.pid').html()

})

$('#oldgpu-max').focus(function () {
    $(this).parents('.form-group').removeClass('has-error')
    $(this).prev('.name_tishi').hide()
})

$('#editorDepart .btn-yes').on('click',function () {
    var quota = $('#oldgpu-max').val()
    var priority = $('#depart-oldpriority').val()

    $.ajax({
        type: 'GET',
        url: '/get_gpu_number',
        success: function (e) {
            console.log('gpu', e.total_gpu_count)

            if (quota > e.total_gpu_count) {
                $('#oldgpu-max').parents('.form-group').addClass('has-error')
                $('#oldgpu-max').prev('.name_tishi').show()
                $('#oldgpu-max').prev('.name_tishi').html('不能超过系统总GPU ' + total_gpu)
            } else if (!gpu_pattern.test(quota)) {
                $('#oldgpu-max').parents('.form-group').addClass('has-error')
                $('#oldgpu-max').prev('.name_tishi').show()
                $('#oldgpu-max').prev('.name_tishi').html('GPU数为整数')

            }
            else {
                $.ajax({
                    type: 'POST',
                    url: '/department_update',
                    data: {'gpu': quota, 'id': departid, 'priority': priority},
                    success: function (e) {
                        console.log('e', e)
                        if (e.errmsg == 'ok') {
                            $('#editorDepart').hide()
                            $('.modal-backdrop').hide()
                            $('.depart_list .pid').each(function () {


                                if ($(this).html() == e.depart_id) {
                                    $(this).parents('tr').find('td').eq(2).html($('#depart-oldpriority').val())
                                    $(this).parents('tr').find('td').eq(1).find('span').html($('#oldgpu-max').val())
                                }
                            })
                        } else {

                            $('#editorDepart').hide()
                            $('.modal-backdrop').hide()
                            $('.static').show()
                            $('#myAlert').addClass('alert-warning').removeClass('alert-success')
                            $('.static strong').html('部门修改失败！')

                        }
                    }
                })
            }


        }
    })

})





//关闭提示框
$(".close").click(function(){
    // $(".alert").alert('close');
    $('.static').css('display','none')
    $('.modal-backdrop').hide()
});


//   部门详情跳转
$('.depart-box').on('click','.departname',function () {
    localStorage.clear()
    var department_id = $(this).parents('tr').find('.pid').html()
    localStorage.setItem('depart_id',department_id)

    window.location.href='/department_details'

})


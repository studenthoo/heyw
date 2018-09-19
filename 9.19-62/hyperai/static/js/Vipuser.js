$(".tab-btn1").on("click",function(){
	$(".form1").show();
	$(".form2").hide();
	$(this).addClass("tab-color").siblings().removeClass("tab-color")
})
$(".tab-btn2").on("click",function(){
	$(".form2").show();
	$(".form1").hide();
	$(this).addClass("tab-color").siblings().removeClass("tab-color")
})
$(".form2 .framework").on("click",".standard",function () {
	$(this).addClass("standard-color").siblings(".standard").removeClass("standard-color")
})

$('.form1 .img-btn').on('click', function() {
    $(this).addClass('img-c').siblings().removeClass('img-c')
    if($('.img-c').html() == '共享镜像'){
        $('.form1.public-img').show()
        $('.form1 .private-img').hide()
    }else{
        $('.form1 .private-img').show()
        $('.form1 .public-img').hide()
    }
})
$('.form2 .img-btn').on('click', function() {
    $(this).addClass('img-c').siblings().removeClass('img-c')
    if($('.img-c').html() == '共享镜像'){
        $('.form2 .public-img').show()
        $('.form2 .private-img').hide()
    }else{
        $('.form2 .private-img').show()
        $('.form2 .public-img').hide()
    }
})


$('.img-list').on('click', '.btn-span', function() {
    $(this).find('i').css('transform','rotate(0deg)')
    $(this).parents('.img-con-t').next('.img-detail-box').toggle()
    if ($(this).parents('.img-con-t').next('.img-detail-box').is(':hidden')) {
        $(this).find('i').css('transform','rotate(-90deg)')
        console.log('-----hide---')
        $(this).parents('.public-img-list').next('.public-img-list').find('.img-con-t').removeClass('bdr-t')
    } else{
        $(this).parents('.public-img-list').next('.public-img-list').find('.img-con-t').addClass('bdr-t')
    }
})

$('.home-btn-box').on('click','span',function(){
    $(this).addClass('tab-color').siblings().removeClass('tab-color')

    if($(this).html() == '单机任务'){
        $('.form1').show()
        $('.form2').hide()
    }else{
        $('.form2').show()
        $('.form1').hide()
    }
})
$('.form1 .model-check').on('click',function () {
    console.log($(this).is(':checked'))
    if($(this).is(':checked') == true){
        // $('.form1 #c-box1').css('height','570px')
        $(this).parent('.ct-box').next('.gt-box').css('display','block')
    }
    if($(this).is(':checked') == false){
        // $('.form1 #c-box1').css('height','420px')
        $(this).parent('.ct-box').next('.gt-box').css('display','none')
    }
})
$('.form2 .model-check').on('click',function () {
    console.log($(this).is(':checked'))
    if($(this).is(':checked') == true){
        // $('.form1 #c-box1').css('height','570px')
        $(this).parent('.ct-box').next('.gt-box').css('display','block')
    }
    if($(this).is(':checked') == false){
        // $('.form1 #c-box1').css('height','420px')
        $(this).parent('.ct-box').next('.gt-box').css('display','none')
    }
})









// console.log('-------change-----')
// $('.form1 .select_version').children().remove();
// $('.form1 .select_framework').on('change', function () {
//
//     console.log('-------form1 change------')
//     var sel_value = $(this).val()
//     var frame_obj2
//
//     $('.form1 .select_version').children().remove();
//
//     $.post('/vip/frame_select', {'frame_obj': ''}, function (e) {
//
//         frame_obj2 = Object.keys(e.single_frame)
//         for (var f = 0; f < frame_obj2.length; f++) {
//             if (sel_value == frame_obj2[f]) {
//                 for (var m = 0, len = e.single_frame[frame_obj2[f]].length; m < len; m++) {
//                     $('.form1 .select_version').append('<option value="' + e.single_frame[frame_obj2[f]][m] + '">' + e.single_frame[frame_obj2[f]][m] + '</option>')
//                 }
//             }
//         }
//     })
//     if($('.form1 .select_framework').val() == 'caffe'){
//         $('.other-frame').css('display','none')
//         $('.caffe-load').show()
//     }else{
//         $('.other-frame').css('display','block')
//         $('.caffe-load').hide()
//     }
//
// })
//
//
//
// $('.form2 .select_version').children().remove();
// $('.form2 .select_framework').on('change', function () {
//
//     var sel_value = $(this).val()
//     var frame_obj2
//
//     $('.form2 .select_version').children().remove();
//
//     $.post('/vip/frame_select', {'frame_obj': ''}, function (e) {
//
//         frame_obj2 = Object.keys(e.distributed_frame)
//         for (var f = 0; f < frame_obj2.length; f++) {
//             if (sel_value == frame_obj2[f]) {
//                 for (var m = 0, len = e.distributed_frame[frame_obj2[f]].length; m < len; m++) {
//                     $('.form2 .select_version').append('<option value="' + e.distributed_frame[frame_obj2[f]][m] + '">' + e.distributed_frame[frame_obj2[f]][m] + '</option>')
//                 }
//             }
//         }
//     })
//     if($('.form2 .select_framework').val() == 'caffempi'){
//         $('.other-frame').css('display','none')
//         $('.caffempi-load').show()
//     }else{
//         $('.other-frame').css('display','block')
//         $('.caffempi-load').hide()
//     }
//
// })




$(".sub-btn").on('click',function(){
    var tab = $('.tab-color').html();
    if (tab === '单机任务') {
        var nodes = 1;
        var tabs = 0
        var gpu = $(this).parents('form').find('#gpu_count').val();
        var cpu = $(this).parents('form').find('#cpu_count').val()
    } else{
        var nodes = $(this).parents('form').find('#node_count').val();
        var tabs = 1
        var gpu = $(this).parents('form').find('#gpu_count_more').val();
        var cpu = $(this).parents('form').find('#cpu_count_more').val()
    }

    var para_obj ={'ismore':tabs,'node_count':nodes,'gpu_count':gpu,'cpu_count':cpu}
    $.ajax({
        url:'/vip/check_res',
        method:'GET',
        data:para_obj,
        success:function(e){
            console.log(e.a)
            if (e.a == 0) {
                $('.alert-box').css('display','block')
                $('.alert-div-content').find('h3').html(e.res)
                $('.alert-box .alert-btn-yes').on('click',function () {
                    $('.alert-box').css('display','none')
                })
//                    alert(e.res);
                return false;
            } else if(e.a == 1){
                // console.log("xxx")

                if (tab === '单机任务') {
                    console.log($('form1'))
                    $('.form1').submit()
                } else{
                    console.log('form2',$('form2'))
                    $('.form2').submit()
                }
                // $('form').submit();
            }
        }
    })


})



























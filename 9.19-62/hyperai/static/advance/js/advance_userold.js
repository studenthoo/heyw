//单机，分布式表单切换
$('.home-btn-box').on('click', 'span', function() {
	$(this).addClass('tab-color').siblings().removeClass('tab-color')

	if($(this).html() == '单机任务') {
		$('.form1').show()
		$('.form2').hide()
        if($('.form1 .select_framework').val() == 'caffe'){
            $('.form1 .other-frame').css('display','none')
            $('.form1 .caffe-load').show()
        }else{
            $('.form1 .other-frame').css('display','block')
            $('.form1 .caffe-load').hide()
        }
	} else {
		$('.form2').show()
		$('.form1').hide()
        if($('.form2 .select_framework').val() == 'caffempi'){
            $('.form2 .other-frame').css('display','none')
            $('.form2 .caffe-load').show()
        }else{
            $('.form2 .other-frame').css('display','block')
            $('.form2 .caffe-load').hide()
        }
	}
})

// 镜像切换

$('.form1 .title-btn').on('click', 'span', function() {
	$(this).addClass('s-bdr').siblings().removeClass('s-bdr')
	if($(this).html() == '共享镜像') {
		$('.form1 .public-img').show()
		$('.form1 .private-img').hide()
	} else {
		$('.form1 .private-img').show()
		$('.form1 .public-img').hide()
	}
})
$('.form2 .title-btn').on('click', 'span', function() {
	$(this).addClass('s-bdr').siblings().removeClass('s-bdr')
	if($(this).html() == '共享镜像') {
		$('.form2 .public-img').show()
		$('.form2 .private-img').hide()
	} else {
		$('.form2 .private-img').show()
		$('.form2 .public-img').hide()
	}
})

//高级选项
$('.form1 .model-check').on('click', function() {
	console.log($(this).is(':checked'))
	if($(this).is(':checked') == true) {
		console.log('-----')
		// $('.form1 #c-box1').css('height','570px')
		$(this).parents('.c-box').next('.c-box').css('display', 'block')
	}
	if($(this).is(':checked') == false) {
		// $('.form1 #c-box1').css('height','420px')
		$(this).parents('.c-box').next('.c-box').css('display', 'none')
	}
})
$('.form2 .model-check').on('click', function() {
	console.log($(this).is(':checked'))
	if($(this).is(':checked') == true) {
		// $('.form1 #c-box1').css('height','570px')
		$(this).parents('.c-box').next('.c-box').css('display', 'block')
	}
	if($(this).is(':checked') == false) {
		// $('.form1 #c-box1').css('height','420px')
		$(this).parents('.c-box').next('.c-box').css('display', 'none')
	}
})


//上传文件
$('#image_list1').on('change',function (e) {

    var file_num = $(this)[0].files.length;

    if(file_num == 1){
        $('.image_list_i_1').val(e.currentTarget.files[0].name)
    }else{
        $('.image_list_i_1').val(file_num + '个文件')

    }

})
$('#image_list2').on('change',function (e) {
    var file_num = $(this)[0].files.length;
    if(file_num == 1){
        $('.image_list_i_2').val(e.currentTarget.files[0].name)
    }else{
        $('.image_list_i_2').val(file_num + '个文件')
    }
})





var frame_arry1,frame_arry2,public_img1,public_img2,private_img1,private_img2
console.log('=======')

$('.form1 .select_framework').children().remove();
$('.form2 .select_framework').children().remove();
console.log('------------')
$.post('/vip/frame_select', {'frame_obj': ''}, function (e) {
    console.log('single--------d',e)
    frame_arry1 = e.single_frame[2]['image']
    frame_arry2 = e.distributed_frame[2]['image']
    public_img1 = e.single_frame[0]['share_value']
    public_img2 = e.distributed_frame[0]['share_value']
    private_img1 = e.single_frame[1]['private_value']
    private_img2 = e.distributed_frame[1]['private_value']
    // console.log(private_img2[frame_arry2[0]])
    //单机任务
    for (var j = 0; j < frame_arry1.length; j++) {
        $('.form1 .select_framework').append('<option value="' + frame_arry1[j] + '">' + frame_arry1[j] + '</option>')
    }
    if(public_img1 == undefined || public_img1[frame_arry1[0]] == undefined){

    }else{
        for (var i = 0, len = public_img1[frame_arry1[0]].length; i < len; i++) {

            var year = new Date(public_img1[frame_arry1[0]][i][2]).getFullYear()
            var month = new Date(public_img1[frame_arry1[0]][i][2]).getMonth()+1
            var date = new Date(public_img1[frame_arry1[0]][i][2]).getDate()
            var hour = new Date(public_img1[frame_arry1[0]][i][2]).getHours();
            var min = new Date(public_img1[frame_arry1[0]][i][2]).getMinutes();
            var second = new Date(public_img1[frame_arry1[0]][i][2]).getSeconds();
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


            $('.clone-box .img-detail').clone().appendTo($('.form1 .public-img-list'))
            $('.form1 .public-img-list .img-detail').eq(i).find('.share_name').html(public_img1[frame_arry1[0]][i][0])
            $('.form1 .public-img-list .img-detail').eq(i).find('.share_tag').html(public_img1[frame_arry1[0]][i][1])
            $('.form1 .public-img-list .img-detail').eq(i).find('.share_time').html(year+'-'+month+'-'+date+' '+hour+':'+min+':'+second)
        }
    }
    if(private_img1 == undefined || private_img1[frame_arry1[0]] == undefined){

    }else{
        for (var i = 0, len = private_img1[frame_arry1[0]].length; i < len; i++) {
            var year = new Date(private_img1[frame_arry1[0]][i][2]).getFullYear()
            var month = new Date(private_img1[frame_arry1[0]][i][2]).getMonth()+1
            var date = new Date(private_img1[frame_arry1[0]][i][2]).getDate()
            var hour = new Date(private_img1[frame_arry1[0]][i][2]).getHours();
            var min = new Date(private_img1[frame_arry1[0]][i][2]).getMinutes();
            var second = new Date(private_img1[frame_arry1[0]][i][2]).getSeconds();
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


            $('.clone-box .img-detail').clone().appendTo($('.form1 .private-img-list'))
            $('.form1 .private-img-list .img-detail').eq(i).find('.share_name').html(private_img1[frame_arry1[0]][i][0])
            $('.form1 .private-img-list .img-detail').eq(i).find('.share_tag').html(private_img1[frame_arry1[0]][i][1])
            $('.form1 .private-img-list .img-detail').eq(i).find('.share_time').html(year+'-'+month+'-'+date+' '+hour+':'+min+':'+second)
        }
    }


    //分布式任务
    for (var j = 0; j < frame_arry2.length; j++) {
        $('.form2 .select_framework').append('<option value="' + frame_arry2[j] + '">' + frame_arry2[j] + '</option>')
    }
    for (var i = 0, len = public_img2[frame_arry2[0]].length; i < len; i++) {

        var year = new Date(public_img2[frame_arry2[0]][i][2]).getFullYear()
        var month = new Date(public_img2[frame_arry2[0]][i][2]).getMonth()+1
        var date = new Date(public_img2[frame_arry2[0]][i][2]).getDate()
        var hour = new Date(public_img2[frame_arry2[0]][i][2]).getHours();
        var min = new Date(public_img2[frame_arry2[0]][i][2]).getMinutes();
        var second = new Date(public_img2[frame_arry2[0]][i][2]).getSeconds();
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


        $('.clone-box .img-detail').clone().appendTo($('.form2 .public-img-list'))
        $('.form2 .public-img-list .img-detail').eq(i).find('.share_name').html(public_img2[frame_arry2[0]][i][0])
        $('.form2 .public-img-list .img-detail').eq(i).find('.share_tag').html(public_img2[frame_arry2[0]][i][1])
        $('.form2 .public-img-list .img-detail').eq(i).find('.share_time').html(year+'-'+month+'-'+date+' '+hour+':'+min+':'+second)
    }
    if(private_img2 == undefined || private_img2[frame_arry2[0]] == undefined){

    }else{
        for (var i = 0, len = private_img2[frame_arry2[0]].length; i < len; i++) {

            var year = new Date(private_img2[frame_arry2[0]][i][2]).getFullYear()
            var month = new Date(private_img2[frame_arry2[0]][i][2]).getMonth()+1
            var date = new Date(private_img2[frame_arry2[0]][i][2]).getDate()
            var hour = new Date(private_img2[frame_arry2[0]][i][2]).getHours();
            var min = new Date(private_img2[frame_arry2[0]][i][2]).getMinutes();
            var second = new Date(private_img2[frame_arry2[0]][i][2]).getSeconds();
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

            $('.clone-box .img-detail').clone().appendTo($('.form2 .private-img-list'))
            $('.form2 .private-img-list .img-detail').eq(i).find('.share_name').html(private_img2[frame_arry2[0]][i][0])
            $('.form2 .private-img-list .img-detail').eq(i).find('.share_tag').html(private_img2[frame_arry2[0]][i][1])
            $('.form2 .private-img-list .img-detail').eq(i).find('.share_time').html(year+'-'+month+'-'+date+' '+hour+':'+min+':'+second)
        }
    }



    if($('.form1 .select_framework').val() == 'caffe'){
        $('.form1 .other-frame').css('display','none')
        $('.form1 .caffe-load').show()
    }else{
        $('.form1 .other-frame').css('display','block')
        $('.form1 .caffe-load').hide()
    }



})

// 分区
$.ajax({
    type:'GET',
    url:'/vip/new',
    success:function (e) {
        console.log('===========',e)
        for (var i = 0; i<e.usable_label_gpu_count.length;i++){
            console.log('--------分区--------',e.usable_label_gpu_count.length)

            // $('.clone-box .fen-list').clone().appendTo($('.form1 .fen-box'));
            // $('.form1 .fen-list').eq(i).children().eq(0).find('label').html(e.usable_label_gpu_count[i][0])
            // $('.form1 .fen-list').eq(i).children().eq(1).html(e.usable_label_gpu_count[i][1][0] + '个')
            // $('.form1 .fen-list').eq(i).children().eq(2).html(e.usable_label_gpu_count[i][1][1] + 'Core')
            // $('.form1 .fen-list').eq(i).children().eq(3).html(e.usable_label_gpu_count[i][1][2] + 'GB')



            $('.clone-box .fen-list').clone().appendTo($('.form1 .fen-box'));
            $('.form1 .fen-box .fen-list').eq(i).children().eq(0).find('label').html(e.usable_label_gpu_count[i][0])
            $('.form1 .fen-box .fen-list').eq(i).children().eq(1).html(e.usable_label_gpu_count[i][1][0] + '个')
            $('.form1 .fen-box .fen-list').eq(i).children().eq(2).html(e.usable_label_gpu_count[i][1][1] + 'Core')
            $('.form1 .fen-box .fen-list').eq(i).children().eq(3).html(e.usable_label_gpu_count[i][1][2] + 'GB')
        }
    }
})
$.ajax({
    type:'GET',
    url:'/vip/new',
    success:function (e) {
        console.log('===========',e)
        for (var i = 0; i<e.usable_label_gpu_count.length;i++){
            console.log('--------分区2--------',e.usable_label_gpu_count[0][0])

            // $('.clone-box .fen-list').clone().appendTo($('.form1 .fen-box'));
            // $('.form1 .fen-list').eq(i).children().eq(0).find('label').html(e.usable_label_gpu_count[i][0])
            // $('.form1 .fen-list').eq(i).children().eq(1).html(e.usable_label_gpu_count[i][1][0] + '个')
            // $('.form1 .fen-list').eq(i).children().eq(2).html(e.usable_label_gpu_count[i][1][1] + 'Core')
            // $('.form1 .fen-list').eq(i).children().eq(3).html(e.usable_label_gpu_count[i][1][2] + 'GB')


            $('.clone-box .fen-list').clone().appendTo($('.form2 .fen-box'));
            $('.form2 .fen-list').eq(i).children().eq(0).find('label').html(e.usable_label_gpu_count[i][0])
            $('.form2 .fen-list').eq(i).children().eq(1).html(e.usable_label_gpu_count[i][1][0] + '个')
            $('.form2 .fen-list').eq(i).children().eq(2).html(e.usable_label_gpu_count[i][1][1] + 'Core')
            $('.form2 .fen-list').eq(i).children().eq(3).html(e.usable_label_gpu_count[i][1][2] + 'GB')
        }
    }
})






$('.form1 .select_framework').on('change',function () {

    var framework = $(this).val()
    $.post('/vip/frame_select', {'frame_obj': ''}, function (e) {

        frame_arry1 = e.single_frame[2]['image']

        public_img1 = e.single_frame[0]['share_value']

        private_img1 = e.single_frame[1]['private_value']
        var public_key = Object.keys(public_img1)
        var private_key = Object.keys(private_img1)
        //单机任务

        $('.form1 .public-img-list').children().remove()
        $('.form1 .private-img-list').children().remove()
        for (var i = 0,len = public_key.length; i<len;i++){
            if(framework == public_key[i]){

                console.log('-----',public_img1[framework])
                for (var i = 0, len = public_img1[framework].length; i < len; i++) {
                    var year = new Date(public_img1[framework][i][2]).getFullYear()
                    var month = new Date(public_img1[framework][i][2]).getMonth()+1
                    var date = new Date(public_img1[framework][i][2]).getDate()
                    var hour = new Date(public_img1[framework][i][2]).getHours();
                    var min = new Date(public_img1[framework][i][2]).getMinutes();
                    var second = new Date(public_img1[framework][i][2]).getSeconds();
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


                    $('.clone-box .img-detail').clone().appendTo($('.form1 .public-img-list'))
                    $('.form1 .public-img-list .img-detail').eq(i).find('.share_name').html(public_img1[framework][i][0])
                    $('.form1 .public-img-list .img-detail').eq(i).find('.share_tag').html(public_img1[framework][i][1])
                    $('.form1 .public-img-list .img-detail').eq(i).find('.share_time').html(year+'-'+month+'-'+date+' '+hour+':'+min+':'+second)
                }
            }
        }



        for (var i = 0,len = private_key.length; i<len;i++){
            if(framework == private_key[i]){


                for (var i = 0, len = private_img1[framework].length; i < len; i++) {

                    var year = new Date(private_img1[framework][i][2]).getFullYear()
                    var month = new Date(private_img1[framework][i][2]).getMonth()+1
                    var date = new Date(private_img1[framework][i][2]).getDate()
                    var hour = new Date(private_img1[framework][i][2]).getHours();
                    var min = new Date(private_img1[framework][i][2]).getMinutes();
                    var second = new Date(private_img1[framework][i][2]).getSeconds();
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


                    $('.clone-box .img-detail').clone().appendTo($('.form1 .private-img-list'))
                    $('.form1 .private-img-list .img-detail').eq(i).find('.share_name').html(private_img1[framework][i][0])
                    $('.form1 .private-img-list .img-detail').eq(i).find('.share_tag').html(private_img1[framework][i][1])
                    $('.form1 .private-img-list .img-detail').eq(i).find('.share_time').html(year+'-'+month+'-'+date+' '+hour+':'+min+':'+second)
                }
            }
        }

        if($('.form1 .select_framework').val() == 'caffe'){
            $('.form1 .other-frame').css('display','none')
            $('.form1 .caffe-load').show()
        }else{
            $('.form1 .other-frame').css('display','block')
            $('.form1 .caffe-load').hide()
        }
    })
})


$('.form2 .select_framework').on('change',function () {

    var framework = $(this).val()
    $.post('/vip/frame_select', {'frame_obj': ''}, function (e) {
        console.log('--------d',e)

        frame_arry2 = e.distributed_frame[2]['image']

        public_img2 = e.distributed_frame[0]['share_value']

        private_img2 = e.distributed_frame[1]['private_value']

        var public_key = Object.keys(public_img2)
        var private_key = Object.keys(private_img2)

        console.log('-------',framework)
        $('.form2 .public-img-list').children().remove()
        $('.form2 .private-img-list').children().remove()

        for (var i = 0,len = public_key.length; i<len;i++){
            if(framework == public_key[i]){


                for (var i = 0, len = public_img2[framework].length; i < len; i++) {
                    $('.clone-box .img-detail').clone().appendTo($('.form2 .public-img-list'))
                    $('.form2 .public-img-list .img-detail').eq(i).find('.share_name').html(public_img2[framework][i][0])
                    $('.form2 .public-img-list .img-detail').eq(i).find('.share_tag').html(public_img2[framework][i][1])
                    $('.form2 .public-img-list .img-detail').eq(i).find('.share_time').html(public_img2[framework][i][2])
                }
            }
        }



        for (var i = 0,len = private_key.length; i<len;i++){
            if(framework == private_key[i]){


                for (var i = 0, len = private_img2[framework].length; i < len; i++) {
                    $('.clone-box .img-detail').clone().appendTo($('.form2 .private-img-list'))
                    $('.form2 .private-img-list .img-detail').eq(i).find('.share_name').html(private_img2[framework][i][0])
                    $('.form2 .private-img-list .img-detail').eq(i).find('.share_tag').html(private_img2[framework][i][1])
                    $('.form2 .private-img-list .img-detail').eq(i).find('.share_time').html(private_img2[framework][i][2])
                }
            }
        }

        if($('.form2 .select_framework').val() == 'caffempi'){
            $('.form2 .other-frame').css('display','none')
            $('.form2 .caffe-load').show()
        }else{
            $('.form2 .other-frame').css('display','block')
            $('.form2 .caffe-load').hide()
        }
    })
})

$('.vname').focus(function () {
    $(this).parents('.input-group').removeClass('has-error')
})
$('.load-path1').focus(function () {
    $(this).parents('.input-group').removeClass('has-error')
})
$('.caffe-load-path1').focus(function () {
    $(this).parents('.input-group').removeClass('has-error')
})
$('.caffe-load-path2').focus(function () {
    $(this).parents('.input-group').removeClass('has-error')
})


//表单提交验证
var flag1 = true;
function mySubmit1() {
    console.log('-----flag1-----',flag1)
    var v_name = $('.vname').val();
    var v_framework = $('#select_model_cj').val();
    var v_code = $('#image_list1').val()
    var v_loadcode = $('.load-path1').val()
    var v_loadcode_caffe1 = $('.caffe-load-path1').val()
    var v_loadcode_caffe2 = $('.caffe-load-path2').val()
    var main_file = $('.form1 .main_name').val()
    if(flag1 == false){
        return false
    }
    if (v_name == ''){
        $('.vname').parents('.input-group').addClass('has-error')

        return false;
    }
    if (v_framework == 'caffe'){
        if(v_code == '' && v_loadcode_caffe1 == '' && v_loadcode_caffe2 == ''){

            $('.caffe-load-path1').parents('.input-group').addClass('has-error')
            $('.caffe-load-path2').parents('.input-group').addClass('has-error')

            return false;
        }

    }else{
        if(v_code == '' && v_loadcode == ''){
            $('.load-path1').parents('.input-group').addClass('has-error')

            return false;
        }
    }

    // if(v_framework == 'caffe' || v_framework == 'mxnet'){
    //     if(main_file == ''){
    //         $('.static').show()
    //         $('.static strong').html('主文件名未填写！')
    //
    //         return false
    //     }
    // }

    var nodes = 1;
    var tabs = 0
    var gpu = $('form1').find('.gpu_count').val();
    var cpu = $('form1').find('.cpu_count').val()
    var para_obj ={'ismore':tabs,'node_count':nodes,'gpu_count':gpu,'cpu_count':cpu}
    $.ajax({
        url:'/vip/check_res',
        method:'GET',
        data:para_obj,
        success:function(e){
            console.log(e.a)
            if (e.a == 0) {
                $('.static').show()
                $('.static strong').html(e.res)

                return false;
            } else if(e.a == 1){

            }
        }
    })

    $('.form1 .img-checked').each(function () {
        if($(this).is(":checked")){
            var img_name = $(this).next('label').html()
            var img_tag = $(this).parents('.img-detail').children().eq(1).html()
            var img_time = $(this).parents('.img-detail').children().eq(2).html()

            $('.form1').find('.img-name').val(img_name)
            $('.form1').find('.img-tag').val(img_tag)
            $('.form1').find('.img-time').val(img_time)
        }
    })
    $('.form1 .fenqu-checked').each(function () {
        if($(this).is(":checked")){
            var fen_name = $(this).next('label').html()
            $('.form1').find('.fen-name').val(fen_name)
        }
    })





    flag1 = false
    return true;
}
var flag2 = true;
function mySubmit_distribute() {

    console.log('----------form2')
    var v_name2 = $('#distribute_name').val();
    var v_framework2 = $('#select_model_cjs').val();
    var v_code2 = $('#image_list2').val()
    var v_loadcode2 = $('.load-path2').val()
    var v_loadcode_caffempi1 = $('.caffempi-load-path1').val()
    var v_loadcode_caffempi2 = $('.caffempi-load-path2').val()
    var main_file = $('.form2 .main_name').val()
    if(flag2 == false){
        return false
    }
    if (v_name2 == ''){
        $('.static').show()
        $('.static strong').html('作业名称不能为空！')

        return false;
    }
    if (v_framework2 == 'caffempi'){

        if(v_code2 == '' && v_loadcode_caffempi1 == '' && v_loadcode_caffempi2 == ''){
            $('.static').show()
            $('.static strong').html('代码文件不能为空！')

            return false;
        }



    }else{
        if(v_code2 == '' && v_loadcode2 == ''){
            $('.static').show()
            $('.static strong').html('代码文件不能为空！')

            return false;
        }
    }
    // if(v_framework2 == 'caffempi' || v_framework2 == 'tensorflowmpi'){
    //     if(main_file == ''){
    //         $('.static').show()
    //         $('.static strong').html('主文件名未填写！')
    //
    //         return false
    //     }
    // }

    var nodes = $('form2').find('.node_counts').val();
    var tabs = 1
    var gpu = $('form2').find('.gpu_counts').val();
    var cpu = $('form2').find('.cpu_counts').val()
    var para_obj ={'ismore':tabs,'node_count':nodes,'gpu_count':gpu,'cpu_count':cpu}
    $.ajax({
        url:'/vip/check_res',
        method:'GET',
        data:para_obj,
        success:function(e){
            console.log(e.a)
            if (e.a == 0) {
                $('.static').show()
                $('.static strong').html(e.res)

                return false;
            } else if(e.a == 1){

            }
        }
    })



    $('.form2 .img-checked').each(function () {
        if($(this).is(":checked")){
            var img_name = $(this).next('label').html()
            var img_tag = $(this).parents('.img-detail').children().eq(1).html()
            var img_time = $(this).parents('.img-detail').children().eq(2).html()

            $('.form2').find('.img-name').val(img_name)
            $('.form2').find('.img-tag').val(img_tag)
            $('.form2').find('.img-time').val(img_time)
        }
    })
    $('.form2 .fenqu-checked').each(function () {
        if($(this).is(":checked")){
            var fen_name = $(this).next('label').html()
            $('.form2').find('.fen-name').val(fen_name)
        }
    })


    flag2 = false


    return true;
}


//关闭提示框
$(".close").click(function(){
    // $(".alert").alert('close');
    $('.static').css('display','none')
    $('.modal-backdrop').hide()
});



$('.refresh-btn').on('click',function () {
    $(this).removeClass('c-green').addClass('c-gray')
    $.ajax({
        type:'GET',
        url:'/vip/get_framework',
        success:function (e) {
            console.log('----refresh----',e)
            if(e.statu == 'Successful!'){

                $('.refresh-btn').removeClass('c-gray').addClass('c-green')

                var frame_arry1,frame_arry2,public_img1,public_img2,private_img1,private_img2
                console.log('=======')


                console.log('------------')
                $.post('/vip/frame_select', {'frame_obj': ''}, function (e) {
                    console.log('single--------d',e)
                    frame_arry1 = e.single_frame[2]['image']
                    frame_arry2 = e.distributed_frame[2]['image']
                    public_img1 = e.single_frame[0]['share_value']
                    public_img2 = e.distributed_frame[0]['share_value']
                    private_img1 = e.single_frame[1]['private_value']
                    private_img2 = e.distributed_frame[1]['private_value']
                    // console.log(private_img2[frame_arry2[0]])
                    //单机任务
                    $('.form1 .select_framework').children().remove();
                    $('.form2 .select_framework').children().remove();
                    $('.form1 .public-img-list').children().remove();
                    $('.form1 .private-img-list').children().remove();
                    $('.form2 .public-img-list').children().remove();
                    $('.form2 .private-img-list').children().remove();
                    for (var j = 0; j < frame_arry1.length; j++) {
                        $('.form1 .select_framework').append('<option value="' + frame_arry1[j] + '">' + frame_arry1[j] + '</option>')
                    }
                    if(public_img1 == undefined || public_img1[frame_arry1[0]] == undefined){

                    }else{
                        for (var i = 0, len = public_img1[frame_arry1[0]].length; i < len; i++) {

                            var year = new Date(public_img1[frame_arry1[0]][i][2]).getFullYear()
                            var month = new Date(public_img1[frame_arry1[0]][i][2]).getMonth()+1
                            var date = new Date(public_img1[frame_arry1[0]][i][2]).getDate()
                            var hour = new Date(public_img1[frame_arry1[0]][i][2]).getHours();
                            var min = new Date(public_img1[frame_arry1[0]][i][2]).getMinutes();
                            var second = new Date(public_img1[frame_arry1[0]][i][2]).getSeconds();
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


                            $('.clone-box .img-detail').clone().appendTo($('.form1 .public-img-list'))
                            $('.form1 .public-img-list .img-detail').eq(i).find('.share_name').html(public_img1[frame_arry1[0]][i][0])
                            $('.form1 .public-img-list .img-detail').eq(i).find('.share_tag').html(public_img1[frame_arry1[0]][i][1])
                            $('.form1 .public-img-list .img-detail').eq(i).find('.share_time').html(year+'-'+month+'-'+date+' '+hour+':'+min+':'+second)
                        }
                    }
                    if(private_img1 == undefined || private_img1[frame_arry1[0]] == undefined){

                    }else{
                        for (var i = 0, len = private_img1[frame_arry1[0]].length; i < len; i++) {
                            var year = new Date(private_img1[frame_arry1[0]][i][2]).getFullYear()
                            var month = new Date(private_img1[frame_arry1[0]][i][2]).getMonth()+1
                            var date = new Date(private_img1[frame_arry1[0]][i][2]).getDate()
                            var hour = new Date(private_img1[frame_arry1[0]][i][2]).getHours();
                            var min = new Date(private_img1[frame_arry1[0]][i][2]).getMinutes();
                            var second = new Date(private_img1[frame_arry1[0]][i][2]).getSeconds();
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


                            $('.clone-box .img-detail').clone().appendTo($('.form1 .private-img-list'))
                            $('.form1 .private-img-list .img-detail').eq(i).find('.share_name').html(private_img1[frame_arry1[0]][i][0])
                            $('.form1 .private-img-list .img-detail').eq(i).find('.share_tag').html(private_img1[frame_arry1[0]][i][1])
                            $('.form1 .private-img-list .img-detail').eq(i).find('.share_time').html(year+'-'+month+'-'+date+' '+hour+':'+min+':'+second)
                        }
                    }


                    //分布式任务
                    for (var j = 0; j < frame_arry2.length; j++) {
                        $('.form2 .select_framework').append('<option value="' + frame_arry2[j] + '">' + frame_arry2[j] + '</option>')
                    }
                    for (var i = 0, len = public_img2[frame_arry2[0]].length; i < len; i++) {

                        var year = new Date(public_img2[frame_arry2[0]][i][2]).getFullYear()
                        var month = new Date(public_img2[frame_arry2[0]][i][2]).getMonth()+1
                        var date = new Date(public_img2[frame_arry2[0]][i][2]).getDate()
                        var hour = new Date(public_img2[frame_arry2[0]][i][2]).getHours();
                        var min = new Date(public_img2[frame_arry2[0]][i][2]).getMinutes();
                        var second = new Date(public_img2[frame_arry2[0]][i][2]).getSeconds();
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


                        $('.clone-box .img-detail').clone().appendTo($('.form2 .public-img-list'))
                        $('.form2 .public-img-list .img-detail').eq(i).find('.share_name').html(public_img2[frame_arry2[0]][i][0])
                        $('.form2 .public-img-list .img-detail').eq(i).find('.share_tag').html(public_img2[frame_arry2[0]][i][1])
                        $('.form2 .public-img-list .img-detail').eq(i).find('.share_time').html(year+'-'+month+'-'+date+' '+hour+':'+min+':'+second)
                    }
                    if(private_img2 == undefined || private_img2[frame_arry2[0]] == undefined){

                    }else{
                        for (var i = 0, len = private_img2[frame_arry2[0]].length; i < len; i++) {

                            var year = new Date(private_img2[frame_arry2[0]][i][2]).getFullYear()
                            var month = new Date(private_img2[frame_arry2[0]][i][2]).getMonth()+1
                            var date = new Date(private_img2[frame_arry2[0]][i][2]).getDate()
                            var hour = new Date(private_img2[frame_arry2[0]][i][2]).getHours();
                            var min = new Date(private_img2[frame_arry2[0]][i][2]).getMinutes();
                            var second = new Date(private_img2[frame_arry2[0]][i][2]).getSeconds();
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

                            $('.clone-box .img-detail').clone().appendTo($('.form2 .private-img-list'))
                            $('.form2 .private-img-list .img-detail').eq(i).find('.share_name').html(private_img2[frame_arry2[0]][i][0])
                            $('.form2 .private-img-list .img-detail').eq(i).find('.share_tag').html(private_img2[frame_arry2[0]][i][1])
                            $('.form2 .private-img-list .img-detail').eq(i).find('.share_time').html(year+'-'+month+'-'+date+' '+hour+':'+min+':'+second)
                        }
                    }



                    if($('.form1 .select_framework').val() == 'caffe'){
                        $('.form1 .other-frame').css('display','none')
                        $('.form1 .caffe-load').show()
                    }else{
                        $('.form1 .other-frame').css('display','block')
                        $('.form1 .caffe-load').hide()
                    }







                })





            }else{
                // $('.static').show()
                // $('.static strong').html(e.statu)
            }
        }
    })
})

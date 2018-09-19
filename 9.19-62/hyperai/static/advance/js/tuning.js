$('#opt-fun').on('change',function(){
	if ($(this).val() == 'GD') {
		$('.gd-box').show()
		$('.checkbox-lr').hide()
		$('.gd-box').siblings().hide()
	} else if($(this).val() == 'RMSProp'){
		$('.gd-box').show()
		$('.checkbox-lr').hide()
		$('.gd-box').siblings().hide()
		$('.rmsprop-box').show();
		$('.checkbox-momen').show()
		
	}
	else if($(this).val() == 'Adam'){
		$('.gd-box').show()
		$('.checkbox-lr').show()
		$('.gd-box').siblings().hide()
		$('.adam-box').show();
		
	}
	else if($(this).val() == 'Momentum'){
		$('.gd-box').show()
		$('.checkbox-lr').hide()
		$('.gd-box').siblings().hide()
		$('.rmsprop-momen').show();
		$('.checkbox-momen').hide()
		
	}
})

$('.format-box input').focus(function(){
	$(this).parents('.format-box').find('.format').show()
})
$('.format-box input').blur(function(){
	$(this).parents('.format-box').find('.format').hide()
})



//上传文件
$('#image_list2').on('change',function (e) {
    var file_num = $(this)[0].files.length;
    if(file_num == 1){
        $('.image_list_i_2').val(e.currentTarget.files[0].name)
    }else{
        $('.image_list_i_2').val(file_num + '个文件')
    }
})


// 分区
$.get('/tuning',function (e) {
    console.log('----fenqu----',e)
    for (var i = 0; i<e.usable_label_gpu_count.length;i++){

        $('.clone-box .fen-list').clone().appendTo($('.fen-box'));
        $('.fen-box .fen-list').eq(i).children().eq(0).find('label').html(e.usable_label_gpu_count[i][0])
        $('.fen-box .fen-list').eq(i).children().eq(1).html(e.usable_label_gpu_count[i][1][0] + '个')
        $('.fen-box .fen-list').eq(i).children().eq(2).html(e.usable_label_gpu_count[i][1][1] + 'Core')
        $('.fen-box .fen-list').eq(i).children().eq(3).html(e.usable_label_gpu_count[i][1][2] + 'GB')


        // $('.clone-box .fen-list').clone().appendTo($('.form2 .fen-box'));
        // $('.form2 .fen-list').eq(i).children().eq(0).find('label').html(e.usable_label_gpu_count[i][0])
        // $('.form2 .fen-list').eq(i).children().eq(1).html(e.usable_label_gpu_count[i][1][0] + '个')
        // $('.form2 .fen-list').eq(i).children().eq(2).html(e.usable_label_gpu_count[i][1][1] + 'Core')
        // $('.form2 .fen-list').eq(i).children().eq(3).html(e.usable_label_gpu_count[i][1][2] + 'GB')
    }
})




//提交，check

// var flag = 1
$("input[type='button']").on('click',function() {



        $('.fen-box .fenqu-checked').each(function () {
            if($(this).is(":checked")){
                var fen_name = $(this).next('label').html()
                $('form').find('.fen-name').val(fen_name)
            }
        })

        $(".check").each(function() {
            let t1 = $(this).parents('.check-box').next('div').find('input').val();
            let t2 = $(this).parents('.check-box').next('div').next('span').next('div').find('input').val();
            let t_arry = [];
            t_arry.push(t1,t2);
            let t_str = t_arry.join()
            console.log('123',t_str)
            if(($(this).is(":checked")) && (t_arry.length !== 0)) {
                let txt_flag = $(this).parents('.format-box').prev('h4').html()
                if(txt_flag === '学习率(lr)'){
                    console.log('lr')
                    localStorage.setItem('fun',txt_flag)
                    $(this).parents('.format-box').find("input[type='hidden']").val('lr')

                }else if(txt_flag === '动量(momentum)'){
                    localStorage.setItem('fun1',txt_flag)
                    console.log('momentum')
                    $(this).parents('.format-box').find("input[type='hidden']").val('momentum')

                }else if(txt_flag === '梯度衰减因子(decay)'){
                    localStorage.setItem('fun2',txt_flag)
                    console.log('decay')
                    $(this).parents('.format-box').find("input[type='hidden']").val('decay')

                }else if(txt_flag === '指数衰减率1(beta1)'){
                    localStorage.setItem('fun3',txt_flag)
                    console.log('beta1')
                    $(this).parents('.format-box').find("input[type='hidden']").val('beta1')

                }else if(txt_flag === '指数衰减率2(beta2)'){
                    localStorage.setItem('fun4',txt_flag)
                    console.log('beta2')
                    $(this).parents('.format-box').find("input[type='hidden']").val('beta2')

                }


                $(this).val(t_str)
                console.log('++++++++++', $(this).val())

            } else {

            }
        })
        if($('#homework_name').val() == ''){
            $('.static').show()
            $('#myAlert').show()
            $('.static strong').html('作业名称不能为空！')
            // $('.prompt-box').css('display','block')
            // $('.prompt-box .alert-div-content h3').html('作业名称不能为空！')

            return false
        }else if(($('#model_file').val() == '') && ($('#model_path').val() == '')){
            $('.static').show()
            $('#myAlert').show()
            $('.static strong').html('模型文件或路径不能为空！')
            // $('.prompt-box').css('display','block')
            // $('.prompt-box .alert-div-content h3').html('模型文件或路径不能为空！')

            return false
        }else if($('#dataset_file').val() == ''){
            $('.static').show()
            $('#myAlert').show()
            $('.static strong').html('选择数据集不能为空！')
            // $('.prompt-box').css('display','block')
            // $('.prompt-box .alert-div-content h3').html('选择数据集不能为空！')

            return false
        }else if($('#bayesion_iteration').val() == ''){
            $('.static').show()
            $('#myAlert').show()
            $('.static strong').html('bayesion迭代次数不能为空！')
            // $('.prompt-box').css('display','block')
            // $('.prompt-box .alert-div-content h3').html('bayesion迭代次数不能为空！')

            return false
        }else if($('#model_iteration').val() == ''){
            $('.static').show()
            $('#myAlert').show()
            $('.static strong').html('模型迭代次数不能为空！')
            // $('.prompt-box').css('display','block')
            // $('.prompt-box .alert-div-content h3').html('模型迭代次数不能为空！')

            return false
        }else if($('#batch_size').val() == ''){
            $('.static').show()
            $('#myAlert').show()
            $('.static strong').html('batch-size不能为空！')
            // $('.prompt-box').css('display','block')
            // $('.prompt-box .alert-div-content h3').html('batch-size不能为空！')

            return false
        }

        console.log($('#gpu_count').val())
        var gpu = $('#gpu_count').val()
        var para_obj ={'gpu_count':gpu}
        // $.ajax({
        //     url:'/tuning/check_res',
        //     method:'GET',
        //     data:para_obj,
        //     success:function(e){
        //
        //         if (e.a == 0) {
        //             $('.static').show()
        //             $('#myAlert').show()
        //             $('.static strong').html(e.res)
        //             // alert(e.res);
        //             return false
        //         } else if(e.a == 1){
        //             // console.log("xxx")
        //             console.log('----------------------flag')
        //             flag = 2
        //             // return true
        //             $('form').submit();
        //             // window.location.href='/show/paraopt/monitor'
        //         }
        //     }
        // })

    var form = new FormData(document.getElementById("formid"));

    console.log('-------form----', form.get('homework_name'))
    $.ajax({
        url:"/tuning/new",
        type:"POST",
        data:form,
        dataType: "json",
        contentType: false, //必须
        processData: false,
        success:function(data){

            console.log("over..",data);
            localStorage.removeItem('data')
          	localStorage.setItem('data',JSON.stringify({'create_time':data.create_time,'statue':data.statue,'job_id':data.job_id,'method':data.method}))
            window.location.href='/show/paraopt/monitor'
        },
        error:function(e){
            console.log("error..",e);
            alert("错误！！");

        }
    });




})
//关闭提示框
$(".close").click(function(){
    $(".alert").alert('close');
    $('.static').css('display','none')
    $('.modal-backdrop').hide()
});

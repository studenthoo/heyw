
var flag = 1
$("input[type='button']").on('click',function() {


	if(flag == 1) {



		$(".check").each(function() {
			let t1 = $(this).next('input').val();
			let t2 = $(this).next('input').next('em').next('input').val();
			let t_arry = [];
			t_arry.push(t1,t2);
			let t_str = t_arry.join()
			if(($(this).is(":checked")) && (t_arry.length !== 0)) {
				let txt_flag = $(this).parents('.l-box').find('h4').html()
				if(txt_flag === '学习率(lr)'){
					console.log('lr')
					$(this).siblings("input[type='hidden']").val('lr')

				}else if(txt_flag === '动量(momentum)'){
                    console.log('momentum')
					$(this).siblings("input[type='hidden']").val('momentum')

				}else if(txt_flag === '梯度衰减因子(decay)'){
                    console.log('decay')
					$(this).siblings("input[type='hidden']").val('decay')

				}else if(txt_flag === '指数衰减率1(beta1)'){
                    console.log('beta1')
					$(this).siblings("input[type='hidden']").val('beta1')

				}else if(txt_flag === '指数衰减率2(beta2)'){
                    console.log('beta2')
					$(this).siblings("input[type='hidden']").val('beta2')

				}


				$(this).val(t_str)
				console.log('++++++++++', $(this).val())

			} else {

			}
		})
        if($('#homework_name').val() == ''){
			$('.prompt-box').css('display','block')
			$('.prompt-box .alert-div-content h3').html('作业名称不能为空！')

			return false
		}else if(($('#model_file').val() == '') && ($('#model_path').val() == '')){
			$('.prompt-box').css('display','block')
			$('.prompt-box .alert-div-content h3').html('模型文件或路径不能为空！')

			return false
        }else if($('#dataset_file').val() == ''){
			$('.prompt-box').css('display','block')
			$('.prompt-box .alert-div-content h3').html('选择数据集不能为空！')

			return false
		}else if($('#bayesion_iteration').val() == ''){
			$('.prompt-box').css('display','block')
			$('.prompt-box .alert-div-content h3').html('bayesion迭代次数不能为空！')

            return false
        }else if($('#model_iteration').val() == ''){
			$('.prompt-box').css('display','block')
			$('.prompt-box .alert-div-content h3').html('模型迭代次数不能为空！')

            return false
        }else if($('#batch_size').val() == ''){
			$('.prompt-box').css('display','block')
			$('.prompt-box .alert-div-content h3').html('batch-size不能为空！')
          
            return false
        }
			// else {
		// 	$('.t-box1').find("input[type='text']").each(function () {
		// 		if($(this).val() == ''){
         //            alert('参数不能为空')
         //            return false
		// 		}else{
         //            // alert('参数不能为空')
         //            // return false
		// 		}
         //    })
		// }
        console.log($('#gpu_count').val())
        var gpu = $('#gpu_count').val()
        var para_obj ={'gpu_count':gpu}
        $.ajax({
            url:'check_res',
            method:'GET',
            data:para_obj,
            success:function(e){

                if (e.a == 0) {
					$('.alert-box').css('display','block')
					$('.alert-div-content').find('h3').html(e.res)
					$('.alert-box .alert-btn-yes').on('click',function () {
						$('.alert-box').css('display','none')
					})
                    // alert(e.res);
                    return false
                } else if(e.a == 1){
                    // console.log("xxx")
					console.log('----------------------flag')
                    flag = 2
                   // return true
                    $('form').submit();
                }
            }
        })
		// flag = 2
		// return true
		// console.log($(".study").val())

	} else {
		console.log('-------------')
		return false;
	}

})
// 框架选择
// $('.nav-tabs').append('<li><a href="#">自定义</a></li>')
$('#network-tab-custom').css('display','none')
        $('#stdnetRole').css('display','none')
 $('#network-tab-standard-contents').css('display','none')
$('#network-tabs li').on('click',function () {
    if($(this).children().text()=='Custom Network'){
         $('#network-tab-standard-contents').slideUp(500)
         $(this).children().css({
        'color':'white',
        'background':' #00b5b8'
        })
        $(this).siblings().children().css({
             'color':'#2c3850',
            'background':' #d9dce1'
        })
        // $('#network-tab-standard-contents').css('display','none')
        $('#stdnetRole').css('display','none')
        $('#network-tab-custom').css('display','block')
    }
    else{
        //   $(this).children().css({
        // 'color':'white',
        // 'background':' #00b5b8'
        // })
        // $(this).siblings().children().css({
        //      'color':'#2c3850',
        //     'background':' #d9dce1'
        // })
        // $('#network-tab-standard-contents').slideDown(500)
        // $('#stdnetRole').css('display','block')
        // $('#network-tab-custom').css('display','none')
         // $('.network-tab-standard-contents').css('display','block')
    }


})

// 自定义
$('#customFramework li').on('click',function () {
    // console.log($(this).children().children().children('span').text())
    $('.demo_border').html($(this).children().text())
    if($(this).children().children().children('span').text()=='Caffe'){
        $('#framework').attr('value','caffe')
    }
    else if($(this).children().children().children('span').text()=='Torch'){
         $('#framework').attr('value','torch')
    }
    else if($(this).children().text()=='Torch'){
        $('#framework').attr('value','torch')
    }
    else {
        $('#framework').attr('value','tensorflow')
    }

     $(this).children().css({
        'color':'white',
        'background':' #00b5b8'
        })
        $(this).siblings().children().css({
             'color':'#2c3850',
            'background':' #d9dce1'
        })
    console.log($('#framework').attr('value'))
})
$('#customFramework_many li').on('click',function () {
		 console.log($(this).children().children().children().val())
		console.log(1)
		$('.demo_border').html($(this).children().children().children().val())
		if($(this).children().children().children().val()=='Caffe2'){
			$('#framework').attr('value','caffe2')
		}
		else if($(this).children().children().children().val()=='Tensorflow'){
			$('#framework').attr('value','tensorflow')
		}
		console.log($('#framework').attr('value'))
		$(this).children().css({
			'color':'#2c3850',
			'background':'rgb(0, 181, 184)'
		})
		$(this).siblings().children().css({
			'color':'black',
			'background':"rgb(217, 220, 225)"
		})
	})

$('.container2').css('display','none');
$('.container3').css('display','none');
$('.btn_data_2-no').on('click',function() {
    $('.container1').css('display', 'block').siblings().css('display', 'none')
})
$('.btn_data_3-no').on('click',function() {
    $('.container2').css('display', 'block').siblings().css('display', 'none')
})
$('.btn_data_1').on('click',function(){
    var gpu_count = '';
    var cpu_count = '';
    var memory_count = '';
    if($('.btn_i_node').html() == '单节点配置'){
        gpu_count = $('#gpu_count_new').val()
        cpu_count = $('#cpu_count').val()
        memory_count = $('#memory_count').val()

    }else if($('.btn_i_node').html() == '分布式配置'){
        gpu_count = $('#gpu_count_new_more').val()
        cpu_count = $('#cpu_count_more').val()
        memory_count = $('#memory_count_more').val()

    }
    $.ajax({
        type:'GET',
        url:'/models/images/classification/check_res',
        data:{
            gpu_count:gpu_count,
            cpu_count:cpu_count,
            memory_count:memory_count,
            node_count:$('#node_count').val(),
            ismpi:$('#train_method').val()
        },
        success:function (e) {
            console.log(e)
            if(e.a=='1'){
                $('.container2').css('display','block').siblings().css('display','none')
                $('.container1').css('display','none')
                $('.container3').css('display','none')
            }
            else {
                $('.alert-box').css('display','block')
                $('.alert-div-content').find('h3').html(e.res)
                $('.alert-btn-yes').on('click',function () {
                    $('.alert-box').css('display','none')
                })
                // alert(e.res)
            }
        }
    })
})

$('.btn_data_2').on('click',function(){
    // 第三页交互
    $('.demo_name').html($('.neme__data').val())  //项目名字
    $('.demo_back').html($('.select_model_xx').val())   //  应用场景
     // console.log($('.acen_select').val())
    $('.demo_border').html($('.select_kuangjia').val())  //训练框架
     // console.log($('.select_kuangjia').val())
    $('.demo_wang').html($('.select_wang').val())  //选取网络
    // console.log($('.select_wang').val())
    $('.demo_data').html($('.select_data').children().val())  //样本数据
    $('.demo_number').html($('.select_demo_number').val())  //迭代次数
    $('.demo_CPU').html($('#cpu_count').val()+'Core')  //CPU
    $('.demo_gp').html($('#memory_count').val()+'G')  //内存
    $('.demo_GPU').html($('#gpu_count_new').val())  //GPU
    $('.demo_time1').html($('.select_demo_time1').val())  //保存间隔
    $('.demo_time2').html($('.select_demo_time2').val())  //日志保存间隔
    if($('.btn_i_node').text() == '单节点配置'){
        $('.demo_all_num').html('1')
    }else if($('.btn_i_node').text() == '分布式配置'){
        $('.demo_all_num').html($('.node_num').val())
    }



    // 跳转
	$('.container3').css('display','block').siblings().css('display','none')
    $('.container1').css('display','none')
    $('.container2').css('display','none')
})
//页面数据
$(function(){
	//checkbox
	$(".lis-adcheck-show").on("ifChecked", function(event) {
 		      	$(".lis-adcheck-hide").show();
 	});
 	$(".lis-adcheck-show").on("ifUnchecked", function(event) {
 		        $(".lis-adcheck-hide").hide();
 	});

 	//自定义参数
 	// $(".customize-add").on("click", function() {
    //     customizeAdd(), $(".customize-addlis").each(function() {
    //         $(this) && $(this).find(".customize-remove").on("click", function() {
    //             $(this).parents(".customize-addlis").remove();
    //         }), $(this) && $(this).find(".customize-remove").on("click", function() {
    //                 $(this).children(".customize-addlis").remove();
    //             });
    //     });
    // });
    // $(".customize-remove").on("click", function() {
    //     $(this).parents(".customize-addlis").remove();
    // });
})
$('#select_cj_i').on('change',function () {
    // $.post(,{'value':$(this).val()},function (e) {
    //     console.log(e)
    //     remove($('#dataset').children());
    //     $('#dataset').append('<option>3123513535</option>')
    // })
})
// $('#dataset').append('<option>3123513535</option>')






function customizeAdd() {$(".lis-customizebox").append('<div class="c-box customize-addlis m-t15">'+'<input type="text" placeholder="Image1" class="f-l input-info bdr w-16-1 ml-12" />'+'<input type="text" placeholder="12444" class="f-l input-info bdr w-18 ml-12" />'+'<input type="text" placeholder="12444" class="f-l input-info bdr w-18 ml-12" />'+'<a href="#" class="f-r c-red customize-remove m-t5"> <i class="iconfont fz-20 plr-5"> &#xe638; </i></a>'+'</div>');};
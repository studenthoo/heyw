// 框架选择
// $('.nav-tabs').append('<li><a href="#">自定义</a></li>')
$('#network-tab-standard-contents').css('display','none')
$('#stdnetRole li').on('click',function () {

    $('.demo_border').html($(this).children().text())
    if($(this).children().text()=='自定义'){
         $('#network-tab-standard-contents').slideUp(500)
         $(this).children().css({
        'color':'white',
        'background':' #00b5b8'
        })
        $(this).siblings().children().css({
             'color':'#2c3850',
            'background':' #d9dce1'
        })
        $('.Now_work').css('display','block')

    }
    else{
        if($(this).children().text()=='Caffe'){
            console.log(1)
             $('#framework').attr('value','caffe')
        }
        else if($(this).children().text()=='Torch'){
            $('#framework').attr('value','torch')
        }
        else {
             console.log(2)
             $('#framework').attr('value','tensorflow')
        }
        // $('#framework').attr('value',$(this).children().text())
          $(this).children().css({
        'color':'white',
        'background':' #00b5b8'
        })
        $(this).siblings().children().css({
             'color':'#2c3850',
            'background':' #d9dce1'
        })
        $('#network-tab-standard-contents').slideDown(500)
         $('.Now_work').css('display','none')
        console.log($('#framework').attr('value'))
    }


})
// 自定义
$('#customFramework li').on('click',function () {
    // console.log($('#framework').attr('value'))
    // console.log($(this).children().children().children().val())
    $('.demo_border').html($(this).children().children().children().val())
    if($(this).children().children().children().val()=='Caffe'){
        $('#framework').attr('value','caffe')
    }
    else if($(this).children().children().children().val()=='Torch'){
        $('#framework').attr('value','torch')
    }
    else if($(this).children().children().children().val()=='Tensorflow'){
        $('#framework').attr('value','tensorflow')
    }
    console.log($('#framework').attr('value'))
    $('this').children().css({
        'color':'white',
        'background':'rgb(0, 181, 184)'
    })
    $('this').siblings().children().css({
        'color':'black',
        'background':"rgb(217, 220, 225)"
    })
})
$('.table input').on('click',function () {
    $(this).parent().parent().css('background','#d9dce1').siblings().css('background','white')
    $('.demo_wang').html($(this).siblings().text())
})







$('.container2').css('display','none');
$('.container3').css('display','none');
$('.btn_data_1').on('click',function(){
     // console.log({
     //        gpu_count:$('#gpu_count_new').val(),
     //        cpu_count:$('#cpu_count').val(),
     //        memory_count:$("#memory_count").val(),
     //        node_count:$('#node_count').val(),
     //        ismpi:$('#train_method').val()
     //    })
    $.ajax({
        type:'GET',
        url:'/models/images/classification/check_res',
        data:{
            gpu_count:$('#gpu_count_new').val(),
            cpu_count:$('#cpu_count').val(),
            memory_count:$("#memory_count").val(),
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
                alert(e.res)
            }
        }
    })
    // 选取网络
    $('tbody input').each(function () {
        if($(this).prop('checked')==true){
            $('.demo_wang').html($(this).val())
        }
    })
})

$('.btn_data_2').on('click',function(){
    // 第三页交互
    $('.demo_name').html($('.neme__data').val())  //项目名字
    $('.demo_back').html($('.acen_select').val())   //  应用场景
     console.log($('.acen_select').val())
    $('.demo_border').html($('#framework').attr('value'))  //训练框架
    $('.demo_data').html($('.select_data').children().val())  //样本数据
    $('.demo_number').html($('.select_demo_number').val())  //迭代次数
    $('.demo_CPU').html($('#cpu_count').val()+'Core')  //CPU
    $('.demo_gp').html($('#memory_count').val()+'G')  //内存
    $('.demo_GPU').html($('#gpu_count_new').val())  //GPU
    $('.demo_time1').html($('.select_demo_time1').val())  //保存间隔
    $('.demo_time2').html($('.select_demo_time2').val())  //日志保存间隔
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
 	$(".customize-add").on("click", function() {
        customizeAdd(), $(".customize-addlis").each(function() {
            $(this) && $(this).find(".customize-remove").on("click", function() {
                $(this).parents(".customize-addlis").remove();
            }), $(this) && $(this).find(".customize-remove").on("click", function() {
                    $(this).children(".customize-addlis").remove();
                });
        });
    });
    $(".customize-remove").on("click", function() {
        $(this).parents(".customize-addlis").remove();
    });
})
 // var editor = ace.edit("ace-editor");
 //                        editor.$blockScrolling = Infinity;
 //                        editor.setTheme("ace/theme/chrome");
 //                        editor.session.setFoldStyle('manual');
 //                        editor.setShowPrintMargin(false);
 //                        var PythonMode = ace.require("ace/mode/python").Mode;
 //                        var LuaMode = ace.require("ace/mode/lua").Mode;
 //                        $( document ).ready(function() {
 //                            editor.setValue($('textarea#custom_network').val());
 //                            editor.selection.moveTo(0, 0);
 //                            console.log($('textarea#custom_network').val())
 //                        });
 //                        $('body').on('click',function () {
 //                            console.log(editor.getValue())
 //                            $('#custom_network').val(editor.getValue())
 //                        })


$('#network-tabs li').on('click',function () {
    // $('.demo_border').html($(this).children().text())
    if($(this).children('a').text()=='Custom Network'){
        $('#network-tab-custom').css('display','block')
         $('.Standard_Networks').css('display','none')
        $('#method').val('custom')
    }
    else{
         $('#network-tab-custom').css('display','none')
         $('.Standard_Networks').css('display','block')
         $('#method').val('standard')
    }


        // $('#framework').attr('value',$(this).children().text())
          $(this).children().css({
        'color':'white',
        'background':' #00b5b8'
        })
        $(this).siblings().children().css({
             'color':'#2c3850',
            'background':' #d9dce1'
        })




})






function customizeAdd() {$(".lis-customizebox").append('<div class="c-box customize-addlis m-t15">'+'<input type="text" placeholder="Image1" class="f-l input-info bdr w-16-1 ml-12" />'+'<input type="text" placeholder="12444" class="f-l input-info bdr w-18 ml-12" />'+'<input type="text" placeholder="12444" class="f-l input-info bdr w-18 ml-12" />'+'<a href="#" class="f-r c-red customize-remove m-t5"> <i class="iconfont fz-20 plr-5"> &#xe638; </i></a>'+'</div>');};        
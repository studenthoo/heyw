/***
 * ----------------------------------------------------------------------------
 * js Document public js Start
 * Author: DistantSound
 * ----------------------------------------------------------------------------
 * 参数说明：
 *	easing                缓动效果
 * effect                动画效果
 * autoPlay              自动运行
 * interTime ,delayTime  毫秒
 *	defaultIndex          默认的当前位置索引0
 * defaultPlay           默认是否执行效果
 * mainCell              切换元素的包裹层对象
 * titCell               鼠标的触发元素对象
 ***/










// 获取文件
function getFileName(path) {
	var pos1 = path.lastIndexOf('/');
	var pos2 = path.lastIndexOf('\\');
	var pos = Math.max(pos1, pos2);
	if(pos < 0) {
		return path
	} else {
		return path.substring(pos + 1)
	}
}
$(document).ready(function() {
	$(".codefile").change(function() {
		var str = $(this).val();
		var filename = getFileName(str);
		var filetxt = filename.substring(filename.lastIndexOf(".") + 1);
		$(this).parents("a").prev("input").val(filename)
	})

})

// 优化方式select
$(".div-input").find(".t-way").click(function() {
	var txt = $(this).val()
	
	if(txt == 'Population Based Training') {
		$(".t-box1-all").hide()
		$(".t-box2").show()
		$(".t-fun1").hide()
		$(".t-fun2").show()
		$(".pbt-par").show()
		$(".bys-par").hide()
		if ($(".t-box1").is(':hidden')) {
//			$(".t-box1").find("input").val('')
		} else{
			
		}
		$(".t-fun2").on("click",function(){
		var t2 = $(this).val()
		if(t2 == 'SGD'){
		
			$(this).parents(".model-text").siblings(".t-box2").find(".l-box:odd").show()
		}else if(t2 == 'Adam'){
		
			$(this).parents(".model-text").siblings(".t-box2").find(".l-box:odd").hide()
		}
	})
	} else if(txt == 'Bayesian optimization') {
		$(".t-box2").hide()
		$(".t-box1-all").show()
		$(".t-fun2").hide()
		$(".t-fun1").show()
		$(".pbt-par").hide()
		$(".bys-par").show()
		if ($(".t-box2").is(':hidden')) {
//			$(".t-box2").find("input").val('')
		} else{
			
		}
	}
})



// 超参
if ($(".t-way").val() == 'Bayesian optimization') {
		var tt1 = $('.t-fun1').val();
		if (tt1 == 'GD') {
			for(var i = 0; i<$('.l-box').length; i++){
				$('.l-box').eq(i).find('input').eq(0).val('');
				$('.l-box').eq(i).find('input').eq(1).val('');
				$('.l-box').eq(i).find('input').eq(2).val('');
			}
				$('.t-fun1').parents('.model-text').siblings('.t-box1-all').find('.t-box1').find('.l-box').show()
				$('.t-fun1').parents('.model-text').siblings('.t-box1-all').find('.t-box1').find('.l-box:gt(0)').hide()
				$('#checkone').hide();
			} else if(tt1 == 'RMSProp'){
			for(var i = 0; i<$('.l-box').length; i++){
				$('.l-box').eq(i).find('input').eq(0).val('');
				$('.l-box').eq(i).find('input').eq(1).val('');
				$('.l-box').eq(i).find('input').eq(2).val('');
			}
				$('.t-fun1').parents('.model-text').siblings('.t-box1-all').find('.t-box1').find('.l-box').show()
				// $('.check-none').show();
				$('#checkone').hide();
				$('#checktwo').show()
				$('.t-fun1').parents('.model-text').siblings('.t-box1-all').find('.t-box1').find('.l-box:gt(2)').hide()
			}else if(tt1 == 'Adam'){
			for(var i = 0; i<$('.l-box').length; i++){
				$('.l-box').eq(i).find('input').eq(0).val('');
				$('.l-box').eq(i).find('input').eq(1).val('');
				$('.l-box').eq(i).find('input').eq(2).val('');
			}
				$('.t-fun1').parents('.model-text').siblings('.t-box1-all').find('.t-box1').find('.l-box').show()
				$('#checkone').show();
				$('.t-fun1').parents('.model-text').siblings('.t-box1-all').find('.t-box1').find('.l-box').eq(1).hide()
				$('.t-fun1').parents('.model-text').siblings('.t-box1-all').find('.t-box1').find('.l-box').eq(2).hide()
			}else if(tt1 == 'Momentum'){
			for(var i = 0; i<$('.l-box').length; i++){
				$('.l-box').eq(i).find('input').eq(0).val('');
				$('.l-box').eq(i).find('input').eq(1).val('');
				$('.l-box').eq(i).find('input').eq(2).val('');
			}
				$('.t-fun1').parents('.model-text').siblings('.t-box1-all').find('.t-box1').find('.l-box').show()
				$('#checkone').hide();
				$('#checktwo').hide();
				$('.t-fun1').parents('.model-text').siblings('.t-box1-all').find('.t-box1').find('.l-box:gt(1)').hide()
			}

		$(".t-fun1").on("change",function(){
			var t1 = $(this).val();
			var check_arry = document.getElementsByClassName('check');
			if (t1 == 'GD') {
				for(var i = 0; i<$('.l-box').length; i++){
					$('.l-box').eq(i).find('input').eq(0).val('');
					$('.l-box').eq(i).find('input').eq(1).val('');
					$('.l-box').eq(i).find('input').eq(2).val('');
				}
				for (var j = 0,len = check_arry.length; j<len; j++){
					check_arry[j].checked = false
				}
				$(this).parents('.model-text').siblings('.t-box1-all').find('.t-box1').find('.l-box').show()
				$(this).parents('.model-text').siblings('.t-box1-all').find('.t-box1').find('.l-box:gt(0)').hide()
				$('#checkone').hide();
			} else if(t1 == 'RMSProp'){
				for(var i = 0; i<$('.l-box').length; i++){
					$('.l-box').eq(i).find('input').eq(0).val('');
					$('.l-box').eq(i).find('input').eq(1).val('');
					$('.l-box').eq(i).find('input').eq(2).val('');
				}
				for (var j = 0,len = check_arry.length; j<len; j++){
					check_arry[j].checked = false
				}
				$(this).parents('.model-text').siblings('.t-box1-all').find('.t-box1').find('.l-box').show()
				$('#checkone').hide();
				$('#checktwo').show()
				$(this).parents('.model-text').siblings('.t-box1-all').find('.t-box1').find('.l-box:gt(2)').hide()
			}else if(t1 == 'Adam'){
				for(var i = 0; i<$('.l-box').length; i++){
					$('.l-box').eq(i).find('input').eq(0).val('');
					$('.l-box').eq(i).find('input').eq(1).val('');
					$('.l-box').eq(i).find('input').eq(2).val('');
				}
				for (var j = 0,len = check_arry.length; j<len; j++){
					check_arry[j].checked = false
				}
				$(this).parents('.model-text').siblings('.t-box1-all').find('.t-box1').find('.l-box').show()

				// $('#checkfive').hide();
				// $('#checkfour').hide();
				$(this).parents('.model-text').siblings('.t-box1-all').find('.t-box1').find('.l-box').eq(1).hide()
				$(this).parents('.model-text').siblings('.t-box1-all').find('.t-box1').find('.l-box').eq(2).hide()
				$('#checkone').show();
			}else if(t1 == 'Momentum'){
				for(var i = 0; i<$('.l-box').length; i++){
					$('.l-box').eq(i).find('input').eq(0).val('');
					$('.l-box').eq(i).find('input').eq(1).val('');
					$('.l-box').eq(i).find('input').eq(2).val('');
				}
				for (var j = 0,len = check_arry.length; j<len; j++){
					check_arry[j].checked = false
				}
				$(this).parents('.model-text').siblings('.t-box1-all').find('.t-box1').find('.l-box').show()
				$('#checkone').hide();
				$('#checktwo').hide();
				$(this).parents('.model-text').siblings('.t-box1-all').find('.t-box1').find('.l-box:gt(1)').hide()
			}
		})
	
} 

// 参数值范围提示
$(".bys-par").on("focus","input[type$='text']",function(){
	$(this).parents(".div-input").prev("span").show()
})
$(".bys-par").find("input[type$='text']").blur(function(){
	$(this).parents(".div-input").prev("span").hide()
})
$(".pbt-par").on("focus","input[type$='text']",function(){
	$(this).parents(".div-input").prev("span").show()	
})
$(".pbt-par").find("input[type$='text']").blur(function(){
	$(this).parents(".div-input").prev("span").hide()
})


$(".c-box").on("focus","input[type$='text']",function(){
	console.log('123456')
	$(this).siblings("span").show()
})
$(".c-box").on("blur","input[type$='text'",function () {
	$(this).siblings('span').hide()
})
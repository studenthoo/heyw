//加载进度
// var ww=10;
// setInterval(function(){
// 	ww+=10
// 	$(".length_i_process").animate({
// 		'width':ww+'%'
// 	},1000)
// 	$(".length_i_process").html(ww+'%')
// 	console.log(ww)
// 	if(ww==100){
// 		$('.btn_all li').css('display','block')
// 	}
// },1100)

//按钮
$('.btn_all li').on('click',function(){
	$(this).css({
		'color':'white',
		'background':'#00b5b8'
	}).siblings().css({
		'color':'black',
		'background':'#DFE6EA'
	})
	console.log($(this).text())
	if($(this).text()=='点击展示训练集'){
		$('.lis_train').css('display','block')
		$('.lis_val').css('display','none')
		var url=$('.lis_train_url').text()
		$('.lis_train iframe').attr('src',url)
	}
	else if($(this).text()=='点击展示验证集'){
		$('.lis_train').css('display','none')
		$('.lis_val').css('display','block')
		var url=$('.lis_val_url').text()
		$('.lis_val iframe').attr('src',url)
	}
})

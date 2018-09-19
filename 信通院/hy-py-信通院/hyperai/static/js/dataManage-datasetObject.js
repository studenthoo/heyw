

//加载进度
// var ww=10;
// setInterval(function(){
// 	ww+=10
// 	$(".length_i").animate({
// 		'width':ww+'%'
// 	},1000)
// 	$(".length_i").html(ww+'%')
// 	console.log(ww)
// 	if(ww==100){
// 		$('.btn-toggle li').css('display','block')
// 	}
// },1100)




$(".btn-toggle li").on("click",function(){
	$(this).addClass("putcolor");
	$(this).siblings().removeClass("putcolor");
	$(this).find("a").addClass("li-a");
	$(this).siblings().find("a").removeClass("li-a");
	var txt = $(this).find("a").text()
	if (txt == "点击展示训练集") {
		$(".lis-tview-train").show();
		$(".lis-tview-val").hide();
		var url1=$('.lis_train_url').text()
		$('.iframe_train').attr('src',url1)
	} 
	
	else if(txt == "点击展示验证集"){
		$(".lis-tview-train").hide();
		$(".lis-tview-val").show();
		var url2=$('.lis_val_url').text()
		$('.iframe_val').attr('src',url2)
	}
})

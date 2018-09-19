

//加载进度
// var ww=10;
// setInterval(function(){
// 	ww+=10
// 	$(".length_i_segmentate").animate({
// 		'width':ww+'%'
// 	},1000)
// 	$(".length_i_segmentate").html(ww+'%')
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
	if (txt == "标签训练集") {
		$(".lis-tview-lt").show();
		$(".lis-tview-tt").hide();
		$(".lis-tview-lv").hide();
		$(".lis-tview-tv").hide()
		var url = $(".lis_train_url1").text();
		$("iframe").attr("src",url)
		
	} 
	else if(txt == "特征训练集"){
		$(".lis-tview-lt").hide();
		$(".lis-tview-tt").show();
		$(".lis-tview-lv").hide();
		$(".lis-tview-tv").hide()
		var url = $(".lis_train_url2").text();
		$("iframe").attr("src",url)
	}
	else if(txt == "标签验证集"){
		$(".lis-tview-lt").hide();
		$(".lis-tview-tt").hide();
		$(".lis-tview-lv").show();
		$(".lis-tview-tv").hide()
		var url = $(".lis_val_url2").text();
		$("iframe").attr("src",url)
		
	}else if(txt == "特征验证集"){
		$(".lis-tview-lt").hide();
		$(".lis-tview-tt").hide();
		$(".lis-tview-lv").hide();
		$(".lis-tview-tv").show()
		var url = $(".lis_val_url1").text();
		$("iframe").attr("src",url)
		
	}
})
